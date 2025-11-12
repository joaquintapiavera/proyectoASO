from PyQt6 import QtWidgets, QtCore
from ui.configuracion import Ui_MainWindow
import subprocess
import shlex
import os
from modelos.session_manager import RootSession

class ModeloConfiguracion:
    def __init__(self):
        self.iniciar_nfs = False
        self.nfsv4_habilitado = False
        self.gss_security = False
        self.dominio_nfsv4 = ""

    def set_iniciar_nfs(self, valor: bool):
        self.iniciar_nfs = bool(valor)

    def set_nfsv4(self, valor: bool):
        self.nfsv4_habilitado = bool(valor)

    def set_gss(self, valor: bool):
        self.gss_security = bool(valor)

    def set_dominio(self, dominio: str):
        self.dominio_nfsv4 = dominio.strip()

    def validar_configuracion(self):
        errores = []
        if self.nfsv4_habilitado and not self.dominio_nfsv4:
            errores.append("Debe ingresar un dominio NFSv4 si está habilitado NFSv4")
        return errores

class CommandThread(QtCore.QThread):
    finished = QtCore.pyqtSignal(bool, str, str)

    def __init__(self, shell_script: str, run_direct_if_root: bool = True, parent=None):
        super().__init__(parent)
        self.shell_script = shell_script
        self.run_direct_if_root = run_direct_if_root
        self.session = RootSession.instance()

    def run(self):
        try:
            if self.run_direct_if_root and hasattr(os, "geteuid") and os.geteuid() == 0:
                proc = subprocess.run(["sh", "-c", self.shell_script], capture_output=True, text=True, check=False)
                success = proc.returncode == 0
                self.finished.emit(success, proc.stdout or "", proc.stderr or "")
                return
        except Exception:
            pass
        try:
            if self.session.authenticated and self.session.password:
                proc = subprocess.run(["sudo", "-S", "sh", "-c", self.shell_script], input=self.session.password + "\n", capture_output=True, text=True, check=False)
                success = proc.returncode == 0
                stderr = proc.stderr or ""
                if not success:
                    low = stderr.lower() if isinstance(stderr, str) else ""
                    if "incorrect" in low or "authentication" in low or "denied" in low:
                        self.session.clear()
                else:
                    self.session.set_authenticated(password=self.session.password)
                self.finished.emit(success, proc.stdout or "", proc.stderr or "")
                return
            proc = subprocess.run(["pkexec", "sh", "-c", self.shell_script], capture_output=True, text=True, check=False)
            success = proc.returncode == 0
            if success:
                self.session.set_authenticated()
            self.finished.emit(success, proc.stdout or "", proc.stderr or "")
            return
        except FileNotFoundError:
            try:
                proc = subprocess.run(["sh", "-c", self.shell_script], capture_output=True, text=True, check=False)
                success = proc.returncode == 0
                self.finished.emit(success, proc.stdout or "", proc.stderr or "")
                return
            except Exception as e:
                self.finished.emit(False, "", f"Execution error: {e}")
                return
        except Exception as e:
            self.finished.emit(False, "", f"Unexpected error: {e}")
            return

class LoadingDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, message="Ejecutando, por favor espera..."):
        super().__init__(parent)
        self.setWindowTitle("")
        self.setModal(True)
        flags = self.windowFlags()
        self.setWindowFlags(flags & ~QtCore.Qt.WindowType.WindowCloseButtonHint & ~QtCore.Qt.WindowType.WindowMinimizeButtonHint)
        self.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.resize(360, 90)
        layout = QtWidgets.QVBoxLayout(self)
        lbl = QtWidgets.QLabel(message, parent=self)
        lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)
        self.setLayout(layout)

class ControladorConfiguracion(QtWidgets.QMainWindow):
    def __init__(self, cambiador=None, parent=None):
        super().__init__(parent)
        self.cambiador = cambiador
        self.modelo = ModeloConfiguracion()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.radioButton.toggled.connect(self.on_iniciar_changed)
        self.ui.radioButton_2.toggled.connect(self.on_no_iniciar_changed)
        self.ui.checkBox.toggled.connect(self.on_nfsv4_toggled)
        self.ui.checkBox_2.toggled.connect(self.on_gss_toggled)
        self.ui.lineEdit.textChanged.connect(self.on_dominio_changed)
        self.ui.pushButton.clicked.connect(self.on_ayuda)
        self.ui.pushButton_2.clicked.connect(self.on_cancelar)
        self.ui.pushButton_3.clicked.connect(self.on_atras)
        self.ui.pushButton_4.clicked.connect(self.on_siguiente)
        self._cmd_thread = None
        self._loading = None
        self._load_model_to_ui()

    def _load_model_to_ui(self):
        self.ui.radioButton.setChecked(self.modelo.iniciar_nfs)
        self.ui.radioButton_2.setChecked(not self.modelo.iniciar_nfs)
        self.ui.checkBox.setChecked(self.modelo.nfsv4_habilitado)
        self.ui.checkBox_2.setChecked(self.modelo.gss_security)
        self.ui.lineEdit.setText(self.modelo.dominio_nfsv4)

    def on_iniciar_changed(self, checked):
        if checked:
            self.modelo.set_iniciar_nfs(True)
            self.ui.radioButton_2.setChecked(False)

    def on_no_iniciar_changed(self, checked):
        if checked:
            self.modelo.set_iniciar_nfs(False)
            self.ui.radioButton.setChecked(False)

    def on_nfsv4_toggled(self, checked):
        self.modelo.set_nfsv4(checked)

    def on_gss_toggled(self, checked):
        self.modelo.set_gss(checked)

    def on_dominio_changed(self, text):
        self.modelo.set_dominio(text)

    def on_ayuda(self):
        QtWidgets.QMessageBox.information(self, "Ayuda", "Configura el servicio NFS. Marca 'Iniciar' para habilitar el servicio y 'Habilitar NFSv4' si deseas NFSv4. 'Siguiente' aplicará los cambios.")

    def on_cancelar(self):
        self.close()

    def on_atras(self):
        if self.cambiador:
            try:
                self.cambiador.mostrar_vista("menu")
                return
            except Exception:
                pass
        self.close()

    def _find_nfs_unit(self):
        candidates = ["nfs-server.service", "nfsserver.service", "nfs-kernel-server.service"]
        for u in candidates:
            try:
                r = subprocess.run(["systemctl", "list-unit-files", u], capture_output=True, text=True)
                out = (r.stdout or "") + (r.stderr or "")
                if u in out:
                    return u
            except Exception:
                pass
        return None

    def _is_service_active(self, unit_name):
        if not unit_name:
            return False
        try:
            r = subprocess.run(["systemctl", "is-active", "--quiet", unit_name])
            return r.returncode == 0
        except Exception:
            return False

    def _build_start_script(self, unit_name, dominio=None):
        lines = []
        lines.append("zypper -n in -y nfs-kernel-server yast2-nfs-server || true")
        if unit_name:
            uq = shlex.quote(unit_name)
            lines.append(f"systemctl enable --now {uq} || true")
        else:
            lines.append("systemctl enable --now rpcbind || true")
            lines.append("systemctl enable --now nfs-kernel-server || true")
        lines.append("if systemctl is-active --quiet firewalld; then firewall-cmd --permanent --add-service=nfs || true; firewall-cmd --reload || true; fi")
        if dominio:
            safe_dom = shlex.quote(dominio)
            lines.append(
                f"if [ -f /etc/idmapd.conf ]; then "
                f"  if grep -q '^Domain' /etc/idmapd.conf; then sed -i \"s/^Domain.*/Domain = {safe_dom}/\" /etc/idmapd.conf || true; "
                f"  else awk '/^\\[General\\]/ {{print; print \"Domain = {safe_dom}\"; skip=1; next}} !skip {{print}}' /etc/idmapd.conf > /tmp/idmapd.conf && mv /tmp/idmapd.conf /etc/idmapd.conf || true; fi "
                f"else printf \"[General]\\nDomain = {safe_dom}\\n\" > /etc/idmapd.conf || true; fi"
            )
            if unit_name:
                lines.append(f"systemctl restart {shlex.quote(unit_name)} || true")
            else:
                lines.append("systemctl restart nfs-kernel-server || true")
        return " && ".join(lines)

    def _build_stop_script(self, unit_name):
        lines = []
        if unit_name:
            lines.append(f"systemctl disable --now {shlex.quote(unit_name)} || true")
        else:
            lines.append("systemctl disable --now nfs-kernel-server || true")
            lines.append("systemctl disable --now rpcbind || true")
        lines.append("if systemctl is-active --quiet firewalld; then firewall-cmd --permanent --remove-service=nfs || true; firewall-cmd --reload || true; fi")
        return " && ".join(lines)

    def on_siguiente(self):
        errores = self.modelo.validar_configuracion()
        if errores:
            QtWidgets.QMessageBox.warning(self, "Configuración inválida", "\n".join(errores))
            return
        unit = self._find_nfs_unit()
        if self.modelo.iniciar_nfs:
            script = self._build_start_script(unit, dominio=self.modelo.dominio_nfsv4 if self.modelo.nfsv4_habilitado else None)
            message = "Aplicando configuración: instalando y habilitando NFS..."
            proceed_after_success = True
        else:
            script = self._build_stop_script(unit)
            message = "Deteniendo y deshabilitando NFS..."
            proceed_after_success = False
        self._loading = LoadingDialog(self, message=message)
        self._loading.show()
        self._set_enabled_ui(False)
        self._cmd_thread = CommandThread(script, run_direct_if_root=True, parent=self)
        self._cmd_thread.finished.connect(lambda success, out, err: self._on_command_finished(success, out, err, proceed_after_success, unit))
        self._cmd_thread.start()

    def _set_enabled_ui(self, enabled: bool):
        widgets = [
            self.ui.radioButton, self.ui.radioButton_2,
            self.ui.checkBox, self.ui.checkBox_2,
            self.ui.lineEdit,
            self.ui.pushButton, self.ui.pushButton_2, self.ui.pushButton_3, self.ui.pushButton_4
        ]
        for w in widgets:
            try:
                w.setEnabled(enabled)
            except Exception:
                pass

    def _on_command_finished(self, success: bool, stdout: str, stderr: str, proceed_after_success: bool, unit_name):
        try:
            if self._loading:
                self._loading.close()
        except Exception:
            pass
        self._set_enabled_ui(True)
        actual_active = False
        if self.modelo.iniciar_nfs:
            unit = unit_name or self._find_nfs_unit()
            actual_active = self._is_service_active(unit)
            if not actual_active:
                unit2 = self._find_nfs_unit()
                actual_active = self._is_service_active(unit2)
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Resultado de la operación")
        dlg.resize(800, 500)
        layout = QtWidgets.QVBoxLayout(dlg)
        status_lbl = QtWidgets.QLabel("Éxito" if success else "Error durante la ejecución")
        layout.addWidget(status_lbl)
        tabs = QtWidgets.QTabWidget()
        txt_out = QtWidgets.QPlainTextEdit()
        txt_out.setReadOnly(True)
        txt_out.setPlainText(stdout or "<sin salida>")
        tabs.addTab(txt_out, "STDOUT")
        txt_err = QtWidgets.QPlainTextEdit()
        txt_err.setReadOnly(True)
        txt_err.setPlainText(stderr or "<sin error>")
        tabs.addTab(txt_err, "STDERR")
        layout.addWidget(tabs)
        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        btns.accepted.connect(dlg.accept)
        layout.addWidget(btns)
        dlg.exec()
        if self.modelo.iniciar_nfs:
            if success and actual_active:
                if self.cambiador:
                    try:
                        self.cambiador.mostrar_vista("export")
                        return
                    except Exception:
                        pass
                QtWidgets.QMessageBox.information(self, "Hecho", "NFS habilitado y en ejecución. Puedes continuar.")
                return
            else:
                QtWidgets.QMessageBox.critical(self, "Falló", "No se pudo dejar NFS activo. Revisa la salida y corrige antes de continuar.")
                return
        else:
            QtWidgets.QMessageBox.information(self, "NFS deshabilitado", "NFS fue detenido/deshabilitado. No se puede avanzar porque NFS no está activo.")
            return
