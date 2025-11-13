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

    try:
        conn = sqlite3.connect(DB_NAME)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None
