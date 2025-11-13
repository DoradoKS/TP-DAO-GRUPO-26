import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "clinica.db"

SQL_CREAR_TABLA_USUARIO = """
CREATE TABLE IF NOT EXISTS Usuario (
    usuario TEXT PRIMARY KEY,
    contrasenia TEXT NOT NULL,
    rol TEXT NOT NULL
);
"""

SQL_CREAR_TABLA_BARRIO = """
CREATE TABLE IF NOT EXISTS Barrio (
    id_barrio INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL
);
"""

SQL_CREAR_TABLA_OBRA_SOCIAL = """
CREATE TABLE IF NOT EXISTS ObraSocial (
    id_obra_social INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL
);
"""

SQL_CREAR_TABLA_CONSULTORIO = """
CREATE TABLE IF NOT EXISTS Consultorio (
    id_consultorio INTEGER PRIMARY KEY,
    descripcion TEXT
);
"""

SQL_CREAR_TABLA_ESTADO = """
CREATE TABLE IF NOT EXISTS Estado (
    id_estado INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL
);
"""

SQL_CREAR_TABLA_PACIENTE = """
CREATE TABLE IF NOT EXISTS Paciente (
    id_paciente INTEGER PRIMARY KEY AUTOINCREMENT,
    id_barrio INTEGER NOT NULL,
    usuario TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    tipo_dni TEXT NOT NULL, -- Cambiado a TEXT
    dni TEXT NOT NULL,
    email TEXT NOT NULL,
    telefono TEXT,
    id_obra_social INTEGER,
    calle TEXT,
    numero_calle INTEGER,
    UNIQUE(tipo_dni, dni),
    FOREIGN KEY (usuario) REFERENCES Usuario(usuario),
    FOREIGN KEY (id_barrio) REFERENCES Barrio(id_barrio),
    FOREIGN KEY (id_obra_social) REFERENCES ObraSocial(id_obra_social)
);
"""

SQL_CREAR_TABLA_ESPECIALIDAD = """
CREATE TABLE IF NOT EXISTS Especialidad (
    id_especialidad INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    descripcion TEXT
);
"""

SQL_CREAR_TABLA_MEDICO = """
CREATE TABLE IF NOT EXISTS Medico (
    id_medico INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT NOT NULL UNIQUE,
    matricula INTEGER NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    tipo_dni TEXT NOT NULL, -- Cambiado a TEXT
    dni TEXT NOT NULL,
    calle TEXT,
    numero_calle INTEGER,
    id_barrio INTEGER,
    email TEXT NOT NULL,
    telefono TEXT,
    id_especialidad INTEGER NOT NULL,
    UNIQUE(tipo_dni, dni),
    FOREIGN KEY (usuario) REFERENCES Usuario(usuario),
    FOREIGN KEY (id_barrio) REFERENCES Barrio(id_barrio),
    FOREIGN KEY (id_especialidad) REFERENCES Especialidad(id_especialidad)
);
"""

SQL_CREAR_TABLA_TURNO = """
CREATE TABLE IF NOT EXISTS Turno (
    id_turno INTEGER PRIMARY KEY AUTOINCREMENT,
    id_paciente INTEGER NOT NULL,
    id_medico INTEGER NOT NULL,
    id_consultorio INTEGER,
    fecha_hora DATETIME NOT NULL,
    motivo TEXT,
    FOREIGN KEY (id_paciente) REFERENCES Paciente(id_paciente),
    FOREIGN KEY (id_medico) REFERENCES Medico(id_medico),
    FOREIGN KEY (id_consultorio) REFERENCES Consultorio(id_consultorio)
);
"""

SQL_CREAR_TABLA_HISTORIAL = """
CREATE TABLE IF NOT EXISTS Historial (
    id_historial INTEGER PRIMARY KEY AUTOINCREMENT,
    id_paciente INTEGER NOT NULL,
    id_medico INTEGER NOT NULL,
    fecha DATETIME NOT NULL,
    diagnostico TEXT,
    observaciones TEXT,
    FOREIGN KEY (id_paciente) REFERENCES Paciente(id_paciente),
    FOREIGN KEY (id_medico) REFERENCES Medico(id_medico)
);
"""

SQL_CREAR_TABLA_RECETA = """
CREATE TABLE IF NOT EXISTS Receta (
    id_receta INTEGER PRIMARY KEY AUTOINCREMENT,
    id_paciente INTEGER NOT NULL,
    id_medico INTEGER NOT NULL,
    id_turno INTEGER,
    estado INTEGER NOT NULL,
    fecha DATETIME NOT NULL,
    descripcion TEXT,
    FOREIGN KEY (id_paciente) REFERENCES Paciente(id_paciente),
    FOREIGN KEY (id_medico) REFERENCES Medico(id_medico),
    FOREIGN KEY (id_turno) REFERENCES Turno(id_turno),
    FOREIGN KEY (estado) REFERENCES Estado(id_estado)
);
"""
SQL_CREAR_TABLA_FRANJA_HORARIA = """
CREATE TABLE IF NOT EXISTS FranjaHoraria (
    id_franja INTEGER PRIMARY KEY AUTOINCREMENT,
    id_medico INTEGER NOT NULL,
    dia_semana INTEGER NOT NULL,  -- 1=Lunes, 2=Martes, etc.
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    FOREIGN KEY (id_medico) REFERENCES Medico(id_medico),
    UNIQUE (id_medico, dia_semana, hora_inicio)
);
"""

SQL_INSERTAR_OBRAS_SOCIALES_DEFAULT = """
INSERT OR IGNORE INTO ObraSocial (id_obra_social, nombre) VALUES
    (1, 'APROSS'), (2, 'DASPU'), (3, 'DASUTN'), (4, 'OMINT'), 
    (5, 'OSDE'), (6, 'PAMI'), (7, 'SWISS MEDICAL');
"""

SQL_INSERTAR_BARRIOS_DEFAULT = """
INSERT OR IGNORE INTO Barrio (id_barrio, nombre) VALUES
    (1, 'ACOSTA'), (2, 'ALBERDI'), (3, 'ALTA CÓRDOBA'), (4, 'ALTAMIRA'), (5, 'ALTO ALBERDI'),
    (6, 'ALTO VERDE'), (7, 'AMEGHINO NORTE'), (8, 'AMEGHINO SUR'), (9, 'ARGUELLO'), (10, 'AYACUCHO'),
    (11, 'BAJADA DE PIEDRA'), (12, 'BAJO GENERAL PAZ'), (13, 'BELLA VISTA'), (14, 'CENTRO'), (15, 'CERRO DE LAS ROSAS');
"""

SENTENCIAS_CREACION = [
    SQL_CREAR_TABLA_USUARIO,
    SQL_CREAR_TABLA_BARRIO,
    SQL_CREAR_TABLA_OBRA_SOCIAL,
    SQL_CREAR_TABLA_CONSULTORIO,
    SQL_CREAR_TABLA_ESTADO,
    SQL_CREAR_TABLA_ESPECIALIDAD,
    SQL_CREAR_TABLA_PACIENTE,
    SQL_CREAR_TABLA_MEDICO,
    SQL_CREAR_TABLA_TURNO,
    SQL_CREAR_TABLA_HISTORIAL,
    SQL_CREAR_TABLA_RECETA,
    SQL_CREAR_TABLA_FRANJA_HORARIA,
    SQL_INSERTAR_OBRAS_SOCIALES_DEFAULT,
    SQL_INSERTAR_BARRIOS_DEFAULT
]

def crear_tablas(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        for sentencia in SENTENCIAS_CREACION:
            # Usar executescript para manejar múltiples sentencias en una cadena
            cursor.executescript(sentencia) if ';' in sentencia else cursor.execute(sentencia)
        conn.commit()
        print("¡Todas las tablas han sido creadas exitosamente!")
        return True
    except sqlite3.Error as e:
        print(f"Error al crear las tablas: {e}")
        conn.rollback()
        return False

def inicializar_base_datos():
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        if crear_tablas(conn):
            print(f"Base de datos '{DB_PATH}' inicializada correctamente.")
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    inicializar_base_datos()
