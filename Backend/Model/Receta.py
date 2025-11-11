class Receta:
    def __init__(self, id_receta=None, id_paciente=None, id_medico=None, id_estado=None,
                 fecha=None, descripcion=None):
        self.id_receta = id_receta      # PK
        self.id_paciente = id_paciente  # FK a Paciente
        self.id_medico = id_medico      # FK a Medico
        self.id_estado = id_estado      # FK a Estado (ej: 'Vigente', 'Vencida')
        self.fecha = fecha
        self.descripcion = descripcion # Detalle de los medicamentos

    def __str__(self):
        return (f"Receta(ID: {self.id_receta}, Paciente ID: {self.id_paciente}, "
                f"Fecha: {self.fecha})")