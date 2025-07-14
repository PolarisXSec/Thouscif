from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
    QHeaderView, QListWidget, QListWidgetItem, QLabel
)

class TablaHistorial(QWidget):
    def __init__(self):
        super().__init__()

        # 🧾 Tabla de historial
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["Tipo", "Mensaje", "Fecha/Hora"])
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SingleSelection)

        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        # 📂 Lista de archivos cifrados
        self.lista_archivos = QListWidget()

        # 📄 Etiqueta sobre la lista
        self.label_archivos = QLabel("Archivos cifrados recientes:")
        self.label_archivos.setStyleSheet("font-weight: bold; padding-top: 10px;")

        # Layout general
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tabla)
        layout.addWidget(self.label_archivos)
        layout.addWidget(self.lista_archivos)
        self.setLayout(layout)

    def actualizar(self, logs):
        self.tabla.setRowCount(0)
        for fila, (tipo, mensaje, timestamp) in enumerate(logs):
            self.tabla.insertRow(fila)
            self.tabla.setItem(fila, 0, QTableWidgetItem(tipo))
            self.tabla.setItem(fila, 1, QTableWidgetItem(mensaje))
            self.tabla.setItem(fila, 2, QTableWidgetItem(timestamp))

    def actualizar_archivos(self, archivos):
        for nombre in archivos:
            item = QListWidgetItem(nombre)
            self.lista_archivos.addItem(item)
