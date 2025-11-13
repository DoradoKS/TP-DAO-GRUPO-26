class Turno:
    def __init__(self, id_turno=None, id_paciente=None, id_medico=None, id_consultorio=None, fecha_hora=None, 
                 motivo=None, asistio=None):
        
        # Claves Primarias y Foráneas (FK)
        self.id_turno = id_turno            # PK
        self.id_paciente = id_paciente      # FK a Paciente
        self.id_medico = id_medico          # FK a Medico
        self.id_consultorio = id_consultorio  # FK a Consultorio

        # Atributos Propios
        self.fecha_hora = fecha_hora    # DATETIME NN (fecha y hora del turno)
        self.motivo = motivo
        self.asistio = asistio  # None: pendiente, 1: asistió, 0: inasistencia

    def __str__(self):
        return (f"Turno(ID: {self.id_turno}, Fecha y Hora: {self.fecha_hora}, "
            f"Médico ID: {self.id_medico}, Paciente ID: {self.id_paciente}, Consultorio ID: {self.id_consultorio})")