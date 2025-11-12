import sqlite3
from Backend.BDD.Conexion import get_conexion
from Backend.Model.Especialidad import Especialidad
from Backend.DAO.UsuarioDAO import UsuarioDAO

class EspecialidadDAO:
    """
    DAO para la entidad Especialidad.
    Gestiona las operaciones CRUD en la tabla Especialidad.
    """

    def buscar_por_nombre_exacto(self, nombre):
        """Busca una especialidad por su nombre exacto (case-insensitive)."""
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            sql = "SELECT * FROM Especialidad WHERE nombre = ?"
            cursor.execute(sql, (nombre,))
            fila = cursor.fetchone()
            if fila:
                return Especialidad(id_especialidad=fila[0], nombre=fila[1], descripcion=fila[2])
            return None
        except sqlite3.Error as e:
            print(f"Error al buscar especialidad por nombre: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def crear_especialidad(self, especialidad, usuario_actual):
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol != "Administrador":
            print("Permiso denegado.")
            return None, "Permiso denegado."

        if self.buscar_por_nombre_exacto(especialidad.nombre):
            return None, "Especialidad ya existente."

        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            sql = "INSERT INTO Especialidad (nombre, descripcion) VALUES (?, ?)"
            valores = (especialidad.nombre, especialidad.descripcion)
            cursor.execute(sql, valores)
            conn.commit()
            return cursor.lastrowid, "Especialidad creada exitosamente."
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al crear la especialidad: {e}")
            return None, f"Error de base de datos: {e}"
        finally:
            if conn:
                conn.close()

    def actualizar_especialidad(self, especialidad, usuario_actual):
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol != "Administrador":
            return False, "Permiso denegado."

        existente = self.buscar_por_nombre_exacto(especialidad.nombre)
        if existente and existente.id_especialidad != especialidad.id_especialidad:
            return False, "Ya existe otra especialidad con ese nombre."

        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            sql = "UPDATE Especialidad SET nombre = ?, descripcion = ? WHERE id_especialidad = ?"
            valores = (especialidad.nombre, especialidad.descripcion, especialidad.id_especialidad)
            cursor.execute(sql, valores)
            conn.commit()
            return True, "Especialidad actualizada exitosamente."
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al actualizar la especialidad: {e}")
            return False, f"Error de base de datos: {e}"
        finally:
            if conn:
                conn.close()

    def obtener_todas_las_especialidades(self):
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Especialidad ORDER BY nombre")
            filas = cursor.fetchall()
            return [Especialidad(id_especialidad=f[0], nombre=f[1], descripcion=f[2]) for f in filas]
        except sqlite3.Error as e:
            print(f"Error al obtener las especialidades: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def obtener_especialidad_por_id(self, id_especialidad):
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Especialidad WHERE id_especialidad = ?", (id_especialidad,))
            fila = cursor.fetchone()
            if fila:
                return Especialidad(id_especialidad=fila[0], nombre=fila[1], descripcion=fila[2])
            return None
        except sqlite3.Error as e:
            print(f"Error al obtener la especialidad por ID: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def eliminar_especialidad(self, id_especialidad, usuario_actual):
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol != "Administrador":
            return False, "Permiso denegado."
        
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Especialidad WHERE id_especialidad = ?", (id_especialidad,))
            conn.commit()
            if cursor.rowcount > 0:
                return True, "Especialidad eliminada exitosamente."
            else:
                return False, "No se encontró la especialidad."
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            # Verificamos si es un error de FK
            if "FOREIGN KEY constraint failed" in str(e):
                return False, "No se puede eliminar la especialidad porque tiene médicos asociados."
            print(f"Error al eliminar la especialidad: {e}")
            return False, f"Error de base de datos: {e}"
        finally:
            if conn:
                conn.close()
