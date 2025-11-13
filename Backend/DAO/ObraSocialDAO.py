import sqlite3
from Backend.BDD.Conexion import get_conexion
from Backend.Model.ObraSocial import ObraSocial
from Backend.DAO.UsuarioDAO import UsuarioDAO

class ObraSocialDAO:
    def cargar_obra_social(self, obra_social, usuario_actual):
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol != "Administrador":
            return None, "Permiso denegado."
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            sql = "INSERT INTO ObraSocial (nombre) VALUES (?)"
            valores = (obra_social.nombre,)
            cursor.execute(sql, valores)
            conn.commit()
            return cursor.lastrowid, "Obra Social creada exitosamente."
        except sqlite3.Error as e:
            if conn: conn.rollback()
            return None, f"Error al crear la obra social: {e}"
        finally:
            if conn: conn.close()

    def actualizar_obra_social(self, obra_social, usuario_actual):
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol != "Administrador":
            return False, "Permiso denegado."
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            sql = "UPDATE ObraSocial SET nombre = ? WHERE id_obra_social = ?"
            valores = (obra_social.nombre, obra_social.id_obra_social)
            cursor.execute(sql, valores)
            conn.commit()
            return True, "Obra Social actualizada exitosamente."
        except sqlite3.Error as e:
            if conn: conn.rollback()
            return False, f"Error al actualizar la obra social: {e}"
        finally:
            if conn: conn.close()

    def eliminar_obra_social(self, id_obra_social, usuario_actual):
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol != "Administrador":
            return False, "Permiso denegado."
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            sql = "DELETE FROM ObraSocial WHERE id_obra_social = ?"
            cursor.execute(sql, (id_obra_social,))
            conn.commit()
            if cursor.rowcount > 0:
                return True, "Obra Social eliminada exitosamente."
            else:
                return False, "No se encontró la Obra Social."
        except sqlite3.Error as e:
            if conn: conn.rollback()
            return False, f"Error al eliminar la obra social: {e}"
        finally:
            if conn: conn.close()
    
    def obtener_obra_social(self):
        conn = None
        obras_sociales = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            sql = "SELECT * FROM ObraSocial ORDER BY id_obra_social"
            cursor.execute(sql)
            filas = cursor.fetchall()
            for fila in filas:
                os = ObraSocial(nombre=fila[1], id_obra_social=fila[0])
                obras_sociales.append(os)
            return obras_sociales
        except sqlite3.Error as e:
            print(f"Error al obtener todas las Obras Sociales: {e}")
            return []
        finally:
            if conn: conn.close()

    def buscar_obra_social_por_id(self, id_obra_social):
        # ... (código existente sin cambios)
        pass

    def buscar_obra_social_por_nombre(self, nombre):
        # ... (código existente sin cambios)
        pass
