class Historial:
    def __init__(self, id_historial=None, id_paciente=None, id_medico=None, 
                 fecha=None, diagnostico=None, observaciones=None):
        self.id_historial = id_historial # PK
        self.id_paciente = id_paciente   # FK a Paciente
        self.id_medico = id_medico       # FK a Medico
        self.fecha = fecha
        self.diagnostico = diagnostico
        self.observaciones = observaciones

    def __str__(self):
        return (f"Historial(ID: {self.id_historial}, Paciente ID: {self.id_paciente}, "
                f"Médico ID: {self.id_medico}, Fecha: {self.fecha})")