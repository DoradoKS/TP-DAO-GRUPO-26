class Usuario:
    def __init__(self, usuario=None, contrasenia=None, rol=None):
        self.usuario = usuario          # PK (Usado como FK en Paciente y Medico)
        self.contrasenia = contrasenia  # Varchar NN
        self.rol = rol                  # Varchar NN (Ej: 'Paciente', 'Medico', 'Administrador')

    def __str__(self):
        return f"Usuario(Usuario: {self.usuario}, Rol: {self.rol})"