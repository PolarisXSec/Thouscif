import hashlib
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from login import DATABASE
from login import usuario_actual



class cifrador:

    def __init__(self, contraseña, salt):
        self.clave_maestra = self.derivar_clave(contraseña, salt)
        self.db = DATABASE()




    def derivar_clave(self, password: str, salt: bytes, iteraciones: int = 200_000, longitud: int = 32):
        clave = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt,
            iteraciones,
            dklen=longitud
        )
        return clave
    
    def test_clave_maestra(self):
        clave = print(self.clave_maestra)
        return self.clave_maestra
    

    def clave_archivos(self):
        clave = os.urandom(32)
        return clave 
    

    def cifrar_clave(self, clave):
        print(f"Clave maestra: {self.clave_maestra}")
        aescgm = AESGCM(self.clave_maestra)
        nonce = os.urandom(12)
        clave_cifrada = aescgm.encrypt(nonce, clave, None)
        return nonce + clave_cifrada



    

    def archivo_bytes(self, ruta):

        usuario_id = usuario_actual.id
        if usuario_id is None:
         raise Exception("Usuario no autenticado")
        
        else:
         with open(ruta, "rb") as f:
            datos = f.read()
        
         datos_cifrados, nonce, clave_archivo = self.cifrar_archivo(datos)
         with open(ruta + ".enc", "wb") as f:
            f.write(nonce + datos_cifrados)
         ruta_cifrado = ruta + ".enc"
         self.db.guardar_log(usuario_id, "Cifrado", f"Archivo cifrado guardado en:{ruta_cifrado}")
        try:
         os.remove(ruta)
        except Exception as e:
         self.db.guardar_log(usuario_id, "Error", f"No se pudo eliminar el archivo original:{e}")
        clave_cifrada = self.cifrar_clave(clave_archivo)
        print(f"Clave cifrada: {clave_cifrada}")
        nombre_archivo = os.path.basename(ruta)
        self.db.guardar_clave_cifrada(usuario_id, nombre_archivo, clave_cifrada, ruta_cifrado)
        self.db.guardar_clave_cifrada_historial(usuario_id, nombre_archivo, clave_cifrada, ruta_cifrado)
        self.db.eliminar_archivos_repetidos(usuario_id)
        return datos_cifrados
    
    
    
    
    def cifrar_archivo(self, datos):
        clave_archivo = self.clave_archivos()
        aesgcm = AESGCM(clave_archivo)
        nonce = os.urandom(12)
        datos_cifrados = aesgcm.encrypt(nonce, datos, None)
        return datos_cifrados, nonce, clave_archivo
    

    def descifrar_archivos(self, ruta_archivo_enc:str, clave_archivo:bytes):
        with open(ruta_archivo_enc, "rb") as f:
            contenido = f.read()

        nonce = contenido[:12]
        datos_cifrados = contenido[12:]

        aesgcm = AESGCM
    



