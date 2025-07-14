import sqlite3
print("Actualizado db")
from datetime import datetime

class DATABASE:
    def __init__(self):
        self.baseDeDatos = sqlite3.connect("usuarios.db")
        self.cursor = self.baseDeDatos.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON")
        self.crearTabla()
    
    def crearTabla(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS contraseñas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT NOT NULL,
        contraseña TEXT NOT NULL,
        intentos2FA INTEGER DEFAULT 0,
        ultimoIntento2FA REAL,
        intentos_fallidos INTEGER DEFAULT 0,
        ultimo_intento REAL,
        totpSecret BLOB,
        salt BLOB NOT NULL
                            )
                            """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS intentos_fallidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        fecha_hora TEXT,
        motivo TEXT,
        FOREIGN KEY (usuario_id) REFERENCES contraseñas(id)
            ON DELETE CASCADE
                            )
                            """)
        

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS archivos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        nombre_original TEXT NOT NULL,
        clave_cifrada BLOB NOT NULL,
        ruta_archivos TEXT,
        fecha_subida TEXT DEFAULT CURRENT_TIMESTAMP,
        tamaño INTEGER,
        mime_type TEXT,
        FOREIGN KEY (usuario_id) REFERENCES contraseñas(id)
            ON DELETE CASCADE
                            )
                            """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial_archivos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        nombre_original TEXT NOT NULL,
        clave_cifrada BLOB NOT NULL,
        ruta_archivos TEXT,
        fecha_subida TEXT DEFAULT CURRENT_TIMESTAMP,
        tamaño INTEGER,
        mime_type TEXT,
        FOREIGN KEY (usuario_id) REFERENCES contraseñas(id)
            ON DELETE CASCADE
                            )
                            """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        tipo TEXT,
        mensaje TEXT,
        timestamp TEXT,
        FOREIGN KEY (usuario_id) REFERENCES contraseñas(id)
            ON DELETE CASCADE
                            )
                            """)
        self.baseDeDatos.commit()




    
    
    def usuario_existente(self, usuario):
        self.cursor.execute("SELECT 1 FROM contraseñas WHERE usuario = ?", (usuario,))
        resultado = self.cursor.fetchone()
        return resultado is not None

    def insertarUsuario_hash_clave(self, usuario, hash, secreto, salt):
        self.cursor.execute("INSERT INTO contraseñas (usuario, contraseña, totpSecret, salt) VALUES (?,?,?,?)", (usuario, hash, secreto, salt))
        self.baseDeDatos.commit()

    def comprobarUsuario_hash_clave(self, usuario):
        self.cursor.execute("SELECT contraseña, intentos_fallidos, ultimo_intento FROM contraseñas WHERE usuario = ?", (usuario,))
        resultado = self.cursor.fetchone()
        return resultado
    
    def reseteo_intentos(self, usuario):
        self.cursor.execute("UPDATE contraseñas SET intentos_fallidos = 0 WHERE usuario = ?", (usuario,))
        self.baseDeDatos.commit()

    def reseteo_intentos2FA(self, usuario):
        self.cursor.execute("UPDATE contraseñas SET intentos2FA = 0 WHERE usuario = ?", (usuario,))
        self.baseDeDatos.commit()

    def bloqueador(self, usuario, intentos, ahora):
                self.cursor.execute("UPDATE contraseñas SET intentos_fallidos = ?, ultimo_intento = ? WHERE usuario = ?",
                    (intentos, ahora, usuario))
                self.baseDeDatos.commit()

    def registro_fallos(self, usuario, ahora, motivo):
            self.cursor.execute("INSERT INTO intentos_fallidos (usuario_id, fecha_hora, motivo) VALUES (?,?,?)",
                  (usuario, ahora, motivo))
            self.baseDeDatos.commit()

    def verify_2FA(self, usuario):
         self.cursor.execute("SELECT totpSecret, intentos2FA, ultimoIntento2FA FROM contraseñas WHERE usuario = ? ", (usuario,))
         resultado = self.cursor.fetchone()
         return resultado
    

    def bloquear_2FA(self, intentos2FA, ahora, EntradaUsuario):
           self.cursor.execute("UPDATE contraseñas SET intentos2FA = ?, ultimoIntento2FA = ? WHERE usuario = ?",
                     (intentos2FA, ahora, EntradaUsuario))
           self.baseDeDatos.commit()


    def cerrar_datos(self):
         self.baseDeDatos.close()

    def extract_salt(self, usuario):
         self.cursor.execute("SELECT salt FROM contraseñas WHERE usuario = ? ", (usuario,))
         resultado = self.cursor.fetchone()
         return resultado
    
    def extraer_id_usuario(self, usuario):
         self.cursor.execute("SELECT id FROM contraseñas WHERE usuario = ? ", (usuario,))
         resultado = self.cursor.fetchone()
         return resultado
         
         
    def guardar_clave_cifrada(self, usuario_id, nombre_archivo, clave_cifrada, ruta_archivo):
        self.cursor.execute("INSERT INTO archivos (usuario_id, nombre_original, clave_cifrada, ruta_archivos) VALUES (?,?,?,?)", (usuario_id, nombre_archivo, clave_cifrada, ruta_archivo))
        self.baseDeDatos.commit()

    def guardar_clave_cifrada_historial(self, usuario_id, nombre_archivo, clave_cifrada, ruta_archivo):
        self.cursor.execute("INSERT INTO historial_archivos (usuario_id, nombre_original, clave_cifrada, ruta_archivos) VALUES (?,?,?,?)", (usuario_id, nombre_archivo, clave_cifrada, ruta_archivo))
        self.baseDeDatos.commit()


    def extraer_clave_cifrada(self, usuario_id, nombre_archivo):
        self.cursor.execute("SELECT clave_cifrada FROM archivos WHERE usuario_id = ? AND nombre_original = ?", (usuario_id, nombre_archivo))
        resultado = self.cursor.fetchone()
        return resultado[0]
    

    def guardar_log(self, usuario_id, tipo, mensaje):
         timestamp = datetime.utcnow().isoformat()
         self.cursor.execute("INSERT INTO logs (usuario_id, tipo, mensaje, timestamp) VALUES (?,?,?,?)",
                             (usuario_id, tipo, mensaje, timestamp))
         self.baseDeDatos.commit()

    def obtener_logs(self, usuario_id, limite = 3):
         self.cursor.execute("SELECT tipo, mensaje, timestamp FROM logs WHERE usuario_id = ? ORDER BY id DESC LIMIT ?",
                             (usuario_id, limite))
         return self.cursor.fetchall()
    
    def eliminar_archivos_repetidos(self, usuario_id):
         self.cursor.execute("SELECT nombre_original FROM archivos WHERE usuario_id = ? GROUP BY nombre_original HAVING COUNT(*) > 1",
                             (usuario_id,))
         archivos_repetidos = self.cursor.fetchall()
         
         for (nombre_original,) in archivos_repetidos:
          self.cursor.execute("SELECT id FROM archivos WHERE usuario_id = ? AND nombre_original = ? ORDER BY id DESC LIMIT 1",
                              (usuario_id, nombre_original))
          id_reciente = self.cursor.fetchone()[0]

          self.cursor.execute("DELETE FROM archivos WHERE usuario_id = ? AND nombre_original = ? AND id != ?",
                              (usuario_id, nombre_original, id_reciente))
          self.baseDeDatos.commit()

    def obtener_archivos_usuario(self, usuario_id, limite=5):
     self.cursor.execute(
        "SELECT nombre_original FROM archivos WHERE usuario_id = ? ORDER BY id DESC LIMIT ?",
        (usuario_id, limite)
     )
     return [fila[0] for fila in self.cursor.fetchall()]
