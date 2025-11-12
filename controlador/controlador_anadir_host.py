from PyQt6 import QtWidgets
from ui import anadir_host

class ControladorAddHost(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = anadir_host.Ui_AddHost()
        self.ui.setupUi(self)

        self.ui.buttonBox.accepted.connect(self.aceptar)
        self.ui.buttonBox.rejected.connect(self.rechazar)

    def aceptar(self):
        host = self.ui.le_host.text()
        opciones = {
            "rw": self.ui.rw.isChecked(),
            "ro": self.ui.ro.isChecked(),
            "sync": self.ui.sync.isChecked(),
            "async": self.ui.async_cb.isChecked(),
            "root_squash": self.ui.root_squash.isChecked(),
            "no_root_squash": self.ui.no_root_squash.isChecked(),
            "subtree_check": self.ui.subtree_check.isChecked(),
            "no_subtree_check": self.ui.no_subtree_check.isChecked(),
            "all_squash": self.ui.all_squash.isChecked(),
            "insecure": self.ui.insecure.isChecked(),
            "secure": self.ui.secure.isChecked(),
            "anonuid": self.ui.anonuid.isChecked(),
            "anongid": self.ui.anongid.isChecked(),
        }
        print("Host:", host)
        print("Opciones:", opciones)
        self.accept()

    def rechazar(self):
        self.reject()


