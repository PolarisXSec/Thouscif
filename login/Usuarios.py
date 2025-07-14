






class UsuarioSesion:
    def __init__(self):
        self.id = None
        self.usuario = None


    def iniciar_sesion(self, id_usuario, nombre_usuario):
        self.id = id_usuario
        self.usuario = nombre_usuario

    def cerrar_sesion(self):
        self.id = None
        self.usuario = None

usuario_actual = UsuarioSesion()
    
