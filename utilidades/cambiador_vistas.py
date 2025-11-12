# utilidades/cambiador_vistas.py
from typing import Callable, Dict, Optional, Union
from PyQt6 import QtWidgets

WidgetFactory = Callable[[], QtWidgets.QWidget]
WidgetOrFactory = Union[QtWidgets.QWidget, WidgetFactory]

class CambiadorVistas:
    def __init__(self, stacked_widget: QtWidgets.QStackedWidget):
        self.stacked_widget = stacked_widget
        # name -> (factory_or_instance, instance_or_none)
        self._vistas: Dict[str, (WidgetOrFactory, Optional[QtWidgets.QWidget])] = {}

    def agregar_vista(self, nombre: str, widget_or_factory: WidgetOrFactory):
        if nombre in self._vistas:
            raise ValueError(f"Vista '{nombre}' ya registrada")
        instance = widget_or_factory if isinstance(widget_or_factory, QtWidgets.QWidget) else None
        self._vistas[nombre] = (widget_or_factory, instance)
        if instance is not None:
            self.stacked_widget.addWidget(instance)

    def _instanciar_si_es_necesario(self, nombre: str) -> QtWidgets.QWidget:
        if nombre not in self._vistas:
            raise ValueError(f"No existe la vista registrada con nombre '{nombre}'")
        factory_or_instance, instance = self._vistas[nombre]
        if instance is None:
            if not callable(factory_or_instance):
                raise TypeError("Se esperaba una instancia o una callable que cree la instancia")
            instance = factory_or_instance()
            self._vistas[nombre] = (factory_or_instance, instance)
            self.stacked_widget.addWidget(instance)
        return instance

    def mostrar_vista(self, nombre: str):
        widget = self._instanciar_si_es_necesario(nombre)
        self.stacked_widget.setCurrentWidget(widget)

    def quitar_vista(self, nombre: str):
        if nombre not in self._vistas:
            return
        _, instance = self._vistas.pop(nombre)
        if instance is not None:
            self.stacked_widget.removeWidget(instance)
            instance.deleteLater()

    def listar_vistas(self):
        return list(self._vistas.keys())

    registrar_vista = agregar_vista  # alias retrocompatible
