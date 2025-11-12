import sqlite3

from Backend.BDD.Conexion import get_conexion
from Backend.Model.Consultorio import Consultorio  # Asegúrate de que el archivo se llame Consultorio.py
from Backend.DAO.UsuarioDAO import UsuarioDAO

class ConsultorioDAO:   
    """
    DAO para la entidad Consultorio.
    Gestiona las operaciones CRUD en la tabla Consultorio.
    """

    def crear_consultorio(self, consultorio, usuario_actual):
        # Permisos: solo Administrador puede crear
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol != "Administrador":
            print("Permiso denegado: solo Administrador puede crear consultorios.")
            return None
        """
        Inserta un nuevo objeto Consultorio en la base de datos.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = """
            INSERT INTO Consultorio (
                nombre, piso, numero, id_especialidad
            ) VALUES (?, ?, ?, ?)
            """
            
            valores = (
                consultorio.nombre, consultorio.piso,
                consultorio.numero, consultorio.id_especialidad
            )

            cursor.execute(sql, valores)
            conn.commit()
            print("Consultorio creado exitosamente.")
            return cursor.lastrowid # Retorna el ID del nuevo consultorio

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al crear el consultorio: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def obtener_todos_los_consultorios(self):
        """
        Retorna una lista de todos los consultorios como objetos Consultorio.
        """
        conn = None
        consultorios = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM Consultorio"
            cursor.execute(sql)
            filas = cursor.fetchall()

            for fila in filas:
                consultorio = Consultorio(
                    id_consultorio=fila[0],
                    descripcion=fila[1]
                )
                consultorios.append(consultorio)

            return consultorios

        except sqlite3.Error as e:
            print(f"Error al obtener los consultorios: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def actualizar_consultorio(self, consultorio, usuario_actual):
        # Permisos: solo Administrador puede actualizar
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol != "Administrador":
            print("Permiso denegado: solo Administrador puede actualizar consultorios.")
            return False
        """
        Actualiza un objeto Consultorio existente en la base de datos.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = """
            UPDATE Consultorio
            SET descripcion = ?
            WHERE id_consultorio = ?
            """
            
            valores = (
                consultorio.descripcion,
                consultorio.id_consultorio
            )

            cursor.execute(sql, valores)
            conn.commit()
            print("Consultorio actualizado exitosamente.")
            return True

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al actualizar el consultorio: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def eliminar_consultorio(self, id_consultorio, usuario_actual):
        # Permisos: solo Administrador puede eliminar
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol != "Administrador":
            print("Permiso denegado: solo Administrador puede eliminar consultorios.")
            return False
        """
        Elimina un consultorio de la base de datos usando su ID.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "DELETE FROM Consultorio WHERE id_consultorio = ?"
            
            cursor.execute(sql, (id_consultorio,))
            conn.commit()

            if cursor.rowcount > 0:
                print("Consultorio eliminado exitosamente.")
                return True
            else:
                print("No se encontró el consultorio para eliminar.")
                return False

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al eliminar el consultorio: {e}")
            return False
        finally:
            if conn:
                conn.close()