import sqlite3
# En DAO/MedicoDAO.py

from Backend.BDD.Conexion import get_conexion
from Backend.Model.Medico import Medico # Asegúrate de que el archivo se llame Medico.py

class MedicoDAO:
    """
    DAO para la entidad Medico.
    Gestiona las operaciones CRUD en la tabla Medico.
    """

    def crear_medico(self, medico):
        """
        Inserta un nuevo objeto Medico en la base de datos.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = """
            INSERT INTO Medico (
                usuario, matricula, nombre, apellido, tipo_dni, dni, 
                calle, numero_calle, email, telefono, id_especialidad
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            valores = (
                medico.usuario, medico.matricula, medico.nombre,
                medico.apellido, medico.tipo_dni, medico.dni,
                medico.calle, medico.numero_calle, medico.email,
                medico.telefono, medico.id_especialidad
            )

            cursor.execute(sql, valores)
            conn.commit()
            print("Medico creado exitosamente.")
            return cursor.lastrowid # Retorna el ID del nuevo médico

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al crear el médico: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def obtener_todos_los_medicos(self):
        """
        Retorna una lista de todos los médicos como objetos Medico.
        """
        conn = None
        medicos = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM Medico"
            cursor.execute(sql)
            filas = cursor.fetchall()

            for fila in filas:
                # El orden debe coincidir con el __init__ de la clase Medico
                m = Medico(
                    id_medico=fila[0], usuario=fila[1], matricula=fila[2],
                    nombre=fila[3], apellido=fila[4], tipo_dni=fila[5],
                    dni=fila[6], calle=fila[7], numero_calle=fila[8],
                    email=fila[9], telefono=fila[10], id_especialidad=fila[11]
                )
                medicos.append(m)
            
            return medicos

        except sqlite3.Error as e:
            print(f"Error al obtener todos los médicos: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def obtener_medico_por_matricula(self, matricula):
        """
        Busca un médico por su matrícula (que es UNIQUE).
        Retorna un objeto Medico o None.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM Medico WHERE matricula = ?"
            cursor.execute(sql, (matricula,))
            
            fila = cursor.fetchone()

            if fila:
                m = Medico(
                    id_medico=fila[0], usuario=fila[1], matricula=fila[2],
                    nombre=fila[3], apellido=fila[4], tipo_dni=fila[5],
                    dni=fila[6], calle=fila[7], numero_calle=fila[8],
                    email=fila[9], telefono=fila[10], id_especialidad=fila[11]
                )
                return m
            else:
                return None # No se encontró el médico

        except sqlite3.Error as e:
            print(f"Error al obtener médico por matrícula: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def actualizar_medico(self, medico):
        """
        Actualiza los datos de un médico en la DB, buscando por id_medico.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = """
            UPDATE Medico SET 
                usuario = ?, matricula = ?, nombre = ?, apellido = ?, tipo_dni = ?, 
                dni = ?, calle = ?, numero_calle = ?, email = ?, telefono = ?, 
                id_especialidad = ?
            WHERE id_medico = ?
            """
            
            valores = (
                medico.usuario, medico.matricula, medico.nombre,
                medico.apellido, medico.tipo_dni, medico.dni,
                medico.calle, medico.numero_calle, medico.email,
                medico.telefono, medico.id_especialidad,
                medico.id_medico # ID para el WHERE
            )

            cursor.execute(sql, valores)
            conn.commit()
            print("Medico actualizado exitosamente.")
            return True

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al actualizar el médico: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def eliminar_medico(self, id_medico):
        """
        Elimina un médico de la base de datos usando su ID.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "DELETE FROM Medico WHERE id_medico = ?"
            
            cursor.execute(sql, (id_medico,))
            conn.commit()

            if cursor.rowcount > 0:
                print(f"Medico con ID {id_medico} eliminado exitosamente.")
                return True
            else:
                print(f"No se encontró médico con ID {id_medico}.")
                return False

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            # Esto fallará si el médico tiene turnos asignados (¡bien!)
            print(f"Error al eliminar el médico (puede tener turnos): {e}")
            return False
        finally:
            if conn:
                conn.close()