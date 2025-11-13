import sqlite3
# En DAO/ObraSocialDAO.py

from Backend.BDD.Conexion import get_conexion
from Backend.Model.ObraSocial import ObraSocial # Importa el modelo que acabamos de crear
from Backend.DAO.UsuarioDAO import UsuarioDAO

class ObraSocialDAO:
    """
    DAO para la entidad ObraSocial.
    Por ahora, solo implementamos la lectura de datos.
    """
    def cargar_obra_social(self, obra_social, usuario_actual):
        # Permisos: solo Administrador puede crear
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol != "Administrador":
            print("Permiso denegado: solo Administrador puede crear obras sociales.")
            return None
        """
        Inserta un nuevo objeto ObraSocial en la base de datos.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = """
            INSERT INTO ObraSocial (nombre) 
            VALUES (?)
            """
            
            valores = (
                obra_social.nombre,
            )

            cursor.execute(sql, valores)
            conn.commit()
            print("Obra Social creada exitosamente.")
            return cursor.lastrowid # Retorna el ID de la nueva obra social

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al crear la obra social: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def eliminar_obra_social(self, id_obra_social, usuario_actual):
        # Permisos: solo Administrador puede eliminar
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol != "Administrador":
            print("Permiso denegado: solo Administrador puede eliminar obras sociales.")
            return False
        """
        Elimina una ObraSocial de la base de datos por su ID.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "DELETE FROM ObraSocial WHERE id_obra_social = ?"
            cursor.execute(sql, (id_obra_social,))
            conn.commit()
            print("Obra Social eliminada exitosamente.")
            return True

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al eliminar la obra social: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def actualizar_obra_social(self, obra_social: ObraSocial, usuario_actual: str):
        # Permisos: solo Administrador puede actualizar
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol != "Administrador":
            return False, "Permiso denegado."
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("UPDATE ObraSocial SET nombre = ? WHERE id_obra_social = ?", (obra_social.nombre, obra_social.id_obra_social))
            conn.commit()
            return cursor.rowcount > 0, ("Obra Social actualizada exitosamente." if cursor.rowcount > 0 else "No se encontró la Obra Social.")
        except sqlite3.Error as e:
            if conn: conn.rollback()
            return False, f"Error al actualizar la Obra Social: {e}"
        finally:
            if conn: conn.close()
    
    def obtener_obra_social(self):
        """
        Retorna una lista de todas las obras sociales como objetos.
        """
        conn = None
        obras_sociales = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM ObraSocial ORDER BY nombre"
            cursor.execute(sql)
            filas = cursor.fetchall()

            for fila in filas:
                os = ObraSocial(
                    id_obra_social=fila[0], 
                    nombre=fila[1]
                )
                obras_sociales.append(os)
            
            return obras_sociales

        except sqlite3.Error as e:
            print(f"Error al obtener todas las Obras Sociales: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def buscar_obra_social_por_id(self, id_obra_social):
        """
        Retorna un objeto ObraSocial dado su ID.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM ObraSocial WHERE id_obra_social = ?"
            cursor.execute(sql, (id_obra_social,))
            fila = cursor.fetchone()

            if fila:
                obra_social = ObraSocial(
                    id_obra_social=fila[0],
                    nombre=fila[1]
                )
                return obra_social
            else:
                print(f"No se encontró Obra Social con ID {id_obra_social}.")
                return None

        except sqlite3.Error as e:
            print(f"Error al buscar la Obra Social por ID: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def buscar_obra_social_por_nombre(self, nombre):
        """
        Retorna un objeto ObraSocial dado su nombre.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM ObraSocial WHERE nombre = ?"
            cursor.execute(sql, (nombre,))
            fila = cursor.fetchone()

            if fila:
                obra_social = ObraSocial(
                    id_obra_social=fila[0],
                    nombre=fila[1]
                )
                return obra_social
            else:
                print(f"No se encontró Obra Social con nombre '{nombre}'.")
                return None

        except sqlite3.Error as e:
            print(f"Error al buscar la Obra Social por nombre: {e}")
            return None
        finally:
            if conn:
                conn.close()

