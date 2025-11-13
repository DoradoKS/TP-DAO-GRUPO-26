import sqlite3
from datetime import datetime
from Backend.BDD.Conexion import get_conexion
from Backend.Model.Historial import Historial
from Backend.DAO.UsuarioDAO import UsuarioDAO


class HistorialDAO:
    """
    DAO para la entidad Historial.
    Gestiona el registro y consulta de historiales clínicos.
    """

    def crear_entrada_historial(self, historial, usuario_actual):
        """
        Crea una nueva entrada en el historial clínico.
        Solo médicos pueden crear entradas.
        """
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol != "Medico":
            return None, "Permiso denegado. Solo médicos pueden registrar en el historial."

        if not all([historial.id_paciente, historial.id_medico, historial.diagnostico]):
            return None, "Faltan datos obligatorios (paciente, médico, diagnóstico)."

        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            
            # Usar fecha actual si no se proporciona
            fecha = historial.fecha if historial.fecha else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            sql = """
            INSERT INTO Historial (id_paciente, id_medico, fecha, diagnostico, observaciones)
            VALUES (?, ?, ?, ?, ?)
            """
            valores = (
                historial.id_paciente,
                historial.id_medico,
                fecha,
                historial.diagnostico,
                historial.observaciones
            )
            cursor.execute(sql, valores)
            conn.commit()
            return cursor.lastrowid, "Entrada de historial creada exitosamente."
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            return None, f"Error de base de datos: {e}"
        finally:
            if conn:
                conn.close()

    def obtener_historial_por_paciente(self, id_paciente, usuario_actual):
        """
        Obtiene todo el historial de un paciente.
        Accesible por el paciente mismo o por médicos.
        """
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        
        # Verificar permisos
        if rol == "Paciente":
            # Verificar que el paciente solo pueda ver su propio historial
            from Backend.DAO.PacienteDAO import PacienteDAO
            paciente = PacienteDAO().obtener_paciente_por_usuario(usuario_actual)
            if not paciente or paciente.id_paciente != id_paciente:
                return [], "Permiso denegado. Solo puede consultar su propio historial."
        elif rol not in ["Medico", "Administrador"]:
            return [], "Permiso denegado."

        conn = None
        historiales = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id_historial, id_paciente, id_medico, fecha, diagnostico, observaciones
                FROM Historial 
                WHERE id_paciente = ? 
                ORDER BY fecha DESC
                """,
                (id_paciente,)
            )
            
            for fila in cursor.fetchall():
                historiales.append(Historial(
                    id_historial=fila[0],
                    id_paciente=fila[1],
                    id_medico=fila[2],
                    fecha=fila[3],
                    diagnostico=fila[4],
                    observaciones=fila[5]
                ))
            return historiales, "OK"
        except sqlite3.Error as e:
            print(f"Error al obtener historial: {e}")
            return [], f"Error: {e}"
        finally:
            if conn:
                conn.close()

    def obtener_entrada_por_id(self, id_historial):
        """Obtiene una entrada específica del historial por su ID."""
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id_historial, id_paciente, id_medico, fecha, diagnostico, observaciones
                FROM Historial WHERE id_historial = ?
                """,
                (id_historial,)
            )
            fila = cursor.fetchone()
            
            if fila:
                return Historial(
                    id_historial=fila[0],
                    id_paciente=fila[1],
                    id_medico=fila[2],
                    fecha=fila[3],
                    diagnostico=fila[4],
                    observaciones=fila[5]
                )
            return None
        except sqlite3.Error as e:
            print(f"Error al obtener entrada de historial: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def actualizar_entrada_historial(self, historial, usuario_actual):
        """
        Actualiza una entrada del historial.
        Solo el médico que creó la entrada puede modificarla.
        """
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol != "Medico":
            return False, "Permiso denegado. Solo médicos pueden modificar el historial."

        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            
            # Verificar que el médico sea el autor de la entrada
            from Backend.DAO.MedicoDAO import MedicoDAO
            medico = MedicoDAO().obtener_medico_por_usuario(usuario_actual)
            if not medico:
                return False, "Médico no encontrado."
            
            cursor.execute("SELECT id_medico FROM Historial WHERE id_historial = ?", (historial.id_historial,))
            fila = cursor.fetchone()
            if not fila or fila[0] != medico.id_medico:
                return False, "Solo puede modificar sus propias entradas de historial."
            
            sql = """
            UPDATE Historial 
            SET diagnostico = ?, observaciones = ?
            WHERE id_historial = ?
            """
            cursor.execute(sql, (historial.diagnostico, historial.observaciones, historial.id_historial))
            conn.commit()
            return True, "Entrada de historial actualizada exitosamente."
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            return False, f"Error de base de datos: {e}"
        finally:
            if conn:
                conn.close()

    def eliminar_entrada_historial(self, id_historial, usuario_actual):
        """
        Elimina una entrada del historial.
        Solo administradores pueden eliminar.
        """
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol != "Administrador":
            return False, "Permiso denegado. Solo administradores pueden eliminar entradas."

        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Historial WHERE id_historial = ?", (id_historial,))
            conn.commit()
            return cursor.rowcount > 0, "Entrada eliminada exitosamente." if cursor.rowcount > 0 else "Entrada no encontrada."
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            return False, f"Error de base de datos: {e}"
        finally:
            if conn:
                conn.close()
