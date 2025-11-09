import sqlite3
import pathlib

# Obtenemos la ruta absoluta a la carpeta BDD
# __file__ es la ruta de este archivo (conexion.py)
# .parent es la carpeta que lo contiene (BDD)
BASE_DIR = pathlib.Path(__file__).parent
DB_NAME = BASE_DIR / "clinica.db" # Ruta completa a clinica.db

def get_conexion():
    """
    Retorna un objeto de conexión a la base de datos SQLite.
    Habilita el soporte para claves foráneas (FK).
    """
    try:
        # Se conecta a la DB en la ruta absoluta
        conn = sqlite3.connect(DB_NAME)
        # Activar las claves foráneas (¡MUY IMPORTANTE!)
        # Por defecto, SQLite no las comprueba.
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None