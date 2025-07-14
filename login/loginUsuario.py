from tkinter import messagebox
import time
from datetime import datetime
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHash
from .Usuarios import usuario_actual
class Inicio:
 
 def inicioDeSesion(self, entradaUsuario, entradaContraseña, db, seguridad):
     usuario_id = db.extraer_id_usuario(entradaUsuario)[0]
     if usuario_id:
        usuario_actual.iniciar_sesion(usuario_id, entradaUsuario)
      
        resultado = db.comprobarUsuario_hash_clave(entradaUsuario)
        contraseña = entradaContraseña.text()
        if resultado:
         Hash, intentos, ultimoIntento = resultado
         ahora = time.time()
        if intentos >= 3 and ahora - (ultimoIntento or 0) < 30:
           return {"status": "error", "mensaje": "Demasiados intentos. Espera 30 segundos."}
        try:
          if seguridad.hash_verify(Hash, contraseña):
            db.reseteo_intentos(entradaUsuario)
            return {"status": "ok"}
          else:
            print(usuario_id)
            self.registrarFallo(usuario_id, "Contraseña incorrecta", db)
            intentos += 1
            db.bloqueador(usuario_id, intentos, ahora)
            return {"status": "error", "mensaje": "Contraseña incorrecta."}
          
        except VerifyMismatchError:
            self.registrarFallo(usuario_id, "Contraseña incorrecta", db)
            intentos += 1
            db.bloqueador(entradaUsuario, intentos, ahora)
            return {"status": "error", "mensaje": "Contraseña incorrecta."}
        except InvalidHash:
           self.registrarFallo(usuario_id, "Hash invalido", db)
           return {"status": "error", "mensaje": "El hash almacenado no es válido."}

        except VerificationError:
           self.registrarFallo(usuario_id, "Error de verificacion general", db)
           return {"status": "error", "mensaje": "Error al verificar la contraseña."}
     else:
         return {"status": "error", "mensaje": "El usuario no existe."}



 def registrarFallo(self, usuario, motivo, db):
   ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
   db.registro_fallos(usuario, ahora, motivo)