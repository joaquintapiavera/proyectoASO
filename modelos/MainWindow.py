from PyQt6 import QtWidgets
from utilidades.cambiador_vistas import CambiadorVistas
import ui

class MainWidget(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.stacked_widget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.cambiador = CambiadorVistas(self.stacked_widget)

        self.cambiador.mostrar_vista("configuracion")

        self.cambiador.vistas["vista1"].pushButton.clicked.connect(
            lambda: self.cambiador.mostrar_vista("vista2")
        )
        self.cambiador.vistas["vista2"].pushButton.clicked.connect(
            lambda: self.cambiador.mostrar_vista("vista3")
        )
        self.cambiador.vistas["vista3"].pushButton.clicked.connect(
            lambda: self.cambiador.mostrar_vista("vista1")
        )