# Backend/Model/FranjaHoraria.py

class FranjaHoraria:
    """
    Representa el Modelo de una franja horaria laboral de un médico.
    """
    def __init__(self, id_franja=None, id_medico=None, dia_semana=None, 
                 hora_inicio=None, hora_fin=None):
        self.id_franja = id_franja
        self.id_medico = id_medico
        self.dia_semana = dia_semana
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin

    def __str__(self):
        return (f"Franja(ID: {self.id_franja}, Médico: {self.id_medico}, "
                f"Día: {self.dia_semana}, De: {self.hora_inicio} a {self.hora_fin})")