# ui/ExportWidget.py
from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_ExportWidget(object):
    def setupUi(self, ExportWidget):
        ExportWidget.setObjectName("ExportWidget")
        ExportWidget.resize(823, 690)

        # Contenedor principal (antes centralwidget)
        self.centralwidget = QtWidgets.QWidget(parent=ExportWidget)
        self.centralwidget.setObjectName("centralwidget")

        # Layout vertical superior
        self.verticalLayoutWidget = QtWidgets.QWidget(parent=self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 801, 291))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.Maestro = QtWidgets.QGroupBox(parent=self.verticalLayoutWidget)
        self.Maestro.setObjectName("Maestro")
        self.listaDirectorios = QtWidgets.QListWidget(parent=self.Maestro)
        self.listaDirectorios.setGeometry(QtCore.QRect(10, 30, 781, 201))
        self.listaDirectorios.setObjectName("listaDirectorios")
        self.AniadirDirectorio = QtWidgets.QPushButton(parent=self.Maestro)
        self.AniadirDirectorio.setGeometry(QtCore.QRect(200, 240, 131, 41))
        self.AniadirDirectorio.setObjectName("AniadirDirectorio")
        self.Editar = QtWidgets.QPushButton(parent=self.Maestro)
        self.Editar.setGeometry(QtCore.QRect(340, 240, 121, 41))
        self.Editar.setObjectName("Editar")
        self.Eliminar = QtWidgets.QPushButton(parent=self.Maestro)
        self.Eliminar.setGeometry(QtCore.QRect(470, 240, 131, 41))
        self.Eliminar.setObjectName("Eliminar")
        self.verticalLayout.addWidget(self.Maestro)

        # Layout vertical inferior
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(parent=self.centralwidget)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(10, 310, 801, 291))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")

        self.Detalle = QtWidgets.QGroupBox(parent=self.verticalLayoutWidget_2)
        self.Detalle.setObjectName("Detalle")
        self.tableHost = QtWidgets.QTableWidget(parent=self.Detalle)
        self.tableHost.setGeometry(QtCore.QRect(10, 30, 781, 201))
        self.tableHost.setRowCount(0)
        self.tableHost.setColumnCount(2)
        self.tableHost.setObjectName("tableHost")
        self.AniadirHost = QtWidgets.QPushButton(parent=self.Detalle)
        self.AniadirHost.setGeometry(QtCore.QRect(200, 240, 131, 41))
        self.AniadirHost.setObjectName("AniadirHost")
        self.EditarHost = QtWidgets.QPushButton(parent=self.Detalle)
        self.EditarHost.setGeometry(QtCore.QRect(340, 240, 121, 41))
        self.EditarHost.setObjectName("EditarHost")
        self.EliminarHost = QtWidgets.QPushButton(parent=self.Detalle)
        self.EliminarHost.setGeometry(QtCore.QRect(470, 240, 131, 41))
        self.EliminarHost.setObjectName("EliminarHost")
        self.verticalLayout_3.addWidget(self.Detalle)

        # Botones inferiores
        self.Cancelar = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Cancelar.setGeometry(QtCore.QRect(470, 610, 111, 31))
        self.Cancelar.setObjectName("Cancelar")
        self.Finalizar = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Finalizar.setGeometry(QtCore.QRect(700, 610, 111, 31))
        self.Finalizar.setObjectName("Finalizar")
        self.pushButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(590, 610, 93, 31))
        self.pushButton.setObjectName("Volver")

        # Añadimos el centralwidget al widget raíz
        # (en un QMainWindow esto lo hace setCentralWidget; aquí hacemos add en layout del ExportWidget)
        # Si quieres que centralwidget rellene ExportWidget, colocamos un layout principal:
        self.layout_principal = QtWidgets.QVBoxLayout(ExportWidget)
        self.layout_principal.setContentsMargins(0, 0, 0, 0)
        self.layout_principal.addWidget(self.centralwidget)

        self.retranslateUi(ExportWidget)
        QtCore.QMetaObject.connectSlotsByName(ExportWidget)

    def retranslateUi(self, ExportWidget):
        _translate = QtCore.QCoreApplication.translate
        ExportWidget.setWindowTitle(_translate("ExportWidget", "ExportWidget"))
        self.Maestro.setTitle(_translate("ExportWidget", "Directorios para exportar"))
        self.AniadirDirectorio.setText(_translate("ExportWidget", "Agregar Directorio"))
        self.Editar.setText(_translate("ExportWidget", "Editar Directorio"))
        self.Eliminar.setText(_translate("ExportWidget", "Eliminar Directorio"))
        self.Detalle.setTitle(_translate("ExportWidget", "Hosts y Opciones para: [ninguno]"))
        self.AniadirHost.setText(_translate("ExportWidget", "Agregar Host"))
        self.EditarHost.setText(_translate("ExportWidget", "Editar Host"))
        self.EliminarHost.setText(_translate("ExportWidget", "Eliminar Host"))
        self.Cancelar.setText(_translate("ExportWidget", "Cancelar"))
        self.Finalizar.setText(_translate("ExportWidget", "Finalizar"))
        self.pushButton.setText(_translate("ExportWidget", "Volver"))
