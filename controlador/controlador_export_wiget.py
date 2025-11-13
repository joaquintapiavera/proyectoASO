from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import pyqtSignal
from ui.ExportWidget import Ui_ExportWidget
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
        raise
from modelos.modelo_exports import ModeloExports, HostEntry, ExportEntry
import os
import subprocess
import shlex
import shutil
from typing import Optional


class ControladorExportWidget(QtWidgets.QWidget):
    volver_a_menu = pyqtSignal()

    def __init__(self, cambiador=None, parent=None):
        super().__init__(parent)
        self.cambiador = cambiador
        self.ui = Ui_ExportWidget()
        self.ui.setupUi(self)

        # Modelo
        self.modelo = ModeloExports(path="/etc/exports")

        # Configuración básica de la lista y tabla
        self.ui.listaDirectorios.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.ui.listaDirectorios.setUniformItemSizes(True)
        self.ui.listaDirectorios.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.ui.listaDirectorios.setEnabled(True)  # asegurar que la lista esté habilitada

        self.ui.tableHost.setColumnCount(2)
        self.ui.tableHost.setHorizontalHeaderLabels(["Host", "Opciones"])
        self.ui.tableHost.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.ui.tableHost.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.ui.tableHost.verticalHeader().setVisible(False)

        # Conexiones
        self.ui.AniadirDirectorio.clicked.connect(self.on_aniadir_directorio)
        self.ui.Editar.clicked.connect(self.on_editar_directorio)
        self.ui.Eliminar.clicked.connect(self.on_eliminar_directorio)
        self.ui.AniadirHost.clicked.connect(self.on_aniadir_host)
        self.ui.EditarHost.clicked.connect(self.on_editar_host)
        self.ui.EliminarHost.clicked.connect(self.on_eliminar_host)
        self.ui.Cancelar.clicked.connect(self.on_cancelar)
        self.ui.Finalizar.clicked.connect(self.on_finalizar)
        self.ui.pushButton.clicked.connect(self.on_volver)

        self.ui.listaDirectorios.currentItemChanged.connect(self.on_directorio_seleccionado)
        self.ui.listaDirectorios.itemClicked.connect(self.on_item_clicked)

        # Carga inicial
        self._refresh_lista_directorios()

        # Forzar foco para que teclas básicas (↑ ↓) funcionen
        self.ui.listaDirectorios.setFocus()

    # -----------------------
    # Refrescar lista
    # -----------------------
    def _refresh_lista_directorios(self, keep_selected_path: Optional[str] = None):
        """
        Carga self.modelo.exports en la QListWidget.
        Los items con path no vacíos quedan seleccionables y habilitados.
        Los items que son comentarios quedan deshabilitados (gris).
        Si se pasa keep_selected_path, intenta restaurar la selección a esa ruta.
        """
        # intentar guardar selección actual por path si no se pidió explícitamente
        if keep_selected_path is None:
            cur = self.ui.listaDirectorios.currentItem()
            keep_selected_path = None
            if cur and cur.data(QtCore.Qt.ItemDataRole.UserRole) is not None:
                # guardamos el path asociado si existe
                saved = cur.data(QtCore.Qt.ItemDataRole.UserRole + 1)
                if saved:
                    keep_selected_path = str(saved).strip()

        self.ui.listaDirectorios.clear()

        for model_idx, e in enumerate(self.modelo.exports):
            path = (e.path or "").strip()
            # si no hay path pero sí raw_comment -> mostrar comentario deshabilitado
            if not path and getattr(e, "raw_comment", None):
                item = QtWidgets.QListWidgetItem(e.raw_comment)
                # quitar flags de selectable/enabled para que aparezca gris
                item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsSelectable & ~QtCore.Qt.ItemFlag.ItemIsEnabled)
                item.setData(QtCore.Qt.ItemDataRole.UserRole, None)
                self.ui.listaDirectorios.addItem(item)
                continue

            # si hay path -> item habilitado y seleccionable
            if path:
                item = QtWidgets.QListWidgetItem(path)
                # asignar explícitamente flags seleccionable + enabled
                flags = QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled
                item.setFlags(flags)
                # guardamos el índice del modelo y el path en UserRole / UserRole+1
                item.setData(QtCore.Qt.ItemDataRole.UserRole, model_idx)
                item.setData(QtCore.Qt.ItemDataRole.UserRole + 1, path)
                self.ui.listaDirectorios.addItem(item)

        # intentar restaurar selección por path
        if keep_selected_path:
            for i in range(self.ui.listaDirectorios.count()):
                itm = self.ui.listaDirectorios.item(i)
                data = itm.data(QtCore.Qt.ItemDataRole.UserRole)
                if data is not None:
                    text = (itm.data(QtCore.Qt.ItemDataRole.UserRole + 1) or itm.text()).strip()
                    if text == keep_selected_path.strip():
                        self.ui.listaDirectorios.setCurrentItem(itm)
                        return

        # si no se restauró: seleccionar primer item seleccionable
        for i in range(self.ui.listaDirectorios.count()):
            itm = self.ui.listaDirectorios.item(i)
            if itm and itm.data(QtCore.Qt.ItemDataRole.UserRole) is not None:
                self.ui.listaDirectorios.setCurrentItem(itm)
                break

    # -----------------------
    # Helpers
    # -----------------------
    def debug_print_exports(self):
        print("DEBUG: modelo.exports:")
        for i, e in enumerate(self.modelo.exports):
            print(i, repr(e.path), "hosts:", [(h.host, h.options) for h in e.hosts], "raw_comment:", bool(getattr(e, "raw_comment", None)))

    def _get_selected_model_index(self) -> int | None:
        item = self.ui.listaDirectorios.currentItem()
        if not item:
            return None
        data = item.data(QtCore.Qt.ItemDataRole.UserRole)
        if data is None:
            return None
        return int(data)

    def _populate_hosts_table(self, export_entry: ExportEntry):
        self.ui.tableHost.blockSignals(True)
        self.ui.tableHost.setRowCount(0)
        for h in export_entry.hosts:
            r = self.ui.tableHost.rowCount()
            self.ui.tableHost.insertRow(r)
            self.ui.tableHost.setItem(r, 0, QtWidgets.QTableWidgetItem(h.host))
            self.ui.tableHost.setItem(r, 1, QtWidgets.QTableWidgetItem(h.options))
        self.ui.tableHost.blockSignals(False)

    # -----------------------
    # Eventos UI
    # -----------------------
    def on_item_clicked(self, item):
        # asegurarnos de que al clickear quede current
        self.ui.listaDirectorios.setCurrentItem(item)
        self.ui.listaDirectorios.setFocus()

    def on_aniadir_directorio(self):
        dlg = DialogoDirectorio(parent=self)
        if dlg.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return
        ruta = dlg.obtener_directorio()
        if not ruta:
            return
        if not os.path.exists(ruta):
            q = QtWidgets.QMessageBox.question(self, "Ruta no encontrada",
                                               f"La ruta '{ruta}' no existe. ¿Deseas crearla?",
                                               QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            if q != QtWidgets.QMessageBox.StandardButton.Yes:
                return
            try:
                os.makedirs(ruta, exist_ok=True)
            except PermissionError:
                QtWidgets.QMessageBox.critical(self, "Error", f"No se pudo crear el directorio '{ruta}': permiso denegado")
                return
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"No se pudo crear el directorio '{ruta}': {e}")
                return
        self.modelo.add_export(ruta)
        self._refresh_lista_directorios(keep_selected_path=ruta)
        # seleccionar el nuevo
        for i in range(self.ui.listaDirectorios.count()-1, -1, -1):
            itm = self.ui.listaDirectorios.item(i)
            if itm.data(QtCore.Qt.ItemDataRole.UserRole) is not None and itm.text() == ruta:
                self.ui.listaDirectorios.setCurrentItem(itm)
                break
        # abrir diálogo para añadir host
        self._open_add_host_for_selected_export()

    def on_editar_directorio(self):
        model_idx = self._get_selected_model_index()
        if model_idx is None:
            QtWidgets.QMessageBox.information(self, "Editar directorio", "Seleccioná un directorio válido para editar.")
            return
        entry = self.modelo.exports[model_idx]
        dlg = DialogoDirectorio(parent=self)
        dlg.lineEdit.setText(entry.path)
        if dlg.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return
        nueva = dlg.obtener_directorio()
        if not nueva:
            return
        if nueva != entry.path and not os.path.exists(nueva):
            q = QtWidgets.QMessageBox.question(self, "Ruta no encontrada",
                                               f"La ruta '{nueva}' no existe. ¿Deseas crearla?",
                                               QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            if q != QtWidgets.QMessageBox.StandardButton.Yes:
                return
            try:
                os.makedirs(nueva, exist_ok=True)
            except PermissionError:
                QtWidgets.QMessageBox.critical(self, "Error", f"No se pudo crear el directorio '{nueva}': permiso denegado")
                return
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"No se pudo crear el directorio '{nueva}': {e}")
                return
        entry.path = nueva
        self._refresh_lista_directorios(keep_selected_path=nueva)

    def on_eliminar_directorio(self):
        model_idx = self._get_selected_model_index()
        if model_idx is None:
            QtWidgets.QMessageBox.information(self, "Eliminar directorio", "Seleccioná un directorio válido para eliminar.")
            return
        path = self.modelo.exports[model_idx].path
        reply = QtWidgets.QMessageBox.question(self, "Confirmar eliminación", f"¿Eliminar export '{path}'?",
                                               QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        if reply != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        del self.modelo.exports[model_idx]
        self._refresh_lista_directorios()

    def _open_add_host_for_selected_export(self):
        model_idx = self._get_selected_model_index()
        if model_idx is None:
            return
        entry = self.modelo.exports[model_idx]
        dlg = DialogoAddHost(parent=self)
        if hasattr(dlg, "cargar_desde"):
            try:
                dlg.cargar_desde("", "")
            except Exception:
                pass
        if dlg.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return
        host, opciones = dlg.obtener_datos()
        if not host:
            return
        entry.hosts.append(HostEntry(host=host, options=opciones))
        self._populate_hosts_table(entry)
        self._refresh_lista_directorios(keep_selected_path=entry.path)

    def on_aniadir_host(self):
        model_idx = self._get_selected_model_index()
        if model_idx is None:
            QtWidgets.QMessageBox.information(self, "Añadir host", "Seleccioná primero un directorio/export.")
            return
        entry = self.modelo.exports[model_idx]
        dlg = DialogoAddHost(parent=self)
        if hasattr(dlg, "cargar_desde"):
            try:
                dlg.cargar_desde("", "")
            except Exception:
                pass
        if dlg.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return
        host, opciones = dlg.obtener_datos()
        if not host:
            return
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
        if dlg.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return
        nuevo_host, nuevas_opts = dlg.obtener_datos()
        if not nuevo_host:
            return
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
        reply = QtWidgets.QMessageBox.question(self, "Confirmar eliminación", f"¿Eliminar host {host_info}?",
                                               QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        if reply != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        del entry.hosts[row]
        self._populate_hosts_table(entry)

    # -----------------------
    # Guardar / aplicar
    # -----------------------
    def on_cancelar(self):
        try:
            self.modelo.load_from_file()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error recargando /etc/exports: {e}")
        self._refresh_lista_directorios()
        self.ui.tableHost.setRowCount(0)

    def aplicar_cambios_nfs(self) -> tuple[bool, str]:
        cmd = "exportfs -ra"
        if not shutil.which("exportfs"):
            return False, "Error: 'exportfs' no está en PATH."
        try:
            proc = subprocess.run(shlex.split(cmd), capture_output=True)
            if proc.returncode == 0:
                return True, proc.stdout.decode(errors="ignore")
            else:
                return False, proc.stderr.decode(errors="ignore")
        except FileNotFoundError:
            return False, "Error: El comando 'exportfs' no se encontró en el PATH."
        except Exception as e:
            return False, str(e)

    def on_finalizar(self):
        for p in self.modelo.get_exports_paths():
            if not ModeloExports.verificar_directorio(p):
                ok, msg = ModeloExports.crear_directorio(p)
                if not ok:
                    QtWidgets.QMessageBox.critical(self, "Error", f"No se pudo crear directorio {p}: {msg}")
                    return
        try:
            self.modelo.save_to_file(overwrite=True)
        except PermissionError as e:
            QtWidgets.QMessageBox.critical(self, "Error de permisos", str(e))
            return
        ok2, out = self.aplicar_cambios_nfs()
        if not ok2:
            QtWidgets.QMessageBox.critical(self, "Error", f"Se guardó /etc/exports pero exportfs falló:\n{out}")
        else:
            QtWidgets.QMessageBox.information(self, "Guardado", "/etc/exports guardado y exportfs recargado.")
        self._refresh_lista_directorios()

    # -----------------------
    # Navegación simple / selección
    # -----------------------
    def on_volver(self):
        if getattr(self, "cambiador", None) is not None:
            try:
                self.cambiador.mostrar_vista("configuracion")
                return
            except Exception:
                pass
        self.volver_a_menu.emit()

    def on_directorio_seleccionado(self, current, previous):
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
        name = (self.modelo.exports[model_idx].path or "").strip()
        self.ui.Detalle.setTitle(f"Hosts y Opciones para: [{name}]")
        self._populate_hosts_table(self.modelo.exports[model_idx])
