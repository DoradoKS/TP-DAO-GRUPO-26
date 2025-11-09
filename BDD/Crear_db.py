import sqlite3
import pathlib  # Importamos la librería para manejar rutas

# --- ESTA ES LA PARTE NUEVA ---
# Obtiene la ruta de la carpeta DONDE ESTÁ ESTE SCRIPT
SCRIPT_DIR = pathlib.Path(__file__).parent
# Define el nombre de la DB para que esté EN ESA MISMA CARPETA
DB_NAME = SCRIPT_DIR / "clinica.db"
# --- FIN DE LA PARTE NUEVA ---


def crear_conexion():
    """Crea una conexión a la base de datos SQLite."""
    try:
        # Ahora se conecta usando la ruta completa y correcta
        conn = sqlite3.connect(DB_NAME)
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None

def crear_tablas(conn):
    """Crea las tablas en la base de datos."""
    try:
        cursor = conn.cursor()
        
        # Activar el soporte para claves foráneas (es crucial)
        cursor.execute("PRAGMA foreign_keys = ON;")

        # --- Tablas sin dependencias (o "catálogos") ---

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS TipoDni (
            tipo_dni INTEGER PRIMARY KEY,
            tipo VARCHAR(50) NOT NULL
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Usuario (
            usuario VARCHAR(100) PRIMARY KEY,
            contraseña VARCHAR(100) NOT NULL,
            rol VARCHAR(50) NOT NULL
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Barrio (
            id_barrio INTEGER PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ObraSocial (
            id_obra_social INTEGER PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Especialidad (
            id_especialidad INTEGER PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            descripcion VARCHAR(255)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Consultorio (
            id_consultorio INTEGER PRIMARY KEY,
            descripcion VARCHAR(255)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Estado (
            id_estado INTEGER PRIMARY KEY,
            nombre VARCHAR(50) NOT NULL
        );
        """)

        # --- Tablas con dependencias (claves foráneas) ---

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Paciente (
            id_paciente INTEGER PRIMARY KEY AUTOINCREMENT,
            id_barrio INTEGER NOT NULL,
            usuario VARCHAR(100) NOT NULL,
            nombre VARCHAR(100) NOT NULL,
            apellido VARCHAR(100) NOT NULL,
            fecha_nacimiento DATE NOT NULL,
            tipo_dni INTEGER NOT NULL,
            dni VARCHAR(20) NOT NULL,
            email VARCHAR(100) NOT NULL,
            telefono VARCHAR(50),
            id_obra_social INTEGER,
            calle VARCHAR(100),
            numero_calle INTEGER,
            UNIQUE(usuario),
            UNIQUE(tipo_dni, dni),
            FOREIGN KEY (id_barrio) REFERENCES Barrio(id_barrio),
            FOREIGN KEY (usuario) REFERENCES Usuario(usuario),
            FOREIGN KEY (tipo_dni) REFERENCES TipoDni(tipo_dni),
            FOREIGN KEY (id_obra_social) REFERENCES ObraSocial(id_obra_social)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Medico (
            id_medico INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario VARCHAR(100) NOT NULL,
            matricula INT NOT NULL,
            nombre VARCHAR(100) NOT NULL,
            apellido VARCHAR(100) NOT NULL,
            tipo_dni INTEGER NOT NULL,
            dni VARCHAR(20) NOT NULL,
            calle VARCHAR(100),
            numero_calle INTEGER,
            email VARCHAR(100) NOT NULL,
            telefono VARCHAR(50),
            id_especialidad INTEGER NOT NULL,
            UNIQUE(usuario),
            UNIQUE(matricula),
            UNIQUE(tipo_dni, dni),
            FOREIGN KEY (usuario) REFERENCES Usuario(usuario),
            FOREIGN KEY (tipo_dni) REFERENCES TipoDni(tipo_dni),
            FOREIGN KEY (id_especialidad) REFERENCES Especialidad(id_especialidad)
        );
        """)
    
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Turno (
            id_turno INTEGER PRIMARY KEY AUTOINCREMENT,
            id_medico INTEGER NOT NULL,
            id_paciente INTEGER NOT NULL,
            fechainicio DATE NOT NULL,
            hora_inicio TIME NOT NULL,
            hora_fin TIME NOT NULL,
            observaciones VARCHAR(255),
            estado INTEGER NOT NULL,
            id_consultorio INTEGER,
            FOREIGN KEY (id_medico) REFERENCES Medico(id_medico),
            FOREIGN KEY (id_paciente) REFERENCES Paciente(id_paciente),
            FOREIGN KEY (estado) REFERENCES Estado(id_estado),
            FOREIGN KEY (id_consultorio) REFERENCES Consultorio(id_consultorio)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Historial (
            id_historial INTEGER PRIMARY KEY AUTOINCREMENT,
            id_paciente INTEGER NOT NULL,
            diagnostico VARCHAR(1000),
            FOREIGN KEY (id_paciente) REFERENCES Paciente(id_paciente)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Receta (
            id_receta INTEGER PRIMARY KEY AUTOINCREMENT,
            id_paciente INTEGER NOT NULL,
            id_medico INTEGER NOT NULL,
            id_turno INTEGER,
            estado INTEGER NOT NULL,
            fecha DATETIME NOT NULL,
            descripcion VARCHAR(1000),
            FOREIGN KEY (id_paciente) REFERENCES Paciente(id_paciente),
            FOREIGN KEY (id_medico) REFERENCES Medico(id_medico),
            FOREIGN KEY (id_turno) REFERENCES Turno(id_turno),
            FOREIGN KEY (estado) REFERENCES Estado(id_estado)
        );
        """)

        conn.commit()
        print("¡Todas las tablas han sido creadas exitosamente!")

    except sqlite3.Error as e:
        print(f"Error al crear las tablas: {e}")
        conn.rollback() # Revertir cambios si hay un error

def main():
    conn = crear_conexion()
    if conn:
        crear_tablas(conn)
        conn.close()
        print(f"Base de datos '{DB_NAME}' creada y cerrada.")

if __name__ == "__main__":
    main()