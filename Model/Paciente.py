class Paciente:
    def __init__(self, id_paciente=None, id_barrio=None, id_obra_social=None, usuario=None,
                 nombre=None, apellido=None, fecha_nacimiento=None, tipo_dni=None,
                 dni=None, email=None, telefono=None, calle=None, numero_calle=None):
        
        # Claves Primarias y Foráneas (FK)
        self.id_paciente = id_paciente      # PK
        self.id_barrio = id_barrio          # FK a Barrio
        self.id_obra_social = id_obra_social # FK a ObraSocial
        self.usuario = usuario              # FK a Usuario (que es el nombre de usuario)
        self.tipo_dni = tipo_dni            # FK a TipoDni
        
        # Atributos Propios
        self.nombre = nombre
        self.apellido = apellido
        self.fecha_nacimiento = fecha_nacimiento
        self.dni = dni
        self.email = email
        self.telefono = telefono
        self.calle = calle
        self.numero_calle = numero_calle

    def __str__(self):
        return (f"Paciente(ID: {self.id_paciente}, Nombre: {self.nombre} {self.apellido}, DNI: {self.dni}, "
                f"Usuario: {self.usuario}, Obra Social: {self.id_obra_social})")