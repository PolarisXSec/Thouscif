from argon2 import PasswordHasher
import pyotp
import re
import qrcode
import io
import os
from cryptography.fernet import Fernet
import time
from tkinter import messagebox

print("Actualizado")

class security:
    def __init__(self):
        self.ph = PasswordHasher()


    def contraseña_segura(self, EntradaContraseña):
         patron = r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$'
         return re.match(patron, EntradaContraseña) is not None
        
    def hash(self, contraseña):
      hash = self.ph.hash(contraseña)
      return hash
    
    def hash_verify(self, hash, contraseña):
      try:
       return self.ph.verify(hash, contraseña)
      except:
        return False

    def capa_2fa_registro(self, usuario):
        nombreApp = "VaultCifrado"
        secreto = pyotp.random_base32()
        uri = pyotp.totp.TOTP(secreto).provisioning_uri(name=usuario, issuer_name=nombreApp)
        return uri, secreto
    
    def cifrado_clave_2fa(self, secreto):
        if not os.path.exists("claveMaestra.key"):
         clave = Fernet.generate_key()
         with open("claveMaestra.key", "wb") as file:
          file.write(clave)
        else:
         with open("claveMaestra.key", "rb") as file:
          clave = file.read()

        fernet = Fernet(clave)
        secretoCifrado = fernet.encrypt(secreto.encode())
        return secretoCifrado
    
    def salt_generator():
       salt = os.urandom(16)
       return salt
    
    def verify_2fa(self, codigoIntroducido: str, usuario: str, db):
     ahora = time.time()
     with open ("claveMaestra.key", "rb") as file:
             clave = file.read()
             fernet = Fernet(clave)

     resultado = db.verify_2FA(usuario)
     secretoCifrado, intentos2FA, ultimoIntento = resultado
     secretoDescifrado = fernet.decrypt(secretoCifrado).decode()
     totp = pyotp.TOTP(secretoDescifrado)


     if intentos2FA >= 3 and ahora - (ultimoIntento or 0) < 30:
        return {"status": "error", "mensaje": "Demasiados intentos. Espera 30 segundos."}, None
     else:
      if totp.verify(codigoIntroducido):
        salt = db.extract_salt(usuario)
        db.reseteo_intentos2FA(usuario)
        return {"status": "ok"}, salt[0]
      else:
       intentos2FA += 1
       db.bloquear_2FA(intentos2FA, ahora, usuario)
       return {"status": "error", "mensaje": "Código incorrecto."}, None
