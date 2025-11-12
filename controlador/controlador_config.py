from PyQt6 import QtWidgets

from controlador.controlador_export_wiget import ControladorExportWidget
from ui.configuracion import Ui_MainWindow

class ControladorConfiguracion(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.ayuda)
        self.ui.pushButton_2.clicked.connect(self.cancelar)
        self.ui.pushButton_3.clicked.connect(self.atras)
        self.ui.pushButton_4.clicked.connect(self.siguiente)

        self.ui.radioButton.toggled.connect(self.estado_nfs)
        self.ui.radioButton_2.toggled.connect(self.estado_nfs)

        self.ui.checkBox.toggled.connect(self.nfsv4_habilitado)
        self.ui.checkBox_2.toggled.connect(self.gss_habilitado)

    def ayuda(self):
        QtWidgets.QMessageBox.information(self, "Ayuda", "Aquí va la ayuda de NFS Server")

    def cancelar(self):
        self.close()

    def atras(self):
        print("Botón Atrás presionado")

    def siguiente(self):
        # Crear instancia del widget
        self.ventana_siguiente = ControladorExportWidget()
        self.ventana_siguiente.show()

        # Cerrar o esconder la ventana actual
        self.close()  # o self.hide() si quieres mantenerla en memoria

    def estado_nfs(self):
        if self.ui.radioButton.isChecked():
            print("NFS Server: Iniciar")
        elif self.ui.radioButton_2.isChecked():
            print("NFS Server: No iniciar")

    def nfsv4_habilitado(self):
        print("Habilitar NFSv4:", self.ui.checkBox.isChecked())

    def gss_habilitado(self):
        print("Enable GSS Security:", self.ui.checkBox_2.isChecked())
