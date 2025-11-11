class Especialidad:
    def __init__(self, id_especialidad=None, nombre=None, descripcion=None):
        self.id_especialidad = id_especialidad # PK
        self.nombre = nombre
        self.descripcion = descripcion

    def __str__(self):
        return f"Especialidad(ID: {self.id_especialidad}, Nombre: {self.nombre})"