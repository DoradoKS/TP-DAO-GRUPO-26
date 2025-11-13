import sqlite3
import pathlib
from .schema import SENTENCIAS_CREACION

# Obtenemos la ruta absoluta a la carpeta BDD
BASE_DIR = pathlib.Path(__file__).parent
DB_NAME = BASE_DIR / "clinica.db" # Ruta completa a clinica.db

def _inicializar_bdd():
    """
    Crea la base de datos y todas las tablas si no existen.
    """
    conn = None
    try:
        print(f"Creando nueva base de datos en: {DB_NAME}")
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        for sentencia in SENTENCIAS_CREACION:
            cursor.executescript(sentencia) # Usar executescript para múltiples sentencias
        conn.commit()
        print("Base de datos inicializada correctamente.")
    except sqlite3.Error as e:
        print(f"Error al inicializar la base de datos: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def get_conexion():
    """
    Retorna un objeto de conexión a la base de datos SQLite.
    Si la base de datos no existe, la crea e inicializa.
    Habilita el soporte para claves foráneas (FK).
    """
    if not DB_NAME.exists():
        _inicializar_bdd()

    def _aplicar_migraciones(conn):
        try:
            cur = conn.cursor()
            # Verificar columnas existentes en tabla Historial
            cur.execute("PRAGMA table_info(Historial);")
            columnas = [fila[1] for fila in cur.fetchall()]  # nombre de columna en índice 1

            cambios = []
            if 'id_medico' not in columnas:
                cambios.append(("id_medico", "INTEGER"))
            if 'fecha' not in columnas:
                cambios.append(("fecha", "DATETIME"))
            if 'observaciones' not in columnas:
                cambios.append(("observaciones", "TEXT"))

            for nombre, tipo in cambios:
                print(f"Migración: agregando columna '{nombre}' ({tipo}) a tabla Historial...")
                cur.execute(f"ALTER TABLE Historial ADD COLUMN {nombre} {tipo};")
                conn.commit()
            if cambios:
                print("Migración aplicada: columnas agregadas a Historial:", ", ".join(n for n, _ in cambios))

            # Migraciones para Turno
            cur.execute("PRAGMA table_info(Turno);")
            columnas_turno = [fila[1] for fila in cur.fetchall()]
            cambios_turno = []
            if 'asistio' not in columnas_turno:
                cambios_turno.append(("asistio", "INTEGER"))

            for nombre, tipo in cambios_turno:
                print(f"Migración: agregando columna '{nombre}' ({tipo}) a tabla Turno...")
                cur.execute(f"ALTER TABLE Turno ADD COLUMN {nombre} {tipo};")
                conn.commit()
            if cambios_turno:
                print("Migración aplicada: columnas agregadas a Turno:", ", ".join(n for n, _ in cambios_turno))
        except sqlite3.Error as e:
            # No bloquear la conexión si falla la migración; solo informar
            print(f"Advertencia: no se pudo aplicar migraciones: {e}")

    try:
        conn = sqlite3.connect(DB_NAME)
        conn.execute("PRAGMA foreign_keys = ON;")
        _aplicar_migraciones(conn)
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None
