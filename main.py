# main.py
import sys
from PyQt6 import QtWidgets, QtCore
from utilidades.cambiador_vistas import CambiadorVistas
from controlador.controlador_export_wiget import ControladorExportWidget
from controlador.controlador_config import ControladorConfiguracion

# importa el diálogo
from ui.password_dialog import PasswordDialog

def main():
    app = QtWidgets.QApplication(sys.argv)

    # Mostrar diálogo de contraseña primero
    cmd = "/sbin/yast2 nfs_server"  # el comando que quieres ejecutar (solo para mostrar)
    dlg = PasswordDialog(command=cmd, service_name="mi_app_nfs")
    result = dlg.exec()

    if result == QtWidgets.QDialog.DialogCode.Accepted:
        if dlg.ignore:
            print("Usuario eligió ignorar (continuar sin privilegios de root).")
            # Proceder sin root
        else:
            # Aquí tienes la contraseña en dlg.password (si OK)
            # -> No hago nada con ella directamente (por seguridad). Es tuya para usar.
            print("Contraseña introducida (longitud):", len(dlg.password or ""))
    else:
        # Cancel: cerramos la app
        print("Inicio cancelado por el usuario.")
        sys.exit(0)

    # Si llegamos aquí, mostramos la ventana principal y el sistema de vistas
    main_win = QtWidgets.QMainWindow()
    main_win.setWindowTitle("Mi App NFS")
    stacked = QtWidgets.QStackedWidget()
    main_win.setCentralWidget(stacked)

    cambiador = CambiadorVistas(stacked)

    # Registro perezoso (factories)
    cambiador.agregar_vista("configuracion", lambda: ControladorConfiguracion(cambiador=cambiador))
    cambiador.agregar_vista("export", lambda: ControladorExportWidget(cambiador=cambiador))

    # Vista por defecto
    cambiador.mostrar_vista("configuracion")

    main_win.resize(900, 700)
    main_win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
