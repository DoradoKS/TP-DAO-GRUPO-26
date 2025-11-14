import sqlite3

from Backend.BDD.Conexion import get_conexion
from Backend.Model.Receta import Receta
from Backend.Validaciones.validaciones import Validaciones
from Backend.DAO.UsuarioDAO import UsuarioDAO

class RecetaDAO:
    """
    Gestiona las operaciones CRUD en la tabla Receta.
    """

    def crear_receta(self, receta, usuario_actual):
        """
        Inserta un nuevo objeto Receta en la base de datos.
        """
        # Permisos: solo Medico o Administrador pueden crear recetas
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol not in ["Medico", "Administrador"]:
            print("Permiso denegado: solo Medico o Administrador pueden crear recetas.")
            return None
        # Preparar datos para las validaciones (aceptar ambos nombres de atributo)
        fecha_val = getattr(receta, 'fecha_emision', None) or getattr(receta, 'fecha', None)
        detalles_val = getattr(receta, 'detalles', None) or getattr(receta, 'descripcion', None)

        datos = {
            'id_paciente': receta.id_paciente,
            'id_medico': receta.id_medico,
            'fecha_emision': fecha_val,
            'detalles': detalles_val
        }

        es_valido, errores = Validaciones.validar_receta_completa(datos)
        if not es_valido:
            print("Errores de validación al crear receta:")
            for err in errores:
                print(f"   - {err}")
            return None

        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = """
            INSERT INTO Receta (
                id_paciente, id_medico, id_turno, estado, fecha, descripcion
            ) VALUES (?, ?, ?, ?, ?, ?)
            """

            id_turno_val = getattr(receta, 'id_turno', None)
            estado_val = getattr(receta, 'id_estado', None) or getattr(receta, 'estado', None) or 1
            valores = (
                receta.id_paciente,
                receta.id_medico,
                id_turno_val,
                estado_val,
                fecha_val,
                detalles_val
            )

            cursor.execute(sql, valores)
            conn.commit()
            print("Receta creada exitosamente.")
            return cursor.lastrowid # Retorna el ID de la nueva receta

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al crear la receta: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def obtener_todas_las_recetas(self):
        """
        Retorna una lista de todas las recetas como objetos Receta.
        """
        conn = None
        recetas = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM Receta"
            cursor.execute(sql)
            filas = cursor.fetchall()

            for fila in filas:
                # Columns: id_receta, id_paciente, id_medico, id_turno, estado, fecha, descripcion
                receta = Receta(
                    id_receta=fila[0],
                    id_paciente=fila[1],
                    id_medico=fila[2],
                    id_estado=fila[4],
                    fecha=fila[5],
                    descripcion=fila[6]
                )
                recetas.append(receta)

            return recetas

        except sqlite3.Error as e:
            print(f"Error al obtener las recetas: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def obtener_recetas_por_paciente(self, id_paciente):
        """
        Retorna una lista de recetas para un paciente específico.
        """
        conn = None
        recetas = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM Receta WHERE id_paciente = ?"
            cursor.execute(sql, (id_paciente,))
            filas = cursor.fetchall()

            for fila in filas:
                receta = Receta(
                    id_receta=fila[0],
                    id_paciente=fila[1],
                    id_medico=fila[2],
                    id_estado=fila[4],
                    fecha=fila[5],
                    descripcion=fila[6]
                )
                recetas.append(receta)

            return recetas

        except sqlite3.Error as e:
            print(f"Error al obtener las recetas del paciente: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def eliminar_receta(self, id_receta):
        """
        Elimina una receta dado su ID.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "DELETE FROM Receta WHERE id_receta = ?"
            cursor.execute(sql, (id_receta,))
            conn.commit()

            if cursor.rowcount > 0:
                print("Receta eliminada exitosamente.")
                return True
            else:
                print("No se encontró la receta para eliminar.")
                return False

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al eliminar la receta: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def actualizar_receta(self, receta, usuario_actual):
        """
        Actualiza los detalles de una receta existente.
        """
        # Permisos: solo el propio Medico (autor de la receta) o Administrador pueden actualizar
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        # Obtener usuario del medico que emitió la receta
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT id_medico FROM Receta WHERE id_receta = ?", (receta.id_receta,))
            fila = cursor.fetchone()
            id_medico_receta = fila[0] if fila else None
            # Obtener usuario del medico
            if id_medico_receta:
                cursor.execute("SELECT usuario FROM Medico WHERE id_medico = ?", (id_medico_receta,))
                fila_medico = cursor.fetchone()
                usuario_medico = fila_medico[0] if fila_medico else None
            else:
                usuario_medico = None
        finally:
            if conn:
                conn.close()
        if rol == "Medico" and usuario_actual != usuario_medico:
            print("Permiso denegado: solo el propio médico que emitió la receta puede actualizarla.")
            return False
        if rol not in ["Medico", "Administrador"]:
            print("Permiso denegado: solo Medico o Administrador pueden actualizar recetas.")
            return False
        # Validaciones previas
        fecha_val = getattr(receta, 'fecha_emision', None) or getattr(receta, 'fecha', None)
        detalles_val = getattr(receta, 'detalles', None) or getattr(receta, 'descripcion', None)

        datos = {
            'id_paciente': receta.id_paciente,
            'id_medico': receta.id_medico,
            'fecha_emision': fecha_val,
            'detalles': detalles_val
        }

        es_valido, errores = Validaciones.validar_receta_completa(datos)
        if not es_valido:
            print("Errores de validación al actualizar receta:")
            for err in errores:
                print(f"   - {err}")
            return False

        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = """
            UPDATE Receta
            SET id_paciente = ?, id_medico = ?, id_turno = ?, estado = ?, fecha = ?, descripcion = ?
            WHERE id_receta = ?
            """

            id_turno_val = getattr(receta, 'id_turno', None)
            estado_val = getattr(receta, 'id_estado', None) or getattr(receta, 'estado', None) or 1
            valores = (
                receta.id_paciente,
                receta.id_medico,
                id_turno_val,
                estado_val,
                fecha_val,
                detalles_val,
                receta.id_receta
            )

            cursor.execute(sql, valores)
            conn.commit()

            if cursor.rowcount > 0:
                print("Receta actualizada exitosamente.")
                return True
            else:
                print("No se encontró la receta para actualizar.")
                return False

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al actualizar la receta: {e}")
            return False
        finally:
            if conn:
                conn.close()    

    def obtener_receta_por_id(self, id_receta):
        """
        Retorna un objeto Receta dado su ID.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM Receta WHERE id_receta = ?"
            cursor.execute(sql, (id_receta,))
            fila = cursor.fetchone()

            if fila:
                receta = Receta(
                    id_receta=fila[0],
                    id_paciente=fila[1],
                    id_medico=fila[2],
                    id_estado=fila[4],
                    fecha=fila[5],
                    descripcion=fila[6]
                )
                return receta
            else:
                print("No se encontró la receta con el ID proporcionado.")
                return None

        except sqlite3.Error as e:
            print(f"Error al obtener la receta por ID: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def eliminar_recetas_por_paciente(self, id_paciente):
        """
        Elimina todas las recetas asociadas a un paciente específico.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "DELETE FROM Receta WHERE id_paciente = ?"
            cursor.execute(sql, (id_paciente,))
            conn.commit()

            print(f"Se eliminaron {cursor.rowcount} recetas del paciente.")
            return True

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al eliminar las recetas del paciente: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def eliminar_recetas_por_medico(self, id_medico):
        """
        Elimina todas las recetas asociadas a un médico específico.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "DELETE FROM Receta WHERE id_medico = ?"
            cursor.execute(sql, (id_medico,))
            conn.commit()

            print(f"Se eliminaron {cursor.rowcount} recetas del médico.")
            return True

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al eliminar las recetas del médico: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def obtener_recetas_por_medico(self, id_medico):
        """
        Retorna una lista de recetas para un médico específico.
        """
        conn = None
        recetas = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM Receta WHERE id_medico = ?"
            cursor.execute(sql, (id_medico,))
            filas = cursor.fetchall()

            for fila in filas:
                receta = Receta(
                    id_receta=fila[0],
                    id_paciente=fila[1],
                    id_medico=fila[2],
                    id_estado=fila[4],
                    fecha=fila[5],
                    descripcion=fila[6]
                )
                recetas.append(receta)

            return recetas

        except sqlite3.Error as e:
            print(f"Error al obtener las recetas del médico: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def obtener_recetas_por_fecha(self, fecha):
        """
        Retorna una lista de recetas emitidas en una fecha específica.
        """
        conn = None
        recetas = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM Receta WHERE DATE(fecha) = DATE(?)"
            cursor.execute(sql, (fecha,))
            filas = cursor.fetchall()

            for fila in filas:
                receta = Receta(
                    id_receta=fila[0],
                    id_paciente=fila[1],
                    id_medico=fila[2],
                    id_estado=fila[4],
                    fecha=fila[5],
                    descripcion=fila[6]
                )
                recetas.append(receta)

            return recetas

        except sqlite3.Error as e:
            print(f"Error al obtener las recetas por fecha: {e}")
            return []
        finally:
            if conn:
                conn.close()

    