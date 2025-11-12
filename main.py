import sys

import PyQt6
from PyQt6 import QtWidgets


from controlador.controlador_config import ControladorConfiguracion


def main():
    app = QtWidgets.QApplication(sys.argv)

    ventana = ControladorConfiguracion()
    ventana.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()