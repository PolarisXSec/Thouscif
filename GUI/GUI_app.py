from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget, QTableWidget, QTableWidgetItem,
    QApplication, QFileDialog, QLineEdit, QDialog, QMessageBox
)
from PySide6.QtGui import QPixmap, QFont, QFontDatabase
from PySide6.QtCore import Qt
import sys
from login import DATABASE, usuario_actual, security
from vault_app import cifrador, Descifrador
from PySide6.QtWidgets import QListWidget
from datetime import datetime  
from .Historial_acciones import TablaHistorial
from .Pagina_inicio import PaginaInicio

class MainWindow(QWidget):
    def __init__(self, usuario, contraseña, salt):
        super().__init__()
        self.setWindowTitle("MyVault")
        self.resize(1000, 600)
        self.db = DATABASE()
        self.sec = security()
        self.usuario = usuario
        self.contraseña = contraseña
        self.salt = salt
        self.contadorMostrar = 0
        self.usuario_id = usuario_actual.id

        layout_principal = QHBoxLayout(self)

        # Menú lateral
        menu_lateral = QWidget()
        layout_menu = QVBoxLayout(menu_lateral)
        layout_menu.setAlignment(Qt.AlignTop)
        menu_lateral.setStyleSheet("background-color: #0F6CBD;")

        roboto = self.fuentes_personalizadas("Fuentes/Roboto_Condensed-Medium.ttf", 10, False)

        boton_inicio = QPushButton("Inicio")
        boton_archivos = QPushButton("Archivos")
        boton_archivos.setCheckable(True)
        boton_archivos.setFont(roboto)

        # Submenú
        submenu_archivos = QWidget()
        submenu_layout = QVBoxLayout(submenu_archivos)
        submenu_layout.setContentsMargins(30, 0, 0, 0)
        submenu_layout.setSpacing(0)
        submenu_archivos.setVisible(False)

        boton_cifrar = QPushButton("Cifrar archivo")
        boton_descifrar = QPushButton("Descifrar archivo")

        for subboton in [boton_cifrar, boton_descifrar]:
            subboton.setFont(roboto)
            subboton.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: white;
                    padding: 5px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                }
            """)
            submenu_layout.addWidget(subboton)

        boton_archivos.toggled.connect(lambda checked: submenu_archivos.setVisible(checked))

        boton_contraseñas = QPushButton("Contraseñas")
        boton_configuracion = QPushButton("Configuración")
        boton_reports = QPushButton("Reportes")

        # Estilo general para los botones
        estilo_boton_lateral = """
            QPushButton {
                background-color: transparent;
                border: none;
                color: white;
                padding: 10px;
                font-size: 14px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QPushButton:checked {
                background-color: rgba(255, 255, 255, 0.15);
            }
        """

        for boton in [boton_inicio, boton_archivos, boton_contraseñas, boton_reports, boton_configuracion]:
            boton.setFont(roboto)
            boton.setStyleSheet(estilo_boton_lateral)

        # Añadir botones al layout lateral
        layout_menu.addWidget(boton_inicio)
        layout_menu.addWidget(boton_archivos)
        layout_menu.addWidget(submenu_archivos)
        layout_menu.addWidget(boton_contraseñas)
        layout_menu.addWidget(boton_reports)
        layout_menu.addWidget(boton_configuracion)

        # Contenido principal
        self.stack = QStackedWidget()

        self.pagina_inicio = QWidget()
        layout_inicio = QVBoxLayout(self.pagina_inicio)
        self.pagina_iniciar = PaginaInicio()
        layout_inicio.addWidget(self.pagina_inicio)

        self.pagina_archivos = QWidget()
        layout_archivos = QVBoxLayout(self.pagina_archivos)
        self.label_estado_archivo = QLabel("")
        self.label_estado_archivo.setWordWrap(True)
        #Historial Acciones (Archivos)
        self.historial_tabla = TablaHistorial()
        EtiquetaHistorial = QLabel("Historial de acciones recientes:")
        EtiquetaHistorial.setFont(roboto)
        layout_archivos.addWidget(EtiquetaHistorial)
        layout_archivos.addWidget(self.historial_tabla)


        #Actualizar Historial
        usuario_id = self.usuario_id
        logs = self.db.obtener_logs(usuario_id, limite=3)
        self.historial_tabla.actualizar(logs)

        self.pagina_contraseñas = QWidget()
        layout_contraseñas = QVBoxLayout(self.pagina_contraseñas)
        layout_contraseñas.addWidget(QLabel("Gestión de contraseñas"))

        self.pagina_configuracion = QWidget()
        layout_config = QVBoxLayout(self.pagina_configuracion)
        layout_config.addWidget(QLabel("Configuración"))

        self.pagina_reportes = QWidget()
        layout_reportes = QVBoxLayout(self.pagina_reportes)
        layout_reportes.addWidget(QLabel("Reportes"))

        self.stack.addWidget(self.pagina_inicio)
        self.stack.addWidget(self.pagina_archivos)
        self.stack.addWidget(self.pagina_contraseñas)
        self.stack.addWidget(self.pagina_reportes)
        self.stack.addWidget(self.pagina_configuracion)

        tabla = TablaHistorial()

        # Navegación
        boton_inicio.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_inicio))
        tabla.actualizar(logs)
        archivos = self.db.obtener_archivos_usuario(usuario_id)
        print(archivos)
        tabla.actualizar_archivos(archivos)

        boton_archivos.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_archivos))
        boton_contraseñas.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_contraseñas))
        boton_configuracion.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_configuracion))
        boton_reports.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_reportes))

        boton_cifrar.clicked.connect(lambda: self.mostrar_ventana_cifrado())
        boton_descifrar.clicked.connect(lambda: self.mostrar_ventana_descifrado())


        layout_principal.addWidget(menu_lateral, 1)
        layout_principal.addWidget(self.stack, 4)

    def fuentes_personalizadas(self, ruta_ttf: str, tamaño: int, negrita: bool):
        font_id = QFontDatabase.addApplicationFont(ruta_ttf)
        if font_id == -1:
            print("Error", "No se ha podido cargar la fuente.")
        else:
            familia = QFontDatabase.applicationFontFamilies(font_id)[0]
            peso = QFont.Bold if negrita else QFont.Normal
            fuente = QFont(familia, tamaño, peso)
            return fuente

    def mostrar_ventana_cifrado(self):
        dialogo = QDialog(self)
        dialogo.setWindowTitle("Autenticación requerida")
        dialogo.setFixedSize(400, 250)
        dialogo.setStyleSheet("background-color: white; border-radius: 10px;")
        layout = QVBoxLayout(dialogo)
        layout.addWidget(self.interfazINC(dialogo))
        dialogo.exec()

    def mostrar_ventana_descifrado(self):
        dialogo = QDialog(self)
        dialogo.setWindowTitle("Autenticación requerida")
        dialogo.setFixedSize(400, 250)
        dialogo.setStyleSheet("background-color: white; border-radius: 10px;")
        layout = QVBoxLayout(dialogo)
        layout.addWidget(self.interfazDES(dialogo))
        dialogo.exec()

    def interfazINC(self, parent):
        widget = QWidget(parent)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(15)

        EtiquetaContraseña = QLabel("Introduce tu contraseña:")
        Entradacontraseña = QLineEdit()
        Entradacontraseña.setEchoMode(QLineEdit.Password)
        BotonCifrar = QPushButton("Cifrar")
        BotonCifrar.clicked.connect(lambda: self.cifrar_archivo_gui(Entradacontraseña))
        BotonVolver = QPushButton("Volver")
        BotonVolver.clicked.connect(self.close)
        botonMostrar = QPushButton("Mostrar / Ocultar")
        botonMostrar.clicked.connect(lambda: self.mostrar(Entradacontraseña))

        fuente_roboto_light = self.fuentes_personalizadas("Fuentes/Roboto_Condensed-Light.ttf", 11, False)
        fuente_roboto_normal = self.fuentes_personalizadas("Fuentes/Roboto_Condensed-Regular.ttf", 10, True)

        EtiquetaContraseña.setFont(fuente_roboto_light)
        botonMostrar.setFont(fuente_roboto_normal)
        BotonCifrar.setFont(fuente_roboto_normal)
        BotonVolver.setFont(fuente_roboto_normal)

        BotonVolver.setStyleSheet("""
            QPushButton {
                background-color: #0F6CBD;
                color: white;
                border: 2px solid #0F6CBD;
                border-radius: 3px;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #0C5AA5;
            }
            QPushButton:pressed {
                background-color: #09497D;
            }
        """)

        EtiquetaContraseña.setAlignment(Qt.AlignHCenter)

        layout.addStretch(1)
        layout.addWidget(EtiquetaContraseña)
        layout.addWidget(Entradacontraseña)
        layout.addWidget(botonMostrar)
        layout.addWidget(BotonCifrar)
        layout.addWidget(BotonVolver)
        layout.addStretch(2)

        return widget

    def interfazDES(self, parent):
        widget = QWidget(parent)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(15)

        EtiquetaContraseña = QLabel("Introduce tu contraseña:")
        Entradacontraseña = QLineEdit()
        Entradacontraseña.setEchoMode(QLineEdit.Password)
        BotonCifrar = QPushButton("Descifrar")
        BotonCifrar.clicked.connect(lambda: self.descifrar_archivo_gui(Entradacontraseña))
        BotonVolver = QPushButton("Volver")
        BotonVolver.clicked.connect(self.close)
        botonMostrar = QPushButton("Mostrar / Ocultar")
        botonMostrar.clicked.connect(lambda: self.mostrar(Entradacontraseña))

        fuente_roboto_light = self.fuentes_personalizadas("Fuentes/Roboto_Condensed-Light.ttf", 11, False)
        fuente_roboto_normal = self.fuentes_personalizadas("Fuentes/Roboto_Condensed-Regular.ttf", 10, True)

        EtiquetaContraseña.setFont(fuente_roboto_light)
        botonMostrar.setFont(fuente_roboto_normal)
        BotonCifrar.setFont(fuente_roboto_normal)
        BotonVolver.setFont(fuente_roboto_normal)

        BotonVolver.setStyleSheet("""
            QPushButton {
                background-color: #0F6CBD;
                color: white;
                border: 2px solid #0F6CBD;
                border-radius: 3px;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #0C5AA5;
            }
            QPushButton:pressed {
                background-color: #09497D;
            }
        """)

        EtiquetaContraseña.setAlignment(Qt.AlignHCenter)

        layout.addStretch(1)
        layout.addWidget(EtiquetaContraseña)
        layout.addWidget(Entradacontraseña)
        layout.addWidget(botonMostrar)
        layout.addWidget(BotonCifrar)
        layout.addWidget(BotonVolver)
        layout.addStretch(2)

        return widget

    def cifrar_archivo_gui(self, entradaContraseña):
        resultado = self.db.comprobarUsuario_hash_clave(self.usuario)
        EntradaContraseña = entradaContraseña.text()

        if resultado:
            Hash, intentos, ultimoIntento = resultado
            try:
                if self.sec.hash_verify(Hash, EntradaContraseña):
                    ruta_archivo, _ = QFileDialog.getOpenFileName(self, "Selecciona un archivo a cifrar")
                    if ruta_archivo:
                        try:
                            cif = cifrador(self.contraseña, self.salt)
                            ruta_cifrado = cif.archivo_bytes(ruta_archivo)
                            msg = QMessageBox(self)
                            msg.setIcon(QMessageBox.Information)
                            msg.setWindowTitle("Cifrado")
                            msg.setText("Su archivo ha sido cifrado.")
                            msg.exec()
                        except Exception as e:
                            print(e)
                            self.label_estado_archivo.setText(f"Error al cifrar: {e}")
                else:
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Critical)
                    msg.setWindowTitle("Error de autenticación")
                    msg.setText("Contraseña incorrecta. Por favor, inténtalo de nuevo.")
                    msg.exec()
            except Exception as e:
                print("Error al verificar el hash:", e)
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText("Error interno al verificar la contraseña.")
                msg.exec()
        else:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText("Usuario no encontrado o datos corruptos.")
            msg.exec()
    
    
    def descifrar_archivo_gui(self, entradaContraseña):
        resultado = self.db.comprobarUsuario_hash_clave(self.usuario)
        EntradaContraseña = entradaContraseña.text()

        if resultado:
            Hash, intentos, ultimoIntento = resultado
            try:
                if self.sec.hash_verify(Hash, EntradaContraseña):
                    ruta_archivo, _ = QFileDialog.getOpenFileName(self, "Selecciona un archivo a cifrar")
                    if ruta_archivo:
                        try:
                            des = Descifrador(self.contraseña, self.salt)
                            ruta_cifrado = des.descifrar_clave(ruta_archivo)
                            msg = QMessageBox(self)
                            msg.setIcon(QMessageBox.Information)
                            msg.setWindowTitle("Cifrado")
                            msg.setText("Su archivo ha sido descifrado.")
                            msg.exec()
                        except Exception as e:
                            print(e)
                            self.label_estado_archivo.setText(f"Error al descifrar: {e}")
                else:
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Critical)
                    msg.setWindowTitle("Error de autenticación")
                    msg.setText("Contraseña incorrecta. Por favor, inténtalo de nuevo.")
                    msg.exec()
            except Exception as e:
                print("Error al verificar el hash:", e)
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText("Error interno al verificar la contraseña.")
                msg.exec()
        else:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText("Usuario no encontrado o datos corruptos.")
            msg.exec()

    def mostrar(self, EntradaContraseña):
        self.contadorMostrar += 1
        if self.contadorMostrar % 2:
            EntradaContraseña.setEchoMode(QLineEdit.Normal)
        else:
            EntradaContraseña.setEchoMode(QLineEdit.Password)

  