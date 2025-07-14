from .cifrar_archivos import cifrador
from login import DATABASE
import hashlib
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from login import usuario_actual

class Descifrador:
    def __init__(self, contraseña, salt):
        self.cif = cifrador(contraseña, salt)
        self.db = DATABASE()
        self.clave_maestra = self.cif.clave_maestra


    def descifrar_clave(self, ruta_archivo):
        usuario_id = usuario_actual.id
        if usuario_id is None:
         raise Exception("Usuario no autenticado")
        else:
         clave_maestra = self.clave_maestra
         print(f"Clave maestra:{clave_maestra}")
         nombre_archivo = os.path.basename(ruta_archivo).replace(".enc", "")
         clave_cifrada = self.db.extraer_clave_cifrada(usuario_id, nombre_archivo)
         print(f"Clave cifrada: {clave_cifrada}")
         nonce = clave_cifrada[:12]
         print(f"Nonce: {nonce}")
         clave_encriptada = clave_cifrada[12:]
         print(f"Clave encritpada: {clave_encriptada}")
         aesgcm = AESGCM(clave_maestra)
         try:
          clave_archivo = aesgcm.decrypt(nonce, clave_encriptada, None)
          self.descifrar_archivos(ruta_archivo, clave_archivo, usuario_id)
         except Exception as e:
             self.db.guardar_log(usuario_id, "Error", f"Falló el descifrado de la clave: posiblemente clave incorrecta o datos alterados.")
             raise ValueError("Falló el descifrado de la clave: posiblemente clave incorrecta o datos alterados.") from e
        
    def descifrar_archivos(self, ruta_archivo_enc:str, clave_archivo:bytes, usuario_id):
        with open(ruta_archivo_enc, "rb") as f:
            contenido = f.read()

        nonce = contenido[:12]
        datos_cifrados = contenido[12:]
        aesgcm = AESGCM(clave_archivo)
        try:
         archivo_descifrado = aesgcm.decrypt(nonce, datos_cifrados, None)
        except Exception as e:
            self.db.guardar_log(usuario_id, "Error", f"Descifrado fallido: archivo alterado o clave incorrecta.")
            raise ValueError("Descifrado fallido: archivo alterado o clave incorrecta.") from e    
        ruta_salida = ruta_archivo_enc.replace(".enc", "")
        with open(ruta_salida, "wb") as f:
           f.write(archivo_descifrado)
        self.db.guardar_log(usuario_id, "Descifrado", f"Archivo descifrado y guardado en {ruta_salida}")
        try:
         os.remove(ruta_archivo_enc)
        except Exception as e:
         self.db.guardar_log(usuario_id, "Error", f"No se pudo eliminar el archivo original: {e}")
         print(f"No se pudo eliminar el archivo original: {e}")

 
       
    
        







