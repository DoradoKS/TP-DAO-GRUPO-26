class TipoDni:
    def __init__(self, tipo_dni=None, tipo=None):
        self.tipo_dni = tipo_dni # PK
        self.tipo = tipo

    def __str__(self):
        return f"TipoDni(ID: {self.tipo_dni}, Tipo: {self.tipo})"