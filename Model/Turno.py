class Turno:
    def __init__(self, id_turno=None, id_paciente=None, id_medico=None, id_consultorio=None,
                 id_estado=None, fecha_inicio=None, hora_inicio=None, hora_fin=None, 
                 observaciones=None):
        
        # Claves Primarias y Foráneas (FK)
        self.id_turno = id_turno            # PK
        self.id_paciente = id_paciente      # FK a Paciente
        self.id_medico = id_medico          # FK a Medico
        self.id_consultorio = id_consultorio # FK a Consultorio
        self.id_estado = id_estado          # FK a Estado

        # Atributos Propios
        self.fecha_inicio = fecha_inicio    # DATE NN (fecha del turno)
        self.hora_inicio = hora_inicio      # TIME NN (hora de inicio del turno)
        self.hora_fin = hora_fin            # TIME NN (hora de fin del turno)
        self.observaciones = observaciones

    def __str__(self):
        return (f"Turno(ID: {self.id_turno}, Fecha: {self.fecha_inicio} {self.hora_inicio}, "
                f"Médico ID: {self.id_medico}, Paciente ID: {self.id_paciente}, Estado ID: {self.id_estado})")