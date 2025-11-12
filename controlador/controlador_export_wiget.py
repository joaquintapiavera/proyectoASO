# controlador/controlador_export_widget.py
from PyQt6 import QtWidgets
from ui.ExportWidget import Ui_ExportWidget

class ControladorExportWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ExportWidget()
        self.ui.setupUi(self)
