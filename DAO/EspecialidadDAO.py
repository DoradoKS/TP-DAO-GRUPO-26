import sqlite3      

from Backend.BDD.Conexion import get_conexion
from Backend.Model.Especialidad import Especialidad

class EspecialidadDAO:
    """
    DAO para la entidad Especialidad.
    Gestiona las operaciones CRUD en la tabla Especialidad.
    """

    def crear_especialidad(self, especialidad):
        """
        Inserta un nuevo objeto Especialidad en la base de datos.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = """
            INSERT INTO Especialidad (nombre, descripcion) 
            VALUES (?, ?)
            """
            
            valores = (
                especialidad.nombre, especialidad.descripcion
            )

            cursor.execute(sql, valores)
            conn.commit()
            print("Especialidad creada exitosamente.")
            return cursor.lastrowid # Retorna el ID de la nueva especialidad

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al crear la especialidad: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def obtener_todas_las_especialidades(self):
        """
        Retorna una lista de todas las especialidades como objetos Especialidad.
        """
        conn = None
        especialidades = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM Especialidad"
            cursor.execute(sql)
            filas = cursor.fetchall()

            for fila in filas:
                especialidad = Especialidad(
                    id_especialidad=fila[0],
                    nombre=fila[1],
                    descripcion=fila[2]
                )
                especialidades.append(especialidad)

            return especialidades

        except sqlite3.Error as e:
            print(f"Error al obtener las especialidades: {e}")
            return []
        finally:
            if conn:
                conn.close()    

    def obtener_especialidad_por_id(self, id_especialidad):
        """
        Retorna un objeto Especialidad dado su ID.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM Especialidad WHERE id_especialidad = ?"
            cursor.execute(sql, (id_especialidad,))
            fila = cursor.fetchone()

            if fila:
                especialidad = Especialidad(
                    id_especialidad=fila[0],
                    nombre=fila[1],
                    descripcion=fila[2]
                )
                return especialidad
            else:
                return None

        except sqlite3.Error as e:
            print(f"Error al obtener la especialidad por ID: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def actualizar_especialidad(self, especialidad):    
        """
        Actualiza una especialidad existente en la base de datos.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = """
            UPDATE Especialidad
            SET nombre = ?, descripcion = ?
            WHERE id_especialidad = ?
            """
            valores = (
                especialidad.nombre,
                especialidad.descripcion,
                especialidad.id_especialidad
            )

            cursor.execute(sql, valores)
            conn.commit()
            print("Especialidad actualizada exitosamente.")
            return True

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al actualizar la especialidad: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def eliminar_especialidad(self, id_especialidad):
        """
        Elimina una especialidad de la base de datos usando su ID.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "DELETE FROM Especialidad WHERE id_especialidad = ?"
            
            cursor.execute(sql, (id_especialidad,))
            conn.commit()

            if cursor.rowcount > 0:
                print("Especialidad eliminada exitosamente.")
                return True
            else:
                print("No se encontró la especialidad para eliminar.")
                return False

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al eliminar la especialidad: {e}")
            return False
        finally:
            if conn:
                conn.close()