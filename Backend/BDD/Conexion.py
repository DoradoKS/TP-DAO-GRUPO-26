import sqlite3
import pathlib
from .schema import SENTENCIAS_CREACION

# Obtenemos la ruta absoluta a la carpeta BDD
BASE_DIR = pathlib.Path(__file__).parent
DB_NAME = BASE_DIR / "clinica.db" # Ruta completa a clinica.db

def get_conexion():
    """
    Retorna un objeto de conexión a la base de datos SQLite.
    Habilita el soporte para claves foráneas (FK).
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None

def inicializar_bdd():
    """
    Crea todas las tablas de la base de datos si no existen.
    """
    conn = None
    try:
        conn = get_conexion()
        cursor = conn.cursor()
        for sentencia in SENTENCIAS_CREACION:
            cursor.execute(sentencia)
        conn.commit()
        print("Base de datos inicializada correctamente.")
    except sqlite3.Error as e:
        print(f"Error al inicializar la base de datos: {e}")
    finally:
        if conn:
            conn.close()
