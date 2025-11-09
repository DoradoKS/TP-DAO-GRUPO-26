class Barrio:
    def __init__(self, id_barrio=None, nombre=None):
        self.id_barrio = id_barrio # PK
        self.nombre = nombre

    def __str__(self):
        return f"Barrio(ID: {self.id_barrio}, Nombre: {self.nombre})"