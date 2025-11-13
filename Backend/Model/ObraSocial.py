class ObraSocial:
    def __init__(self, nombre, id_obra_social=None):
        self.id_obra_social = id_obra_social
        self.nombre = nombre
    
    def __str__(self):
        return f"ObraSocial(ID: {self.id_obra_social}, Nombre: {self.nombre})"
