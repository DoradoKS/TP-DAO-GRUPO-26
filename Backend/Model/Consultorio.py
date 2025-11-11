class Consultorio:
    def __init__(self, id_consultorio=None, descripcion=None):
        self.id_consultorio = id_consultorio # PK
        self.descripcion = descripcion

    def __str__(self):
        return f"Consultorio(ID: {self.id_consultorio}, Descripción: {self.descripcion})"