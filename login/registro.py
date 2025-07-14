from .databaseVault import DATABASE
from tkinter import messagebox
import re
from .seguridad import security
from .Usuarios import usuario_actual
print("Actualizado")


class registroUsuario:



 
   
 def registro(self, entradaUsuario, entradaContraseña, db, seguridad, secreto_2FA):
    EntradaUsuario = entradaUsuario.text()
    EntradaContraseña = entradaContraseña.text()
    if db.usuario_existente(EntradaUsuario):
        return {"status": "error", "mensaje": "Ese nombre de usuario ya existe"}
    else:
       if not seguridad.contraseña_segura(EntradaContraseña):
         return {"status": "error", "mensaje": "La contraseña no cumple los requisitos"}
       #CIFRADO CONTRASEÑA
       hash = seguridad.hash(EntradaContraseña)
        #CIFRADO CLAVE 2FA
       secretoCifrado = seguridad.cifrado_clave_2fa(secreto_2FA)
       #GENERAR SALT PARA CLAVE MAESTRA
       salt = security.salt_generator()
        #GUARDADO EN BASE DE DATOS
       db.insertarUsuario_hash_clave(EntradaUsuario, hash, secretoCifrado, salt)
       id_usuario = db.extraer_id_usuario(EntradaUsuario)
       if id_usuario:
          usuario_actual.iniciar_sesion(id_usuario, EntradaUsuario)
          return {"status": "ok"}
       else:
          return {"status": "error", "mensaje": "Error al autentificar"}
       
       





