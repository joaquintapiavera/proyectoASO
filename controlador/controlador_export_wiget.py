# controlador/controlador_export_wiget.py
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import pyqtSignal
from ui.ExportWidget import Ui_ExportWidget

# diálogos (usa tus módulos existentes; se intenta varias rutas)
try:
    from ui.dialogo_directorio import DialogoDirectorio
except Exception:
    from ui.dialogo_directorio import DialogoDirectorio

try:
    from ui.dialogo_anadir_host import DialogoAddHost
except Exception:
    try:
        from ui.anadir_host import DialogoAddHost
    except Exception:
        # si ninguno existe, se lanzará ImportError y deberás adaptarlo
        raise

# modelo (archivo que agregaste previamente: modelos/modelo_exports.py)
from modelos.modelo_exports import ModeloExports, HostEntry, ExportEntry

class ControladorExportWidget(QtWidgets.QWidget):
    volver_a_menu = pyqtSignal()

    def __init__(self, cambiador=None, parent=None, password: str | None = None, test_mode: bool = True):
        """
        cambiador: tu CambiadorVistas (opcional).
        password: (opcional) si manejas sudo luego.
        test_mode: True = no escribe /etc/exports (preview).
        """
        super().__init__(parent)
        self.cambiador = cambiador
        self.password = password
        self.ui = Ui_ExportWidget()
        self.ui.setupUi(self)

        # Modelo central
        self.modelo = ModeloExports(test_mode=test_mode)

        # Tabla hosts
        self.ui.tableHost.setColumnCount(2)
        self.ui.tableHost.setHorizontalHeaderLabels(["Host", "Opciones"])
        self.ui.tableHost.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.ui.tableHost.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.ui.tableHost.verticalHeader().setVisible(False)

        # Botones / conexiones
        self.ui.AniadirDirectorio.clicked.connect(self.on_aniadir_directorio)
        self.ui.Editar.clicked.connect(self.on_editar_directorio)
        self.ui.Eliminar.clicked.connect(self.on_eliminar_directorio)

        self.ui.AniadirHost.clicked.connect(self.on_aniadir_host)
        self.ui.EditarHost.clicked.connect(self.on_editar_host)
        self.ui.EliminarHost.clicked.connect(self.on_eliminar_host)

        self.ui.Cancelar.clicked.connect(self.on_cancelar)
        self.ui.Finalizar.clicked.connect(self.on_finalizar)
        self.ui.pushButton.clicked.connect(self.on_volver)

        # Selección en la lista -> muestra hosts
        self.ui.listaDirectorios.currentItemChanged.connect(self.on_directorio_seleccionado)

        # llenar UI desde modelo (y asociar model_index en cada QListWidgetItem)
        self._refresh_lista_directorios()

    # ---------------- Helpers UI <-> modelo ----------------
    def _refresh_lista_directorios(self):
        """
        Rellena listaDirectorios. Para cada item que representa un export válido,
        guardamos el índice del modelo en Qt.UserRole: item.setData(Qt.UserRole, model_index)
        Comentarios/lines vacías se muestran como items no seleccionables (data = None).
        """
        self.ui.listaDirectorios.clear()
        for model_idx, e in enumerate(self.modelo.exports):
            if e.raw_comment and not e.path:
                item = QtWidgets.QListWidgetItem(e.raw_comment)
                # quitar la selectabilidad para comentarios
                item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsSelectable)
                item.setData(QtCore.Qt.ItemDataRole.UserRole, None)
                self.ui.listaDirectorios.addItem(item)
            elif e.path:
                item = QtWidgets.QListWidgetItem(e.path)
                # almacenamos el índice del modelo en el item
                item.setData(QtCore.Qt.ItemDataRole.UserRole, model_idx)
                self.ui.listaDirectorios.addItem(item)

    def _get_selected_model_index(self) -> int | None:
        """
        Devuelve el índice dentro de self.modelo.exports del item seleccionado,
        o None si no hay selección o el item no representa un export.
        """
        item = self.ui.listaDirectorios.currentItem()
        if not item:
            return None
        data = item.data(QtCore.Qt.ItemDataRole.UserRole)
        if data is None:
            return None
        # data es el model_idx (int)
        return int(data)

    def _populate_hosts_table(self, export_entry: ExportEntry):
        """
        Llena la tabla de hosts desde el ExportEntry.
        """
        self.ui.tableHost.blockSignals(True)
        self.ui.tableHost.setRowCount(0)
        for h in export_entry.hosts:
            r = self.ui.tableHost.rowCount()
            self.ui.tableHost.insertRow(r)
            self.ui.tableHost.setItem(r, 0, QtWidgets.QTableWidgetItem(h.host))
            self.ui.tableHost.setItem(r, 1, QtWidgets.QTableWidgetItem(h.options))
        self.ui.tableHost.blockSignals(False)

    # ---------------- Directorios ----------------
    def on_aniadir_directorio(self):
        dlg = DialogoDirectorio(parent=self)
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            ruta = dlg.obtener_directorio()
            if ruta:
                new_entry = self.modelo.add_export(ruta)
                # refrescar UI y seleccionar el nuevo item
                self._refresh_lista_directorios()
                # localizar el QListWidgetItem con model_idx del new_entry
                # buscamos el último model_idx que coincida con ruta (por si hay duplicados)
                for i in range(self.ui.listaDirectorios.count()-1, -1, -1):
                    itm = self.ui.listaDirectorios.item(i)
                    if itm.data(QtCore.Qt.ItemDataRole.UserRole) is not None and itm.text() == ruta:
                        self.ui.listaDirectorios.setCurrentItem(itm)
                        break

    def on_editar_directorio(self):
        model_idx = self._get_selected_model_index()
        if model_idx is None:
            QtWidgets.QMessageBox.information(self, "Editar directorio", "Seleccioná un directorio válido para editar.")
            return
        entry = self.modelo.exports[model_idx]
        dlg = DialogoDirectorio(parent=self)
        dlg.lineEdit.setText(entry.path)
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            nueva = dlg.obtener_directorio()
            if nueva:
                entry.path = nueva
                # refrescar lista: el item debe mantener su data model_idx
                self._refresh_lista_directorios()
                # re-seleccionar item con model_idx igual
                for i in range(self.ui.listaDirectorios.count()):
                    itm = self.ui.listaDirectorios.item(i)
                    if itm.data(QtCore.Qt.ItemDataRole.UserRole) == model_idx:
                        self.ui.listaDirectorios.setCurrentItem(itm)
                        break

    def on_eliminar_directorio(self):
        model_idx = self._get_selected_model_index()
        if model_idx is None:
            QtWidgets.QMessageBox.information(self, "Eliminar directorio", "Seleccioná un directorio válido para eliminar.")
            return
        path = self.modelo.exports[model_idx].path
        reply = QtWidgets.QMessageBox.question(self, "Confirmar eliminación",
                                               f"¿Eliminar export '{path}'?", QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        if reply != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        # eliminar del modelo
        del self.modelo.exports[model_idx]
        # refrescar UI
        self._refresh_lista_directorios()
        self.ui.tableHost.setRowCount(0)

    # ---------------- Hosts ----------------
    def on_aniadir_host(self):
        model_idx = self._get_selected_model_index()
        if model_idx is None:
            QtWidgets.QMessageBox.information(self, "Añadir host", "Seleccioná primero un directorio/export.")
            return
        entry = self.modelo.exports[model_idx]
        dlg = DialogoAddHost(parent=self)
        if hasattr(dlg, "cargar_desde"):
            # limpiar si el diálogo deja campos (no obligatorio)
            try:
                dlg.cargar_desde("", "")
            except Exception:
                pass
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            host, opciones = dlg.obtener_datos()
            if host:
                entry.hosts.append(HostEntry(host=host, options=opciones))
                self._populate_hosts_table(entry)

    def on_editar_host(self):
        model_idx = self._get_selected_model_index()
        if model_idx is None:
            QtWidgets.QMessageBox.information(self, "Editar host", "Seleccioná primero un directorio/export.")
            return
        entry = self.modelo.exports[model_idx]
        row = self.ui.tableHost.currentRow()
        if row < 0 or row >= len(entry.hosts):
            QtWidgets.QMessageBox.information(self, "Editar host", "Seleccioná primero una fila de host para editar.")
            return
        host_entry = entry.hosts[row]
        dlg = DialogoAddHost(parent=self)
        if hasattr(dlg, "cargar_desde"):
            dlg.cargar_desde(host_entry.host, host_entry.options)
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            nuevo_host, nuevas_opts = dlg.obtener_datos()
            host_entry.host = nuevo_host
            host_entry.options = nuevas_opts
            self._populate_hosts_table(entry)

    def on_eliminar_host(self):
        model_idx = self._get_selected_model_index()
        if model_idx is None:
            QtWidgets.QMessageBox.information(self, "Eliminar host", "Seleccioná primero un directorio/export.")
            return
        entry = self.modelo.exports[model_idx]
        row = self.ui.tableHost.currentRow()
        if row < 0 or row >= len(entry.hosts):
            QtWidgets.QMessageBox.information(self, "Eliminar host", "Seleccioná primero una fila de host para eliminar.")
            return
        host_info = f"{entry.hosts[row].host} ({entry.hosts[row].options})"
        reply = QtWidgets.QMessageBox.question(self, "Confirmar eliminación",
                                               f"¿Eliminar host {host_info}?", QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        if reply != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        del entry.hosts[row]
        self._populate_hosts_table(entry)

    # ---------------- Generales ----------------
    def on_cancelar(self):
        # recargar el modelo desde ejemplo o fichero según test_mode
        if self.modelo.test_mode:
            self.modelo.load_from_string(self.modelo._sample_content())
        else:
            try:
                self.modelo.load_from_file()
            except Exception as e:
                print("Error recargando /etc/exports:", e)
        self._refresh_lista_directorios()
        self.ui.tableHost.setRowCount(0)

    def on_finalizar(self):
        """
        Guarda o muestra preview según test_mode. Si test_mode True -> preview.
        Si test_mode False -> intenta escribir (modelo.save_to_file requiere overwrite=True).
        """
        try:
            if self.modelo.test_mode:
                preview = self.modelo.save_to_file()  # devuelve texto en modo test
                dlg = QtWidgets.QDialog(self)
                dlg.setWindowTitle("Preview /etc/exports (test mode)")
                layout = QtWidgets.QVBoxLayout(dlg)
                edt = QtWidgets.QPlainTextEdit()
                edt.setPlainText(preview)
                edt.setReadOnly(True)
                layout.addWidget(edt)
                btn = QtWidgets.QPushButton("Cerrar")
                btn.clicked.connect(dlg.accept)
                layout.addWidget(btn)
                dlg.resize(800, 400)
                dlg.exec()
            else:
                # en modo real, forzamos overwrite=True para que el modelo escriba
                self.modelo.save_to_file(overwrite=True)
                QtWidgets.QMessageBox.information(self, "Guardado", "/etc/exports guardado correctamente.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")

    def on_volver(self):
        if getattr(self, "cambiador", None) is not None:
            try:
                self.cambiador.mostrar_vista("configuracion")
                return
            except Exception:
                pass
        self.volver_a_menu.emit()

    # ---------------- Selección ----------------
    def on_directorio_seleccionado(self, current, previous):
        """
        Cuando cambia selección, recuperamos el model_index del item y mostramos hosts
        guardados en el modelo. Si la selección es un comentario/empty -> limpiamos tabla.
        """
        if not current:
            self.ui.Detalle.setTitle("Hosts y Opciones para: [ninguno]")
            self.ui.tableHost.setRowCount(0)
            return
        data = current.data(QtCore.Qt.ItemDataRole.UserRole)
        if data is None:
            self.ui.Detalle.setTitle("Hosts y Opciones para: [ninguno]")
            self.ui.tableHost.setRowCount(0)
            return
        model_idx = int(data)
        if model_idx < 0 or model_idx >= len(self.modelo.exports):
            self.ui.Detalle.setTitle("Hosts y Opciones para: [ninguno]")
            self.ui.tableHost.setRowCount(0)
            return
        name = self.modelo.exports[model_idx].path
        self.ui.Detalle.setTitle(f"Hosts y Opciones para: [{name}]")
        self._populate_hosts_table(self.modelo.exports[model_idx])
