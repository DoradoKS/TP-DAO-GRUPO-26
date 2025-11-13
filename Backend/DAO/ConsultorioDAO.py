import sqlite3

from Backend.BDD.Conexion import get_conexion
from Backend.Model.Consultorio import Consultorio
from Backend.DAO.UsuarioDAO import UsuarioDAO

class ConsultorioDAO:
    """
    DAO para la entidad Consultorio con columnas (id_consultorio, descripcion).
    """

    def crear_consultorio(self, consultorio: Consultorio, usuario_actual: str):
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol != "Administrador":
            return None, "Permiso denegado."
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Consultorio (descripcion) VALUES (?)", (consultorio.descripcion,))
            conn.commit()
            return cursor.lastrowid, "Consultorio creado exitosamente."
        except sqlite3.Error as e:
            if conn: conn.rollback()
            return None, f"Error al crear el consultorio: {e}"
        finally:
            if conn: conn.close()

    def actualizar_consultorio(self, consultorio: Consultorio, usuario_actual: str):
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol != "Administrador":
            return False, "Permiso denegado."
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("UPDATE Consultorio SET descripcion = ? WHERE id_consultorio = ?", (consultorio.descripcion, consultorio.id_consultorio))
            conn.commit()
            return cursor.rowcount > 0, ("Consultorio actualizado exitosamente." if cursor.rowcount > 0 else "No se encontró el consultorio.")
        except sqlite3.Error as e:
            if conn: conn.rollback()
            return False, f"Error al actualizar el consultorio: {e}"
        finally:
            if conn: conn.close()

    def eliminar_consultorio(self, id_consultorio: int, usuario_actual: str):
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol != "Administrador":
            return False, "Permiso denegado."
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Consultorio WHERE id_consultorio = ?", (id_consultorio,))
            conn.commit()
            return cursor.rowcount > 0, ("Consultorio eliminado exitosamente." if cursor.rowcount > 0 else "No se encontró el consultorio.")
        except sqlite3.Error as e:
            if conn: conn.rollback()
            return False, f"Error al eliminar el consultorio: {e}"
        finally:
            if conn: conn.close()

    def obtener_todos(self):
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT id_consultorio, descripcion FROM Consultorio ORDER BY id_consultorio")
            return [Consultorio(id_consultorio=f[0], descripcion=f[1]) for f in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error al obtener consultorios: {e}")
            return []
        finally:
            if conn: conn.close()

    def obtener_por_id(self, id_consultorio: int):
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT id_consultorio, descripcion FROM Consultorio WHERE id_consultorio = ?", (id_consultorio,))
            fila = cursor.fetchone()
            if fila:
                return Consultorio(id_consultorio=fila[0], descripcion=fila[1])
            return None
        except sqlite3.Error as e:
            print(f"Error al obtener consultorio por ID: {e}")
            return None
        finally:
            if conn: conn.close()