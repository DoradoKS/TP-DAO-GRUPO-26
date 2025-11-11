class Estado:
    def __init__(self, id_estado=None, nombre=None):
        self.id_estado = id_estado # PK
        self.nombre = nombre

    def __str__(self):
        return f"Estado(ID: {self.id_estado}, Nombre: {self.nombre})"