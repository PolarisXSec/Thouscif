print("🟢 GUI.PY ACTUALIZADO")


import tkinter
from tkinter import messagebox
import tkinter as tk
from PIL import Image, ImageTk
import qrcode
import io
import random
import string
from login import Inicio, security, registroUsuario, DATABASE
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QLabel, QVBoxLayout, QStackedWidget, QMessageBox, QDialog
from PySide6.QtGui import QPixmap, QFont, QFontDatabase     
from PySide6.QtCore import Qt
from PIL.ImageQt import ImageQt
import sys
from vault_app import cifrador
from vault_app import Descifrador
from .GUI_app import MainWindow
class Acceso: 


 def __init__(self):
     self.seguridad = security()
     self.db = DATABASE()
     self.login = Inicio()
     self.registro = registroUsuario()

     self.contadorMostrar = 0
     self.app = QApplication(sys.argv)
     self.ventana = QWidget()
     self.stack = QStackedWidget()
     layout = QVBoxLayout()
     self.ventana.setLayout(layout)
     layout.addWidget(self.stack)
     self.ventana.setWindowTitle("Login")
     self.ventana.resize(400, 200)
     self.set_up()
     self.ventana.show()
     self.app.exec()


 def set_up(self):
    self.pantalla_menu = self.menu()
    self.pantalla_usuario = self.interfazREG()
    self.pantalla_inicio = self.interfazINC()
    self.stack.addWidget(self.pantalla_menu)
    self.stack.addWidget(self.pantalla_usuario)
    self.stack.addWidget(self.pantalla_inicio)


 def menu(self):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    botonRegistro = QPushButton("Crear una cuenta")
    botonRegistro.clicked.connect(self.pasar_pagina_registro)
    botonInicio = QPushButton("Iniciar sesión")
    botonInicio.clicked.connect(self.pasar_pagina_inicio)
    botonSalir = QPushButton("Salir")
    botonSalir.setStyleSheet("""
    QPushButton {
        background-color: #0F6CBD;
        color: white;
        border: 2px solid #0F6CBD;
        border-radius: 5px;
        padding: 2px;
    }
    QPushButton:hover {
        background-color: #0C5AA5;
    }
    QPushButton:pressed {
        background-color: #09497D;
    }
""")

    botonSalir.clicked.connect(self.ventana.close)
    fuente_roboto_normal = self.fuentes_personalizadas("Fuentes/Roboto_Condensed-Regular.ttf", 10, True)
    botonInicio.setFont(fuente_roboto_normal)
    botonRegistro.setFont(fuente_roboto_normal)
    botonSalir.setFont(fuente_roboto_normal)
    layout.addWidget(botonRegistro)
    layout.addWidget(botonInicio)
    layout.addWidget(botonSalir)
    return widget


 def interfazREG(self):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    #AJUSTAR MARGENES
    layout.setContentsMargins(40, 30, 40, 30)
    layout.setSpacing(15)
    #CREAR WIDGETS
    EtiquetaUsuario = QLabel("Introduce un nombre de usuario:")
    EntradaUsuario =  QLineEdit()
    EtiquetaContraseña = QLabel("Introduce una contraseña:")
    Entradacontraseña = QLineEdit()
    Entradacontraseña.setEchoMode(QLineEdit.Password)
    BotonRegistro = QPushButton("Registro")
    BotonRegistro.clicked.connect(lambda:self.realizar_registro(EntradaUsuario, Entradacontraseña, self.db, self.seguridad ))
    BotonVolver = QPushButton("Volver")
    BotonVolver.clicked.connect(self.retroceder_pagina)
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
    botonContraseñaSegura = QPushButton("Contraseña segura")
    botonContraseñaSegura.clicked.connect(lambda:self.contraseñaSegura(Entradacontraseña))
    botonMostrar = QPushButton("Mostrar / Oculatar")
    botonMostrar.clicked.connect(lambda:self.mostrar(Entradacontraseña))
    #FUENTES
    fuente_roboto_light = self.fuentes_personalizadas("Fuentes/Roboto_Condensed-Light.ttf", 11, False)
    fuente_roboto_normal = self.fuentes_personalizadas("Fuentes/Roboto_Condensed-Regular.ttf", 10, True)
    EtiquetaUsuario.setFont(fuente_roboto_light)
    EtiquetaContraseña.setFont(fuente_roboto_light)
    botonMostrar.setFont(fuente_roboto_normal)
    BotonRegistro.setFont(fuente_roboto_normal)
    botonContraseñaSegura.setFont(fuente_roboto_normal)
    BotonVolver.setFont(fuente_roboto_normal)
    #ALINEACIONES
    EtiquetaUsuario.setAlignment(Qt.AlignHCenter)
    EtiquetaContraseña.setAlignment(Qt.AlignHCenter)
    #ESPACIO ARRIBA
    layout.addStretch(1)
    layout.addWidget(EtiquetaUsuario)
    layout.addWidget(EntradaUsuario)
    layout.addWidget(EtiquetaContraseña)
    layout.addWidget(Entradacontraseña)
    layout.addWidget(botonMostrar)
    layout.addWidget(botonContraseñaSegura)
    layout.addWidget(BotonRegistro)
    layout.addWidget(BotonVolver)
    #ESPACIO ABAJO
    layout.addStretch(2)
    return widget

 def realizar_registro(self, entradaUsuario, entradaContraseña, db, seguridad):
    usuario = entradaUsuario.text()
    uri, secreto = self.seguridad.capa_2fa_registro(usuario)
    self.secreto_2FA_temporal = secreto
    resultado = self.registro.registro(entradaUsuario, entradaContraseña, self.db, self.seguridad, secreto)
    if resultado["status"] == "ok":
       messagebox.showinfo("REGISTRO", "Usuario registrado.")
       self.ventana_2fa_qr(uri)
    else:
       if resultado["mensaje"] == "Ese nombre de usuario ya existe":
          messagebox.showerror("ERROR", "Ese nombre de usuario ya existe")
       if resultado["mensaje"] == "Error al autentificar":
          messagebox.showerror("ERROR", "Error al autentificar")
       else:
        messagebox.showerror("ERROR", "La contraseña debe tener:\n"
                              "- Una letra mayúscula\n"
                              "- Una letra minúscula\n"
                              "- Un símbolo especial\n"
                              "- Un número\n"
                              "- Mínimo 8 caracteres")
          
       

 def interfazINC(self):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    #AJUSTAR MARGENES
    layout.setContentsMargins(40, 30, 40, 30)
    layout.setSpacing(15)
    #CREAR WIDGETS
    EtiquetaUsuario = QLabel("Introduce tu nombre de usuario:")
    EntradaUsuario =  QLineEdit()
    EtiquetaContraseña = QLabel("Introduce tu contraseña:")
    Entradacontraseña = QLineEdit()
    Entradacontraseña.setEchoMode(QLineEdit.Password)
    BotonInicio = QPushButton("Iniciar sesion")
    BotonInicio.clicked.connect(lambda:self.realizar_inicio(EntradaUsuario, Entradacontraseña, self.db, self.seguridad))
    BotonVolver = QPushButton("Volver")
    BotonVolver.clicked.connect(self.retroceder_pagina)
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
    botonMostrar = QPushButton("Mostrar / Oculatar")
    botonMostrar.clicked.connect(lambda:self.mostrar(Entradacontraseña))
    #FUENTES
    fuente_roboto_light = self.fuentes_personalizadas("Fuentes/Roboto_Condensed-Light.ttf", 11, False)
    fuente_roboto_normal = self.fuentes_personalizadas("Fuentes/Roboto_Condensed-Regular.ttf", 10, True)
    EtiquetaUsuario.setFont(fuente_roboto_light)
    EtiquetaContraseña.setFont(fuente_roboto_light)
    botonMostrar.setFont(fuente_roboto_normal)
    BotonInicio.setFont(fuente_roboto_normal)
    BotonVolver.setFont(fuente_roboto_normal)
    #ALINEACIONES
    EtiquetaUsuario.setAlignment(Qt.AlignHCenter)
    EtiquetaContraseña.setAlignment(Qt.AlignHCenter)
    #ESPACIO ARRIBA
    layout.addStretch(1)
    #AÑADIR WIDGETS
    layout.addWidget(EtiquetaUsuario)
    layout.addWidget(EntradaUsuario)
    layout.addWidget(EtiquetaContraseña)
    layout.addWidget(Entradacontraseña)
    layout.addWidget(botonMostrar)
    layout.addWidget(BotonInicio)
    layout.addWidget(BotonVolver)
    #ESPACIO ABAJO
    layout.addStretch(2)
    return widget


 def realizar_inicio(self, entradausuario, entradacontraseña, db, seguridad):
    usuario = entradausuario.text()
    resultado = self.login.inicioDeSesion(usuario, entradacontraseña, self.db, self.seguridad)
    if resultado["status"] == "ok":
        self.pantalla_2FA = self.ventana_2fa(usuario, entradacontraseña)
        self.stack.addWidget(self.pantalla_2FA)
        self.pasar_pagina_2FA()
    else:
       self.mostrar_mensaje("error", "Inicio de sesión", resultado["mensaje"])


 def mostrar_mensaje(self, tipo, titulo, mensaje):
    if tipo == "error":
        QMessageBox.critical(self.ventana, titulo, mensaje)
    elif tipo == "info":
        QMessageBox.information(self.ventana, titulo, mensaje)
    elif tipo == "warning":
        QMessageBox.warning(self.ventana, titulo, mensaje)





 def pasar_pagina_registro(self):
    self.stack.setCurrentWidget(self.pantalla_usuario)

 def pasar_pagina_inicio(self):
    self.stack.setCurrentWidget(self.pantalla_inicio)

 def retroceder_pagina(self):
    self.stack.setCurrentWidget(self.pantalla_menu)

 def pasar_pagina_2FA(self):
    self.stack.setCurrentWidget(self.pantalla_2FA)
    QMessageBox.information(self.ventana, "2FA", "Verifique su código 2FA en la aplicación de Google Authenticator.")
 
 def retroceder_pagina_inicio(self):
    self.stack.setCurrentWidget(self.pantalla_inicio)

 def prueba(self):
    texto = print("CORRECTO")
    return texto
      



 def ventana_2fa(self, EntradaUsuario, contraseña):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    #AJUSTAR MARGENES
    layout.setContentsMargins(40, 30, 40, 30)
    layout.setSpacing(15)
    #CREAR WIDGETS
    Etiqueta2FA = QLabel("Introduce tu código 2FA")
    Etiqueta2FAsub = QLabel("Utlice Google Authenticator para verificar su identidad")
    Entrada2FA =  QLineEdit()
    Entrada2FA.setEchoMode(QLineEdit.Password)
    BotonVerificar = QPushButton("Verificar")
    BotonVerificar.clicked.connect(lambda:self.verificacion2FA(Entrada2FA, EntradaUsuario, self.db, contraseña))
    BotonVolver = QPushButton("Volver")
    BotonVolver.clicked.connect(self.retroceder_pagina_inicio)
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
    #FUENTES
    fuente_roboto_light = self.fuentes_personalizadas("Fuentes/Roboto_Condensed-Light.ttf", 11, False)
    fuente_roboto_bold = self.fuentes_personalizadas("Fuentes/Roboto_Condensed-Regular.ttf", 14, True)
    fuente_roboto_normal = self.fuentes_personalizadas("Fuentes/Roboto_Condensed-Regular.ttf", 10, True)
    Etiqueta2FA.setFont(fuente_roboto_bold)
    Etiqueta2FAsub.setFont(fuente_roboto_light)
    BotonVerificar.setFont(fuente_roboto_normal)
    BotonVolver.setFont(fuente_roboto_normal)
    #ALINEACIONES
    Etiqueta2FA.setAlignment(Qt.AlignHCenter)
    Etiqueta2FAsub.setAlignment(Qt.AlignHCenter)
    #ESPACIO ARRIBA
    layout.addStretch(1)
    
    #AÑADIR WIDGETS
    layout.addWidget(Etiqueta2FA)
    layout.addWidget(Etiqueta2FAsub)
    layout.addWidget(Entrada2FA)
    layout.addWidget(BotonVerificar)
    layout.addWidget(BotonVolver)
    
    #ESPACIO ABAJO
    layout.addStretch(2)
    return widget


 def verificacion2FA(self, entrada2FA, usuario, db, contraseña):
    Contraseña = contraseña.text()
    codigo_2fa = entrada2FA.text()
    resultado, salt = self.seguridad.verify_2fa(codigo_2fa, usuario, self.db)
    if resultado["status"] == "ok":
        self.main_window = MainWindow(usuario, Contraseña, salt)
        self.main_window.show()
        self.ventana.close
        
        
        QMessageBox.information(self.ventana, "2FA Correcto", "Código 2FA verificado correctamente.")

    else:
        mensaje = resultado["mensaje"]
        if mensaje == "Demasiados intentos. Espera 30 segundos.":
            QMessageBox.critical(self.ventana, "Error 2FA", mensaje)
        elif mensaje == "Código incorrecto.":
            QMessageBox.critical(self.ventana, "Error 2FA", mensaje)
    
    




 def ventana_2fa_qr(self, uri):    
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )
    qr.add_data(uri)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    qt_img = ImageQt(qr_img)
    pixmap = QPixmap.fromImage(qt_img)

    self.qr_window = QWidget()  # ← ¡IMPORTANTE! Guardar como atributo
    self.qr_window.setWindowTitle("Escanea este QR con tu App de Autenticación")
    layout = QVBoxLayout()
    self.qr_window.setLayout(layout)

    label = QLabel()
    label.setPixmap(pixmap)
    layout.addWidget(label)

    self.qr_window.setFixedSize(pixmap.size())
    self.qr_window.show()


 def fuentes_personalizadas(self, ruta_ttf:str, tamaño:int, negrita:bool):
    font_id = QFontDatabase.addApplicationFont(ruta_ttf)
    if font_id == -1:
       print("Error", "No se ha podido cargar la fuente.")
    else:
       familia = QFontDatabase.applicationFontFamilies(font_id)[0]
       peso = QFont.Bold if negrita == True else QFont.Normal   
       fuente = QFont(familia, tamaño, peso)
       return fuente



 def contraseñaSegura(self, EntradaContraseña):
    EntradaContraseña.clear()
    longitud = random.randint(8, 14)
    diccionario = string.ascii_letters + string.digits + string.punctuation
    contraseña = "".join(random.choice(diccionario) for i in range(longitud))
    EntradaContraseña.setText(contraseña)

 def mostrar(self, EntradaContraseña):
    self.contadorMostrar += 1
    if self.contadorMostrar % 2:
      EntradaContraseña.setEchoMode(QLineEdit.Normal) 
    else:
       EntradaContraseña.setEchoMode(QLineEdit.Password)




