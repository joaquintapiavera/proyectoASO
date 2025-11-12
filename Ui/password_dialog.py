# ui/password_dialog.py
from PyQt6 import QtWidgets, QtCore

class PasswordDialog(QtWidgets.QDialog):
    """
    Diálogo en español para pedir la contraseña de root antes de ejecutar un comando.
    Botones: OK / Ignorar / Cancelar
    Devuelve:
      - accepted + dialog.password (string) si OK
      - accepted + dialog.ignore == True si Ignorar
      - rejected si Cancelar
    """
    def __init__(self, command: str = "/sbin/yast2 nfs_server", parent=None, service_name: str = "mi_app_nfs"):
        super().__init__(parent)
        self.setWindowTitle("Ejecutar como root")
        self.setModal(True)
        self.resize(520, 180)

        self.command = command
        self.service_name = service_name  # usado para keyring/QSettings
        self.password = None
        self.ignore = False

        # Layout principal
        v = QtWidgets.QVBoxLayout(self)

        # Texto explicativo
        lbl_info = QtWidgets.QLabel(
            "La acción que solicitaste necesita privilegios de root.\n"
            "Introduce la contraseña de root o pulsa Ignorar para continuar con los privilegios actuales."
        )
        lbl_info.setWordWrap(True)
        v.addWidget(lbl_info)

        # Comando a ejecutar (monoespaciado)
        lbl_cmd = QtWidgets.QLabel(f"Comando: <code>{QtCore.Qt.escape(self.command) if hasattr(QtCore.Qt,'escape') else self.command}</code>")
        lbl_cmd.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        v.addWidget(lbl_cmd)

        # Campo contraseña
        form = QtWidgets.QFormLayout()
        self.password_edit = QtWidgets.QLineEdit()
        self.password_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        form.addRow("Contraseña:", self.password_edit)

        # Recordar contraseña
        self.chk_remember = QtWidgets.QCheckBox("Recordar contraseña")
        form.addRow("", self.chk_remember)

        v.addLayout(form)

        # Botones: OK / Ignorar / Cancelar
        buttons = QtWidgets.QDialogButtonBox()
        ok_btn = buttons.addButton(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        ignore_btn = buttons.addButton(QtWidgets.QDialogButtonBox.StandardButton.Ignore)
        cancel_btn = buttons.addButton(QtWidgets.QDialogButtonBox.StandardButton.Cancel)

        ok_btn.setText("OK")
        ignore_btn.setText("Ignorar")
        cancel_btn.setText("Cancelar")

        buttons.accepted.connect(self._on_ok)     # triggered by OK
        buttons.rejected.connect(self._on_cancel)  # triggered by Cancel
        # connect ignore explicitly
        ignore_btn.clicked.connect(self._on_ignore)

        v.addWidget(buttons)

        # Try to prefill remembered password (keyring preferred)
        self._try_load_saved_password()

    # internal: try to load saved password (keyring first, fallback to QSettings)
    def _try_load_saved_password(self):
        try:
            import keyring
            pw = keyring.get_password(self.service_name, "root")
            if pw:
                self.password_edit.setText(pw)
                self.chk_remember.setChecked(True)
        except Exception:
            # fallback to QSettings (insecure; demo only)
            settings = QtCore.QSettings("mi_org", self.service_name)
            saved = settings.value("remember_password", False, type=bool)
            if saved:
                pw = settings.value("password", "")
                if pw:
                    self.password_edit.setText(pw)
                    self.chk_remember.setChecked(True)

    def _on_ok(self):
        self.password = self.password_edit.text()
        # guardar si pidió recordar
        if self.chk_remember.isChecked() and self.password:
            self._save_password(self.password)
        elif not self.chk_remember.isChecked():
            # eliminar credencial previa si existiera
            self._delete_saved_password()
        self.accept()

    def _on_ignore(self):
        self.ignore = True
        self.accept()

    def _on_cancel(self):
        self.reject()

    def _save_password(self, password: str):
        # prefer keyring; si no está, usar QSettings (inseguro)
        try:
            import keyring
            keyring.set_password(self.service_name, "root", password)
        except Exception:
            settings = QtCore.QSettings("mi_org", self.service_name)
            settings.setValue("remember_password", True)
            settings.setValue("password", password)  # NOTA: inseguro en producción

    def _delete_saved_password(self):
        try:
            import keyring
            keyring.delete_password(self.service_name, "root")
        except Exception:
            settings = QtCore.QSettings("mi_org", self.service_name)
            settings.setValue("remember_password", False)
            settings.remove("password")
