import sys
import os
from PyQt6 import QtWidgets
from utilidades.cambiador_vistas import CambiadorVistas
from controlador.controlador_export_wiget import ControladorExportWidget
from controlador.controlador_config import ControladorConfiguracion
from ui.password_dialog import PasswordDialog
from modelos.session_manager import RootSession

def main():
    app = QtWidgets.QApplication(sys.argv)
    session = RootSession.instance()
    if not session.is_root:
        cmd = "/sbin/yast2 nfs_server"
        dlg = PasswordDialog(command=cmd, service_name="mi_app_nfs")
        result = dlg.exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            if dlg.ignore:
                pass
            else:
                session.set_authenticated(password=dlg.password)
        else:
            sys.exit(0)
    else:
        session.set_authenticated(password=None)

    main_win = QtWidgets.QMainWindow()
    main_win.setWindowTitle("Mi App NFS")
    stacked = QtWidgets.QStackedWidget()
    main_win.setCentralWidget(stacked)

    cambiador = CambiadorVistas(stacked)

    cambiador.agregar_vista("configuracion", lambda: ControladorConfiguracion(cambiador=cambiador))
    cambiador.agregar_vista("export", lambda: ControladorExportWidget(cambiador=cambiador))

    cambiador.mostrar_vista("configuracion")

    main_win.resize(900, 700)
    main_win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
