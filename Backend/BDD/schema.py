# Contiene el esquema de la base de datos para una inicialización consistente.

SQL_CREAR_TABLA_USUARIO = """
CREATE TABLE IF NOT EXISTS Usuario (
    usuario TEXT PRIMARY KEY,
    contrasenia TEXT NOT NULL,
    rol TEXT NOT NULL
);
"""

SQL_CREAR_TABLA_PACIENTE = """
CREATE TABLE IF NOT EXISTS Paciente (
    id_paciente INTEGER PRIMARY KEY AUTOINCREMENT,
    id_barrio INTEGER,
    usuario TEXT UNIQUE,
    nombre TEXT,
    apellido TEXT,
    fecha_nacimiento DATE,
    tipo_dni TEXT,
    dni TEXT UNIQUE,
    email TEXT,
    telefono TEXT,
    id_obra_social INTEGER,
    calle TEXT,
    numero_calle INTEGER,
    FOREIGN KEY (usuario) REFERENCES Usuario(usuario)
);
"""

SQL_CREAR_TABLA_ESPECIALIDAD = """
CREATE TABLE IF NOT EXISTS Especialidad (
    id_especialidad INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    descripcion TEXT
);
"""

SQL_CREAR_TABLA_MEDICO = """
CREATE TABLE IF NOT EXISTS Medico (
    id_medico INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE,
    matricula TEXT UNIQUE,
    nombre TEXT,
    apellido TEXT,
    tipo_dni TEXT,
    dni TEXT UNIQUE,
    calle TEXT,
    numero_calle INTEGER,
    email TEXT,
    telefono TEXT,
    id_especialidad INTEGER,
    FOREIGN KEY (usuario) REFERENCES Usuario(usuario),
    FOREIGN KEY (id_especialidad) REFERENCES Especialidad(id_especialidad)
);
"""

SQL_CREAR_TABLA_TURNO = """
CREATE TABLE IF NOT EXISTS Turno (
    id_turno INTEGER PRIMARY KEY AUTOINCREMENT,
    id_paciente INTEGER NOT NULL,
    id_medico INTEGER NOT NULL,
    fecha_hora DATETIME NOT NULL,
    motivo TEXT,
    FOREIGN KEY (id_paciente) REFERENCES Paciente(id_paciente),
    FOREIGN KEY (id_medico) REFERENCES Medico(id_medico)
);
"""

# Lista de todas las sentencias de creación de tablas
SENTENCIAS_CREACION = [
    SQL_CREAR_TABLA_USUARIO,
    SQL_CREAR_TABLA_ESPECIALIDAD,
    SQL_CREAR_TABLA_PACIENTE,
    SQL_CREAR_TABLA_MEDICO,
    SQL_CREAR_TABLA_TURNO
]
