# controlador/controlador_configuracion.py
from PyQt6 import QtWidgets
from ui.configuracion import Ui_MainWindow  # asegúrate de que este archivo exista

class ControladorConfiguracion(QtWidgets.QMainWindow):
    """
    Controlador que envuelve la UI 'configuracion' generada por pyuic6.
    Hereda de QMainWindow porque la UI llama a setCentralWidget().
    """
    def __init__(self, cambiador=None, parent=None):
        super().__init__(parent)
        self.cambiador = cambiador
        self.ui = Ui_MainWindow()
        # setupUi espera un QMainWindow; pasamos self (que ahora lo es)
        self.ui.setupUi(self)

        # Conectar botones (nombres según tu ui)
        # pushButton_4 = "Siguiente", pushButton_3 = "Atrás"
        self.ui.pushButton_4.clicked.connect(self.on_siguiente)
        self.ui.pushButton_3.clicked.connect(self.on_atras)

    def on_siguiente(self):
        print("➡️ Siguiente pulsado (ir a 'export')")
        if self.cambiador:
            try:
                self.cambiador.mostrar_vista("export")
                return
            except Exception as e:
                print("Error mostrando 'export':", e)
        print("No hay cambiador o no se pudo navegar a 'export'")

    def on_atras(self):
        print("⬅️ Atrás pulsado")
        if self.cambiador:
            try:
                # ajusta a la vista que quieras mostrar al pulsar 'Atrás'
                self.cambiador.mostrar_vista("menu")
                return
            except Exception:
                pass
        # fallback: cerrar la ventana
        self.close()
