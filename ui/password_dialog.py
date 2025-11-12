from PyQt6 import QtWidgets, QtCore
import subprocess
import os

try:
    from pam import pam as Pam
except Exception:
    Pam = None

try:
    import pexpect
except Exception:
    pexpect = None

from modelos.session_manager import RootSession

class CommandThread(QtCore.QThread):
    finished_signal = QtCore.pyqtSignal(bool, str, str, str)

    def __init__(self, commands, password=None, parent=None):
        super().__init__(parent)
        self.commands = list(commands)
        self.password = password

    def run(self):
        shell_cmd = " && ".join(self.commands)
        try:
            if os.geteuid() == 0:
                proc = subprocess.run(["sh", "-c", shell_cmd], capture_output=True, text=True, check=False)
                success = proc.returncode == 0
                self.finished_signal.emit(success, proc.stdout or "", proc.stderr or "", "direct-root")
                return
        except AttributeError:
            pass
        try:
            proc = subprocess.run(["pkexec", "sh", "-c", shell_cmd], capture_output=True, text=True, check=False)
            if proc.returncode == 0:
                self.finished_signal.emit(True, proc.stdout or "", proc.stderr or "", "pkexec")
                return
            pkexec_err = (proc.returncode, proc.stdout, proc.stderr)
        except FileNotFoundError:
            pkexec_err = ("missing", "", "pkexec not found")
        if self.password:
            try:
                proc = subprocess.run(["sudo", "-S", "sh", "-c", shell_cmd], input=self.password + "\n", capture_output=True, text=True, check=False)
                success = proc.returncode == 0
                self.password = None
                self.finished_signal.emit(success, proc.stdout or "", proc.stderr or "", "sudo")
                return
            except Exception as e:
                self.finished_signal.emit(False, "", f"sandboxed sudo error: {e}", "sudo")
                return
        msg = "No se pudo ejecutar como root: pkexec falló o no está disponible."
        if pkexec_err:
            msg += f" Detalle pkexec: {pkexec_err}"
        self.finished_signal.emit(False, "", msg, "none")


class PasswordDialog(QtWidgets.QDialog):
    def __init__(self, command: str = "/sbin/yast2 nfs_server", parent=None, service_name: str = "mi_app_nfs"):
        super().__init__(parent)
        self.setWindowTitle("Ejecutar como root")
        self.setModal(True)
        self.resize(640, 240)
        self.command = command
        self.service_name = service_name
        self.password = None
        self.ignore = False
        v = QtWidgets.QVBoxLayout(self)
        lbl_info = QtWidgets.QLabel(
            "La acción que solicitaste necesita privilegios de root.\n"
            "Introduce la contraseña de root o pulsa Ignorar para continuar con los privilegios actuales.\n\n"
            "Nota: la mejor práctica es usar polkit/pkexec (la app no necesita manejar la contraseña).\n"
            "Si introduces una contraseña, esta se verificará contra PAM (o usando su)."
        )
        lbl_info.setWordWrap(True)
        v.addWidget(lbl_info)
        cmd_display = self.command
        lbl_cmd = QtWidgets.QLabel(f"Comando por defecto: <code>{cmd_display}</code>")
        lbl_cmd.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        v.addWidget(lbl_cmd)
        form = QtWidgets.QFormLayout()
        self.password_edit = QtWidgets.QLineEdit()
        self.password_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        form.addRow("Contraseña (root):", self.password_edit)
        self.chk_remember = QtWidgets.QCheckBox("Recordar contraseña (no recomendado)")
        form.addRow("", self.chk_remember)
        v.addLayout(form)
        buttons = QtWidgets.QDialogButtonBox()
        ok_btn = buttons.addButton(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        ignore_btn = buttons.addButton(QtWidgets.QDialogButtonBox.StandardButton.Ignore)
        cancel_btn = buttons.addButton(QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        ok_btn.setText("OK")
        ignore_btn.setText("Ignorar")
        cancel_btn.setText("Cancelar")
        buttons.accepted.connect(self._on_ok)
        buttons.rejected.connect(self._on_cancel)
        ignore_btn.clicked.connect(self._on_ignore)
        v.addWidget(buttons)
        self._try_load_saved_password()
        self._cmd_thread = None

    def _verify_root_password(self, password: str) -> (bool, str):
        if not password:
            return False, "Contraseña vacía."
        try:
            if os.geteuid() == 0:
                return True, ""
        except AttributeError:
            pass
        if Pam is not None:
            try:
                p = Pam()
                ok = p.authenticate("root", password)
                if ok:
                    return True, ""
                else:
                    return False, "Autenticación PAM fallida (contraseña incorrecta)."
            except Exception as e:
                pam_err = f"PAM error: {e}"
        else:
            pam_err = "módulo pam no disponible."
        if pexpect is None:
            return False, f"No se pudo autenticar: {pam_err} y pexpect no está disponible para fallback."
        try:
            child = pexpect.spawn('su -c "id -u" root', encoding="utf-8", timeout=12)
            patterns = [r"[Pp]assword[: ]*$", r"[Cc]ontrase[nn]a[: ]*$", r"[Pp]assword for", r":\s*$", pexpect.EOF, pexpect.TIMEOUT]
            idx = child.expect(patterns, timeout=8)
            if idx in (0, 1, 2, 3):
                child.sendline(password)
                idx2 = child.expect([r"\b0\b", pexpect.EOF, pexpect.TIMEOUT], timeout=6)
                output = child.before or ""
                exit_status = getattr(child, 'exitstatus', None)
                try:
                    child.close(force=True)
                except Exception:
                    pass
                outstr = str(output).strip() if output is not None else ""
                if idx2 == 0 or exit_status == 0 or outstr == "0" or "0" in outstr.split():
                    return True, ""
                return False, "Contraseña incorrecta o UID distinto de 0."
            elif idx == 4:
                output = child.before or ""
                try:
                    child.close(force=True)
                except Exception:
                    pass
                outstr = str(output).strip() if output is not None else ""
                if outstr == "0" or "0" in outstr.split():
                    return True, ""
                return False, "El comando su terminó sin pedir contraseña ni UID 0."
            else:
                try:
                    child.close(force=True)
                except Exception:
                    pass
                return False, "Timeout usando su para verificar la contraseña."
        except Exception as e:
            return False, f"Error en fallback con su/pexpect: {e}"

    def _try_load_saved_password(self):
        try:
            import keyring
            pw = keyring.get_password(self.service_name, "root")
            if pw:
                self.password_edit.setText(pw)
                self.chk_remember.setChecked(True)
                return
        except Exception:
            pass
        settings = QtCore.QSettings("mi_org", self.service_name)
        saved = settings.value("remember_password", False, type=bool)
        if saved:
            pw = settings.value("password", "")
            if pw:
                self.password_edit.setText(pw)
                self.chk_remember.setChecked(True)

    def _on_ok(self):
        pw = self.password_edit.text()
        if not pw:
            ans = QtWidgets.QMessageBox.question(self, "Continuar sin contraseña?",
                                                 "No se ha introducido ninguna contraseña. ¿Deseas continuar sin verificar como root?",
                                                 QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            if ans == QtWidgets.QMessageBox.StandardButton.Yes:
                if not self.chk_remember.isChecked():
                    self._delete_saved_password()
                self.password = None
                self.accept()
                return
            else:
                return
        ok, msg = self._verify_root_password(pw)
        if not ok:
            QtWidgets.QMessageBox.critical(self, "Autenticación fallida", f"No se pudo verificar la contraseña de root:\n{msg}")
            return
        self.password = pw
        session = RootSession.instance()
        session.set_authenticated(password=pw)
        if self.chk_remember.isChecked() and self.password:
            self._save_password(self.password)
        elif not self.chk_remember.isChecked():
            self._delete_saved_password()
        try:
            self.password_edit.clear()
        except Exception:
            pass
        self.accept()

    def _on_ignore(self):
        self.ignore = True
        self.accept()

    def _on_cancel(self):
        self.reject()

    def _save_password(self, password: str):
        try:
            import keyring
            keyring.set_password(self.service_name, "root", password)
            return
        except Exception:
            pass
        settings = QtCore.QSettings("mi_org", self.service_name)
        settings.setValue("remember_password", True)
        settings.setValue("password", password)

    def _delete_saved_password(self):
        try:
            import keyring
            keyring.delete_password(self.service_name, "root")
            return
        except Exception:
            pass
        settings = QtCore.QSettings("mi_org", self.service_name)
        settings.setValue("remember_password", False)
        settings.remove("password")

    def run_as_root(self, commands):
        try:
            if os.geteuid() == 0:
                out, err, code = self._run_without_privileges(commands)
                self._show_result_dialog(success=(code == 0), stdout=out, stderr=err, method="direct-root")
                return
        except AttributeError:
            pass
        pw = self.password
        self._cmd_thread = CommandThread(commands, password=pw, parent=self)
        self._cmd_thread.finished_signal.connect(self._on_command_finished)
        self._progress = QtWidgets.QProgressDialog("Ejecutando comandos como root...", "Cancelar", 0, 0, self)
        self._progress.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        try:
            self._progress.setCancelButton(None)
        except Exception:
            pass
        self._progress.show()
        self._cmd_thread.start()

    def _run_without_privileges(self, commands):
        shell_cmd = " && ".join(commands)
        try:
            proc = subprocess.run(["sh", "-c", shell_cmd], capture_output=True, text=True, check=False)
            return proc.stdout or "", proc.stderr or "", proc.returncode
        except Exception as e:
            return "", str(e), 1

    def _on_command_finished(self, success, stdout, stderr, method):
        try:
            self._progress.close()
        except Exception:
            pass
        self._show_result_dialog(success, stdout, stderr, method)

    def _show_result_dialog(self, success: bool, stdout: str, stderr: str, method: str):
        title = "Comando ejecutado" if success else "Error al ejecutar comandos"
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle(title)
        dlg.resize(800, 500)
        layout = QtWidgets.QVBoxLayout(dlg)
        info = QtWidgets.QLabel(f"Método usado: <b>{method}</b>")
        layout.addWidget(info)
        tabs = QtWidgets.QTabWidget()
        txt_out = QtWidgets.QPlainTextEdit()
        txt_out.setReadOnly(True)
        txt_out.setPlainText(stdout or "<sin salida>")
        tabs.addTab(txt_out, "Salida STDOUT")
        txt_err = QtWidgets.QPlainTextEdit()
        txt_err.setReadOnly(True)
        txt_err.setPlainText(stderr or "<sin error>")
        tabs.addTab(txt_err, "Salida STDERR")
        layout.addWidget(tabs)
        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        btns.accepted.connect(dlg.accept)
        layout.addWidget(btns)
        dlg.exec()
