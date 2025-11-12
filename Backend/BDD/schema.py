# Contiene el esquema de la base de datos para una inicialización consistente.
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

SQL_CREAR_TABLA_TIPO_DNI = """
CREATE TABLE IF NOT EXISTS TipoDni (
    tipo_dni INTEGER PRIMARY KEY,
    tipo TEXT NOT NULL
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
    tipo_dni INTEGER NOT NULL,
    dni TEXT NOT NULL,
    email TEXT NOT NULL,
    telefono TEXT,
    id_obra_social INTEGER,
    calle TEXT,
    numero_calle INTEGER,
    UNIQUE(tipo_dni, dni),
    FOREIGN KEY (usuario) REFERENCES Usuario(usuario),
    FOREIGN KEY (id_barrio) REFERENCES Barrio(id_barrio),
    FOREIGN KEY (tipo_dni) REFERENCES TipoDni(tipo_dni),
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
    tipo_dni INTEGER NOT NULL,
    dni TEXT NOT NULL,
    calle TEXT,
    numero_calle INTEGER,
    email TEXT NOT NULL,
    telefono TEXT,
    id_especialidad INTEGER NOT NULL,
    UNIQUE(tipo_dni, dni),
    FOREIGN KEY (usuario) REFERENCES Usuario(usuario),
    FOREIGN KEY (tipo_dni) REFERENCES TipoDni(tipo_dni),
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

SQL_CREAR_TABLA_HISTORIAL = """
CREATE TABLE IF NOT EXISTS Historial (
    id_historial INTEGER PRIMARY KEY AUTOINCREMENT,
    id_paciente INTEGER NOT NULL,
    diagnostico TEXT,
    FOREIGN KEY (id_paciente) REFERENCES Paciente(id_paciente)
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

SQL_INSERTAR_TIPOS_DNI = """
INSERT OR IGNORE INTO TipoDni (tipo_dni, tipo) VALUES
    (1, 'DNI'),
    (2, 'Pasaporte'),
    (3, 'Carnet Extranjero');
"""

SQL_INSERTAR_OBRAS_SOCIALES_DEFAULT = """
INSERT OR IGNORE INTO ObraSocial (id_obra_social, nombre) VALUES
    (1, 'APROSS'),
    (2, 'DASPU'),
    (3, 'DASUTN'),
    (4, 'OMINT'),
    (5, 'OSDE'),
    (6, 'PAMI'),
    (7, 'SWISS MEDICAL');
"""

SQL_INSERTAR_BARRIOS_DEFAULT = """
INSERT OR IGNORE INTO Barrio (id_barrio, nombre) VALUES
    (1, 'ACOSTA'),
    (2, 'ALBERDI'),
    (3, 'ALTA CÓRDOBA'),
    (4, 'ALTAMIRA'),
    (5, 'ALTO ALBERDI'),
    (6, 'ALTO VERDE'),
    (7, 'AMEGHINO NORTE'),
    (8, 'AMEGHINO SUR'),
    (9, 'ARGUELLO'),
    (10, 'AYACUCHO'),
    (11, 'BAJADA DE PIEDRA'),
    (12, 'BAJO GENERAL PAZ'),
    (13, 'BELLA VISTA'),
    (14, 'CENTRO'),
    (15, 'CERRO DE LAS ROSAS');
"""

# Lista de todas las sentencias de creación de tablas (para compatibilidad con Conexion.py)
SENTENCIAS_CREACION = [
    SQL_CREAR_TABLA_USUARIO,
    SQL_CREAR_TABLA_TIPO_DNI,
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
    SQL_INSERTAR_TIPOS_DNI,
    SQL_INSERTAR_OBRAS_SOCIALES_DEFAULT,
    SQL_INSERTAR_BARRIOS_DEFAULT
]


def crear_tablas(conn):
    """Crea las tablas en la base de datos usando cursor.execute()"""
    try:
        cursor = conn.cursor()
        
        # Activar el soporte para claves foráneas
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Tablas sin dependencias
        cursor.execute(SQL_CREAR_TABLA_USUARIO)
        cursor.execute(SQL_CREAR_TABLA_TIPO_DNI)
        cursor.execute(SQL_CREAR_TABLA_BARRIO)
        cursor.execute(SQL_CREAR_TABLA_OBRA_SOCIAL)
        cursor.execute(SQL_CREAR_TABLA_CONSULTORIO)
        cursor.execute(SQL_CREAR_TABLA_ESTADO)
        cursor.execute(SQL_CREAR_TABLA_ESPECIALIDAD)
        
        # Tablas con dependencias
        cursor.execute(SQL_CREAR_TABLA_PACIENTE)
        cursor.execute(SQL_CREAR_TABLA_MEDICO)
        cursor.execute(SQL_CREAR_TABLA_TURNO)
        cursor.execute(SQL_CREAR_TABLA_HISTORIAL)
        cursor.execute(SQL_CREAR_TABLA_RECETA)
        
        # Insertar datos por defecto
        cursor.execute(SQL_INSERTAR_TIPOS_DNI)
        cursor.execute(SQL_INSERTAR_OBRAS_SOCIALES_DEFAULT)
        cursor.execute(SQL_INSERTAR_BARRIOS_DEFAULT)
        
        conn.commit()
        print("¡Todas las tablas han sido creadas exitosamente!")
        return True
        
    except sqlite3.Error as e:
        print(f"Error al crear las tablas: {e}")
        conn.rollback()
        return False


def inicializar_base_datos():
    """Función principal para inicializar la base de datos"""
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
