from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_ExportWidget(object):
    def setupUi(self, ExportWidget):
        ExportWidget.setObjectName("ExportWidget")
        ExportWidget.resize(823, 690)
        self.centralwidget = QtWidgets.QWidget(parent=ExportWidget)
        self.centralwidget.setObjectName("centralwidget")

        # Layout vertical superior
        self.verticalLayoutWidget = QtWidgets.QWidget(parent=self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 801, 291))
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        self.Maestro = QtWidgets.QGroupBox(parent=self.verticalLayoutWidget)
        self.Maestro.setTitle("Directorios para exportar")
        self.listaDirectorios = QtWidgets.QListWidget(parent=self.Maestro)
        self.listaDirectorios.setGeometry(QtCore.QRect(10, 30, 781, 201))
        self.AniadirDirectorio = QtWidgets.QPushButton(parent=self.Maestro)
        self.AniadirDirectorio.setGeometry(QtCore.QRect(200, 240, 131, 41))
        self.AniadirDirectorio.setText("Agregar Directorio")
        self.Editar = QtWidgets.QPushButton(parent=self.Maestro)
        self.Editar.setGeometry(QtCore.QRect(340, 240, 121, 41))
        self.Editar.setText("Editar Directorio")
        self.Eliminar = QtWidgets.QPushButton(parent=self.Maestro)
        self.Eliminar.setGeometry(QtCore.QRect(470, 240, 131, 41))
        self.Eliminar.setText("Eliminar Directorio")
        self.verticalLayout.addWidget(self.Maestro)

        # Layout vertical inferior
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(parent=self.centralwidget)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(10, 310, 801, 291))
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)

        self.Detalle = QtWidgets.QGroupBox(parent=self.verticalLayoutWidget_2)
        self.Detalle.setTitle("Hosts y Opciones para: [ninguno]")
        self.tableHost = QtWidgets.QTableWidget(parent=self.Detalle)
        self.tableHost.setGeometry(QtCore.QRect(10, 30, 781, 201))
        self.tableHost.setRowCount(0)
        self.tableHost.setColumnCount(2)
        self.AniadirHost = QtWidgets.QPushButton(parent=self.Detalle)
        self.AniadirHost.setGeometry(QtCore.QRect(200, 240, 131, 41))
        self.AniadirHost.setText("Agregar Host")
        self.EditarHost = QtWidgets.QPushButton(parent=self.Detalle)
        self.EditarHost.setGeometry(QtCore.QRect(340, 240, 121, 41))
        self.EditarHost.setText("Editar Host")
        self.EliminarHost = QtWidgets.QPushButton(parent=self.Detalle)
        self.EliminarHost.setGeometry(QtCore.QRect(470, 240, 131, 41))
        self.EliminarHost.setText("Eliminar Host")
        self.verticalLayout_3.addWidget(self.Detalle)

        # Botones inferiores
        self.Cancelar = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Cancelar.setGeometry(QtCore.QRect(580, 610, 111, 31))
        self.Cancelar.setText("Cancelar")
        self.Finalizar = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Finalizar.setGeometry(QtCore.QRect(700, 610, 111, 31))
        self.Finalizar.setText("Finalizar")
