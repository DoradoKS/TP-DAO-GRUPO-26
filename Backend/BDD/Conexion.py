import sqlite3
import pathlib
from .schema import SENTENCIAS_CREACION

# Ruta a la base de datos
BASE_DIR = pathlib.Path(__file__).parent
DB_NAME = BASE_DIR / "clinica.db"


def _inicializar_bdd():
    """Crea la base de datos y todas las tablas si no existen."""
    conn = None
    try:
        print(f"Creando nueva base de datos en: {DB_NAME}")
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        for sentencia in SENTENCIAS_CREACION:
            cursor.executescript(sentencia)
        conn.commit()
        print("Base de datos inicializada correctamente.")
    except sqlite3.Error as e:
        print(f"Error al inicializar la base de datos: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def _aplicar_migraciones(conn):
    """Aplica migraciones ligeras de esquema si faltan columnas."""
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(Historial);")
        columnas = [fila[1] for fila in cur.fetchall()]

        cambios = []
        if 'id_medico' not in columnas:
            cambios.append(("id_medico", "INTEGER"))
        if 'fecha' not in columnas:
            cambios.append(("fecha", "DATETIME"))
        if 'observaciones' not in columnas:
            cambios.append(("observaciones", "TEXT"))

        for nombre, tipo in cambios:
            cur.execute(f"ALTER TABLE Historial ADD COLUMN {nombre} {tipo};")
            conn.commit()

        cur.execute("PRAGMA table_info(Turno);")
        columnas_turno = [fila[1] for fila in cur.fetchall()]
        if 'asistio' not in columnas_turno:
            cur.execute("ALTER TABLE Turno ADD COLUMN asistio INTEGER;")
            conn.commit()

        try:
            cur.execute("INSERT OR IGNORE INTO Estado (id_estado, nombre) VALUES (1, 'Vigente'), (2, 'Vencida');")
            conn.commit()
        except sqlite3.Error:
            pass
    except sqlite3.Error as e:
        print(f"Advertencia: no se pudo aplicar migraciones: {e}")


class DBConnection:
    """Implementación del patrón Singleton usando __new__.

    La primera vez que se crea un objeto `DBConnection()` se guarda en
    `DBConnection._instance`. Las siguientes llamadas a `DBConnection()`
    retornan la misma instancia.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        # Si no existe la instancia única, crearla y guardarla
        if cls._instance is None:
            cls._instance = super(DBConnection, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Inicializar solo la primera vez
        if getattr(self, '_initialized', False):
            return

        if not DB_NAME.exists():
            _inicializar_bdd()

        try:
            # Permitir uso desde hilos distintos
            self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
            self.conn.execute("PRAGMA foreign_keys = ON;")
            try:
                _aplicar_migraciones(self.conn)
            except Exception:
                pass

            # Proxy mínimo para proteger el cierre accidental desde DAOs
            class _Proxy:
                def __init__(self, real):
                    self._real = real

                def close(self):
                    # Ignorar cierres accidentales desde DAOs de forma silenciosa.
                    # Use `close_real_conexion()` para cerrar la conexión explícitamente.
                    pass

                def close_real(self):
                    return self._real.close()

                def __getattr__(self, name):
                    return getattr(self._real, name)

            self._proxy = _Proxy(self.conn)
        except sqlite3.Error as e:
            print(f"Error al conectar con la base de datos: {e}")
            self.conn = None

        self._initialized = True

    def get_conexion(self):
        return getattr(self, '_proxy', self.conn)

    def close_conexion(self):
        if getattr(self, 'conn', None):
            try:
                self.conn.close()
            except Exception as e:
                print(f"Error cerrando la conexión: {e}")
            finally:
                type(self)._instance = None


def get_conexion():
    """API pública compatible: devuelve la conexión SQLite compartida."""
    singleton = DBConnection()
    return singleton.get_conexion()


def close_real_conexion():
    """Cerrar la conexión real; útil al apagar la aplicación."""
    singleton = DBConnection()
    singleton.close_conexion()

