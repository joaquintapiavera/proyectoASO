# ui/dialogo_anadir_host.py
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMessageBox
try:
    # asumo que el pyuic generó ui/anadir_host.py con la clase Ui_AddHost
    from ui.anadir_host import Ui_AddHost
except Exception:
    from anadir_host import Ui_AddHost


class DialogoAddHost(QtWidgets.QDialog):
    """
    Diálogo para añadir/editar un host.
    - valida que el campo host no esté vacío.
    - obtener_datos() devuelve (host: str, opciones: str) donde opciones es "rw,sync,..."
    - cargar_desde(host, opciones_str) precarga valores para edición.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_AddHost()
        self.ui.setupUi(self)

    def accept(self) -> None:
        host = self.ui.le_host.text().strip()
        if not host:
            QMessageBox.warning(self, "Host vacío", "Introduce un host o IP antes de aceptar.")
            return
        super().accept()

    def obtener_datos(self):
        """Devuelve (host, opciones_coma_sep)"""
        host = self.ui.le_host.text().strip()
        opts = []
        # checks básicos (mismo nombre que en tu ui)
        if self.ui.rw.isChecked():
            opts.append("rw")
        if self.ui.ro.isChecked():
            opts.append("ro")
        if self.ui.sync.isChecked():
            opts.append("sync")
        if self.ui.async_.isChecked():
            opts.append("async")
        if self.ui.root_squash.isChecked():
            opts.append("root_squash")
        if self.ui.no_root_squash.isChecked():
            opts.append("no_root_squash")
        if self.ui.all_squash.isChecked():
            opts.append("all_squash")
        if self.ui.subtree_check.isChecked():
            opts.append("subtree_check")
        if self.ui.no_subtree_check.isChecked():
            opts.append("no_subtree_check")
        if self.ui.secure.isChecked():
            opts.append("secure")
        if self.ui.insecure.isChecked():
            opts.append("insecure")
        if self.ui.anonuid.isChecked():
            opts.append("anonuid")
        if self.ui.anongid.isChecked():
            opts.append("anongid")

        return host, ",".join(opts)

    def cargar_desde(self, host: str, opciones: str):
        """Precarga el diálogo desde valores existentes (útil para editar)."""
        self.ui.le_host.setText(host or "")
        optset = set(o.strip() for o in (opciones or "").split(",") if o.strip())

        # asignar checks según optset
        self.ui.rw.setChecked("rw" in optset)
        self.ui.ro.setChecked("ro" in optset)
        self.ui.sync.setChecked("sync" in optset)
        self.ui.async_.setChecked("async" in optset)
        self.ui.root_squash.setChecked("root_squash" in optset)
        self.ui.no_root_squash.setChecked("no_root_squash" in optset)
        self.ui.all_squash.setChecked("all_squash" in optset)
        self.ui.subtree_check.setChecked("subtree_check" in optset)
        self.ui.no_subtree_check.setChecked("no_subtree_check" in optset)
        self.ui.secure.setChecked("secure" in optset)
        self.ui.insecure.setChecked("insecure" in optset)
        self.ui.anonuid.setChecked("anonuid" in optset)
        self.ui.anongid.setChecked("anongid" in optset)
