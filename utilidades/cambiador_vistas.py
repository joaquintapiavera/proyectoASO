from PyQt6 import QtWidgets


class CambiadorVistas:
    def __init__(self, stacked_widget: QtWidgets.QStackedWidget):
        self.stacked_widget = stacked_widget
        self.vistas = {}

    def agregar_vista(self, nombre: str, widget: QtWidgets.QWidget):
        self.vistas[nombre] = widget
        self.stacked_widget.addWidget(widget)

    def mostrar_vista(self, nombre: str):
        if nombre in self.vistas:
            self.stacked_widget.setCurrentWidget(self.vistas[nombre])
        else:
            raise ValueError(f"No existe la vista registrada con nombre '{nombre}'")
