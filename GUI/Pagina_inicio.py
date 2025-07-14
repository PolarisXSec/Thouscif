from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QHBoxLayout
)

class PaginaInicio(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        # Saludo
        self.label_saludo = QLabel("¡Hola, usuario! Bienvenido de nuevo.")
        self.label_saludo.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 15px;")
        layout.addWidget(self.label_saludo)

        # Estadísticas rápidas
        self.label_estadisticas = QLabel(
            "Archivos cifrados: 10\n"
            "Acciones totales: 25\n"
            "Última acción: Archivo 'secreto.txt' cifrado correctamente."
        )
        layout.addWidget(self.label_estadisticas)

        # Botones acceso rápido
        botones_layout = QHBoxLayout()
        btn_cifrar = QPushButton("Cifrar archivo")
        btn_descifrar = QPushButton("Descifrar archivo")
        btn_historial = QPushButton("Ver historial")
        botones_layout.addWidget(btn_cifrar)
        botones_layout.addWidget(btn_descifrar)
        botones_layout.addWidget(btn_historial)
        layout.addLayout(botones_layout)

        # Últimos archivos (lista simple)
        layout.addWidget(QLabel("Archivos recientes:"))
        self.lista_archivos = QListWidget()
        archivos = ["secreto.txt", "documento.pdf", "foto.png"]
        for a in archivos:
            item = QListWidgetItem(a)
            self.lista_archivos.addItem(item)
        layout.addWidget(self.lista_archivos)

        self.setLayout(layout)
