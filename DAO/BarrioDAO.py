import sqlite3

from BDD.Conexion import get_conexion
from Model.Consultorio import Consultorio  # Asegúrate de que el archivo se llame Consultorio.py

class BarrioDAO:
    """
    DAO para la entidad Barrio.
    Gestiona las operaciones CRUD en la tabla Barrio.
    """

    def crear_barrio(self, barrio):
        """
        Inserta un nuevo objeto Barrio en la base de datos.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = """
            INSERT INTO Barrio (
                nombre, codigo_postal
            ) VALUES (?, ?)
            """
            
            valores = (
                barrio.nombre, barrio.codigo_postal
            )

            cursor.execute(sql, valores)
            conn.commit()
            print("Barrio creado exitosamente.")
            return cursor.lastrowid # Retorna el ID del nuevo barrio

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al crear el barrio: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def obtener_todos_los_barrios(self):
        """
        Retorna una lista de todos los barrios como objetos Barrio.
        """
        conn = None
        barrios = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM Barrio"
            cursor.execute(sql)
            filas = cursor.fetchall()

            for fila in filas:
                barrio = Barrio(
                    id_barrio=fila[0],
                    nombre=fila[1],
                    codigo_postal=fila[2]
                )
                barrios.append(barrio)

            return barrios

        except sqlite3.Error as e:
            print(f"Error al obtener los barrios: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def obtener_barrio_por_id(self, id_barrio):
        """
        Retorna un objeto Barrio dado su ID.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM Barrio WHERE id_barrio = ?"
            cursor.execute(sql, (id_barrio,))
            fila = cursor.fetchone()

            if fila:
                barrio = Barrio(
                    id_barrio=fila[0],
                    nombre=fila[1],
                    codigo_postal=fila[2]
                )
                return barrio
            else:
                return None

        except sqlite3.Error as e:
            print(f"Error al obtener el barrio por ID: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def actualizar_barrio(self, barrio):
        """
        Actualiza un objeto Barrio existente en la base de datos.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = """
            UPDATE Barrio
            SET nombre = ?, codigo_postal = ?
            WHERE id_barrio = ?
            """
            
            valores = (
                barrio.nombre,
                barrio.codigo_postal,
                barrio.id_barrio
            )

            cursor.execute(sql, valores)
            conn.commit()
            print("Barrio actualizado exitosamente.")
            return True

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al actualizar el barrio: {e}")
            return False
        finally:
            if conn:
                conn.close()    

    def eliminar_barrio(self, id_barrio):   
        """
        Elimina un barrio de la base de datos usando su ID.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "DELETE FROM Barrio WHERE id_barrio = ?"
            
            cursor.execute(sql, (id_barrio,))
            conn.commit()

            if cursor.rowcount > 0:
                print("Barrio eliminado exitosamente.")
                return True
            else:
                print("No se encontró el barrio con el ID proporcionado.")
                return False

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al eliminar el barrio: {e}")
            return False
        finally:
            if conn:
                conn.close()
    