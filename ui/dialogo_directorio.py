from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox
)

class DialogoDirectorio(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Exportar directorio - YaST2")
        self.setFixedSize(350, 150)

        layout = QVBoxLayout()

        # Etiqueta + campo de texto + botón Examinar
        hlayout = QHBoxLayout()
        self.label = QLabel("Directorio a exportar:")
        self.lineEdit = QLineEdit()
        self.botonExaminar = QPushButton("Examinar...")
        hlayout.addWidget(self.lineEdit)
        hlayout.addWidget(self.botonExaminar)

        # Botones inferiores
        botones_layout = QHBoxLayout()
        self.botonOk = QPushButton("Aceptar")
        self.botonCancelar = QPushButton("Cancelar")
        botones_layout.addStretch()
        botones_layout.addWidget(self.botonOk)
        botones_layout.addWidget(self.botonCancelar)

        # Añadir widgets al layout principal
        layout.addWidget(self.label)
        layout.addLayout(hlayout)
        layout.addLayout(botones_layout)
        self.setLayout(layout)

        # Conexiones
        self.botonExaminar.clicked.connect(self.abrir_selector)
        self.botonOk.clicked.connect(self.acceptar)
        self.botonCancelar.clicked.connect(self.reject)

    def abrir_selector(self):
        """Abre un diálogo de selección de carpeta."""
        ruta = QFileDialog.getExistingDirectory(self, "Seleccionar directorio")
        if ruta:
            self.lineEdit.setText(ruta)

    def acceptar(self):
        """Verifica que haya un directorio antes de cerrar."""
        if not self.lineEdit.text().strip():
            QMessageBox.warning(self, "Advertencia", "Por favor, selecciona un directorio antes de continuar.")
        else:
            self.accept()

    def obtener_directorio(self):
        """Devuelve el directorio seleccionado."""
        return self.lineEdit.text().strip()
