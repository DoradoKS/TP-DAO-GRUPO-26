# En Model/Medico.py

class Medico:
    def __init__(self, id_medico=None, usuario=None, matricula=None, nombre=None, apellido=None, 
                 tipo_dni=None, dni=None, calle=None, numero_calle=None, email=None, telefono=None, 
                 id_especialidad=None):
        
        # Campos de la tabla
        self.id_medico = id_medico
        self.usuario = usuario
        self.matricula = matricula
        self.nombre = nombre
        self.apellido = apellido
        self.tipo_dni = tipo_dni
        self.dni = dni
        self.calle = calle
        self.numero_calle = numero_calle
        self.email = email
        self.telefono = telefono
        self.id_especialidad = id_especialidad
        
        # Puedes agregar esto después si quieres
        # self.especialidad_obj = None 

    def __str__(self):
        # Un __str__ útil para las pruebas
        return (f"Medico(ID: {self.id_medico}, Nombre: {self.nombre} {self.apellido}, "
                f"Matrícula: {self.matricula}, Especialidad: {self.id_especialidad})")