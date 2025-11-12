# controlador/controlador_export_widget.py
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import pyqtSignal
from ui.ExportWidget import Ui_ExportWidget
from ui.dialogo_anadir_host import DialogoAddHost

# Importa el diálogo de selección de directorio (colócalo en ui/dialogo_directorio.py)
try:
    from ui.dialogo_directorio import DialogoDirectorio
except Exception:
    # Si no lo pusiste en /ui, prueba importar desde la raíz (ajusta si hace falta)
    from ui.dialogo_directorio import DialogoDirectorio


class ControladorExportWidget(QtWidgets.QWidget):
    """
    Controlador para ExportWidget.
    - Señal `volver_a_menu` emitida cuando el usuario pulsa "Volver".
    - Puede recibir opcionalmente un `cambiador` (tu CambiadorVistas) para hacer el cambio de vista directamente.
    """
    volver_a_menu = pyqtSignal()

    def __init__(self, cambiador=None, parent=None):
        super().__init__(parent)
        self.cambiador = cambiador  # opcional, puede ser None
        self.ui = Ui_ExportWidget()
        self.ui.setupUi(self)

        # preparar tabla (columnas)
        self.ui.tableHost.setColumnCount(2)
        self.ui.tableHost.setHorizontalHeaderLabels(["Host", "Opciones"])
        self.ui.tableHost.horizontalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeMode.Stretch
        )
        self.ui.tableHost.horizontalHeader().setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents
        )

        # Conexiones botones
        # NOTA: los nombres se basan en tu ui (AniadirDirectorio, Editar, Eliminar...)
        self.ui.AniadirDirectorio.clicked.connect(self.on_aniadir_directorio)
        self.ui.Editar.clicked.connect(self.on_editar_directorio)
        self.ui.Eliminar.clicked.connect(self.on_eliminar_directorio)

        self.ui.AniadirHost.clicked.connect(self.on_aniadir_host)
        self.ui.EditarHost.clicked.connect(self.on_editar_host)
        self.ui.EliminarHost.clicked.connect(self.on_eliminar_host)

        self.ui.Cancelar.clicked.connect(self.on_cancelar)
        self.ui.Finalizar.clicked.connect(self.on_finalizar)

        # botón Volver (en tu UI el atributo se llama pushButton)
        # si en tu UI el botón tiene otro nombre, ajústalo aquí
        self.ui.pushButton.clicked.connect(self.on_volver)

        self.ui.listaDirectorios.currentItemChanged.connect(self.on_directorio_seleccionado)

        self._cargar_ejemplo()

    # --- directorios (QListWidget) ---
    def on_aniadir_directorio(self):
        """
        Abrir diálogo para seleccionar un directorio (texto + botón Examinar).
        Si el usuario acepta con un directorio válido, se añade a la lista.
        """
        dlg = DialogoDirectorio(parent=self)
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            ruta = dlg.obtener_directorio()
            if ruta:
                self.ui.listaDirectorios.addItem(ruta)
                print(f"📁 Directorio añadido: {ruta}")
            else:
                print("📁 Diálogo aceptado pero sin ruta (no se añadió).")
        else:
            print("📁 Operación de añadir directorio cancelada por el usuario.")

    def on_editar_directorio(self):
        current = self.ui.listaDirectorios.currentItem()
        if current:
            print(f"✏️ Editar Directorio (actual: {current.text()})")
            # Abrir el diálogo con la ruta actual para poder modificarla
            dlg = DialogoDirectorio(parent=self)
            dlg.lineEdit.setText(current.text())
            if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                nueva = dlg.obtener_directorio()
                if nueva:
                    current.setText(nueva)
                    print(f"  -> Nuevo texto: {current.text()}")
                else:
                    print("  -> Diálogo aceptado pero sin ruta")
            else:
                print("  -> Edición cancelada")
        else:
            print("✏️ Editar Directorio pulsado pero no hay selección")

    def on_eliminar_directorio(self):
        current_row = self.ui.listaDirectorios.currentRow()
        if current_row >= 0:
            # takeItem devuelve el QListWidgetItem y lo quita del widget (seguro)
            item = self.ui.listaDirectorios.takeItem(current_row)
            if item:
                text = item.text()
                print(f"🗑️ Eliminar Directorio -> eliminado: {text}")
                del item
            else:
                print("🗑️ Intento eliminar directorio: item None")
        else:
            print("🗑️ Eliminar Directorio pulsado pero no hay selección")

    # --- hosts (QTableWidget) ---
    def on_aniadir_host(self):
        """Abrir diálogo para agregar host y opciones; si el usuario acepta, añadir fila."""
        # importar dialogo (intenta desde ui/ y desde raíz para flexibilidad)
        try:
            from ui.dialogo_anadir_host import DialogoAddHost
        except Exception:
            print(Exception)

        dlg = DialogoAddHost(parent=self)
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            host, opciones = dlg.obtener_datos()
            row = self.ui.tableHost.rowCount()
            self.ui.tableHost.insertRow(row)
            self.ui.tableHost.setItem(row, 0, QtWidgets.QTableWidgetItem(host))
            self.ui.tableHost.setItem(row, 1, QtWidgets.QTableWidgetItem(opciones))
            print(f"🔗 Host añadido: {host} -> {opciones} (fila {row})")
        else:
            print("🔗 Añadir Host cancelado por el usuario.")

    def on_editar_host(self):
        """Abrir el mismo diálogo para editar la fila seleccionada."""
        selected = self.ui.tableHost.currentRow()
        if selected >= 0:
            item_host = self.ui.tableHost.item(selected, 0)
            item_opts = self.ui.tableHost.item(selected, 1)
            host = item_host.text() if item_host is not None else ""
            opts = item_opts.text() if item_opts is not None else ""

            try:
                from ui.dialogo_anadir_host import DialogoAddHost
            except Exception:
                print(Exception)

            dlg = DialogoAddHost(parent=self)
            dlg.cargar_desde(host, opts)
            if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                nuevo_host, nuevas_opts = dlg.obtener_datos()
                self.ui.tableHost.setItem(selected, 0, QtWidgets.QTableWidgetItem(nuevo_host))
                self.ui.tableHost.setItem(selected, 1, QtWidgets.QTableWidgetItem(nuevas_opts))
                print(f"✏️ Host editado fila {selected}: {nuevo_host} -> {nuevas_opts}")
            else:
                print("✏️ Edición de host cancelada por el usuario.")
        else:
            print("✏️ Editar Host pulsado pero no hay fila seleccionada")

    def on_eliminar_host(self):
        selected = self.ui.tableHost.currentRow()
        if selected >= 0:
            # leer datos antes de eliminar la fila (evita acceder a objetos liberados)
            item0 = self.ui.tableHost.item(selected, 0)
            item1 = self.ui.tableHost.item(selected, 1)

            text0 = item0.text() if item0 is not None else "[sin host]"
            text1 = item1.text() if item1 is not None else "[sin opciones]"

            # Ahora eliminar la fila (ya no accederemos a los QTableWidgetItem después)
            self.ui.tableHost.removeRow(selected)

            print(f"🗑️ Eliminar Host -> eliminado: {text0} ({text1})")
        else:
            print("🗑️ Eliminar Host pulsado pero no hay fila seleccionada")

    # --- cancelar / finalizar / volver ---
    def on_cancelar(self):
        print("❌ Cancelar pulsado (cerrar/descartar cambios)")

    def on_finalizar(self):
        print("✅ Finalizar pulsado (aplicar exportación)")

    def on_volver(self):
        """Handler del botón Volver."""
        print("↩️ Volver pulsado")
        # Si se pasó un cambiador, intentamos usarlo para cambiar a 'configuracion'
        if getattr(self, "cambiador", None) is not None:
            try:
                self.cambiador.mostrar_vista("configuracion")
                return
            except Exception:
                # si el cambiador no tiene esa vista o falla, continuamos y emitimos la señal
                pass

        # Emitir señal para que el contenedor externo maneje el cambio de vista
        self.volver_a_menu.emit()

    # --- selección ---
    def on_directorio_seleccionado(self, current, previous):
        name = current.text() if current else "[ninguno]"
        self.ui.Detalle.setTitle(f"Hosts y Opciones para: [{name}]")
        print(f"🔎 Directorio seleccionado: {name}")

    def _cargar_ejemplo(self):
        # datos iniciales de ejemplo
        for i in range(2):
            self.ui.listaDirectorios.addItem(f"/ruta/de/ejemplo{i+1}")
        self.ui.tableHost.insertRow(0)
        self.ui.tableHost.setItem(0, 0, QtWidgets.QTableWidgetItem("192.168.1.10"))
        self.ui.tableHost.setItem(0, 1, QtWidgets.QTableWidgetItem("rw,sync"))
