import sqlite3
# En DAO/ObraSocialDAO.py

from Backend.BDD.Conexion import get_conexion
from Backend.Model.ObraSocial import ObraSocial # Importa el modelo que acabamos de crear

class ObraSocialDAO:
    """
    DAO para la entidad ObraSocial.
    Por ahora, solo implementamos la lectura de datos.
    """
    def cargar_obra_social(self, obra_social):
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

    def eliminar_obra_social(self, id_obra_social):
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

