import sqlite3      
import random

from Backend.BDD.Conexion import get_conexion
from Backend.Model.Turno import Turno
from Backend.DAO.UsuarioDAO import UsuarioDAO
from datetime import datetime, timedelta

class TurnoDAO:
    """
    DAO para la entidad Turno.
    Gestiona las operaciones CRUD en la tabla Turno.
    """

    def crear_turno(self, turno, usuario_actual):
        """
        Inserta un nuevo objeto Turno en la base de datos.
        Retorna una tupla (id_creado, mensaje).
        """
        if not all([turno, turno.id_paciente, turno.id_medico, turno.fecha_hora]):
            return None, "Falta información requerida para crear el turno."

        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol not in ["Administrador", "Paciente"]:
            return None, "Permiso denegado."

        try:
            inicio = datetime.strptime(str(turno.fecha_hora), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                inicio = datetime.strptime(str(turno.fecha_hora), "%Y-%m-%d %H:%M")
            except ValueError:
                return None, "Formato de fecha_hora inválido."

        fin = inicio + timedelta(minutes=30)

        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql_paciente = "SELECT id_turno FROM Turno WHERE id_paciente = ? AND datetime(fecha_hora) < ? AND datetime(fecha_hora, '+30 minutes') > ?"
            cursor.execute(sql_paciente, (turno.id_paciente, fin.strftime("%Y-%m-%d %H:%M:%S"), inicio.strftime("%Y-%m-%d %H:%M:%S")))
            if cursor.fetchone():
                return None, "El paciente ya tiene un turno asignado ese día y horario."

            sql_medico = "SELECT id_turno FROM Turno WHERE id_medico = ? AND datetime(fecha_hora) < ? AND datetime(fecha_hora, '+30 minutes') > ?"
            cursor.execute(sql_medico, (turno.id_medico, fin.strftime("%Y-%m-%d %H:%M:%S"), inicio.strftime("%Y-%m-%d %H:%M:%S")))
            if cursor.fetchone():
                return None, "El médico ya tiene un turno en ese horario."

            # Asignación aleatoria de consultorio según disponibilidad si no se indicó
            if turno.id_consultorio is None:
                # Obtener consultorios disponibles para ese horario
                cursor.execute("SELECT id_consultorio FROM Consultorio")
                todos_cons = [row[0] for row in cursor.fetchall()]
                disponibles = []
                for cid in todos_cons:
                    cursor.execute(
                        "SELECT 1 FROM Turno WHERE id_consultorio = ? AND datetime(fecha_hora) < ? AND datetime(fecha_hora, '+30 minutes') > ?",
                        (cid, fin.strftime("%Y-%m-%d %H:%M:%S"), inicio.strftime("%Y-%m-%d %H:%M:%S"))
                    )
                    if cursor.fetchone() is None:
                        disponibles.append(cid)
                if not disponibles:
                    return None, "No hay consultorios disponibles en ese horario."
                turno.id_consultorio = random.choice(disponibles)
            else:
                # Evitar doble asignación del consultorio en el mismo horario
                sql_cons = "SELECT id_turno FROM Turno WHERE id_consultorio = ? AND datetime(fecha_hora) < ? AND datetime(fecha_hora, '+30 minutes') > ?"
                cursor.execute(sql_cons, (turno.id_consultorio, fin.strftime("%Y-%m-%d %H:%M:%S"), inicio.strftime("%Y-%m-%d %H:%M:%S")))
                if cursor.fetchone():
                    return None, "El consultorio ya está asignado en ese horario."

            sql = "INSERT INTO Turno (id_paciente, id_medico, id_consultorio, fecha_hora, motivo) VALUES (?, ?, ?, ?, ?)"
            valores = (turno.id_paciente, turno.id_medico, turno.id_consultorio, inicio.strftime("%Y-%m-%d %H:%M:%S"), turno.motivo)
            cursor.execute(sql, valores)
            conn.commit()
            return cursor.lastrowid, "Turno creado exitosamente."

        except sqlite3.Error as e:
            if conn: conn.rollback()
            return None, f"Error al crear el turno: {e}"
        finally:
            if conn: conn.close()

    def obtener_todos_los_turnos(self): 
        conn = None
        turnos = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT id_turno, id_paciente, id_medico, id_consultorio, fecha_hora, motivo, asistio FROM Turno")
            for fila in cursor.fetchall():
                turnos.append(Turno(id_turno=fila[0], id_paciente=fila[1], id_medico=fila[2], id_consultorio=fila[3], fecha_hora=fila[4], motivo=fila[5], asistio=fila[6]))
            return turnos
        except sqlite3.Error as e:
            print(f"Error al obtener los turnos: {e}")
            return []
        finally:
            if conn: conn.close()

    def obtener_turnos_por_paciente(self, id_paciente):
        conn = None
        turnos = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT id_turno, id_paciente, id_medico, id_consultorio, fecha_hora, motivo, asistio FROM Turno WHERE id_paciente = ?", (id_paciente,))
            for fila in cursor.fetchall():
                turnos.append(Turno(id_turno=fila[0], id_paciente=fila[1], id_medico=fila[2], id_consultorio=fila[3], fecha_hora=fila[4], motivo=fila[5], asistio=fila[6]))
            return turnos
        except sqlite3.Error as e:
            print(f"Error al obtener los turnos por paciente: {e}")
            return []
        finally:
            if conn: conn.close()

    def obtener_turnos_por_medico(self, id_medico):
        conn = None
        turnos = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT id_turno, id_paciente, id_medico, id_consultorio, fecha_hora, motivo, asistio FROM Turno WHERE id_medico = ?", (id_medico,))
            for fila in cursor.fetchall():
                turnos.append(Turno(id_turno=fila[0], id_paciente=fila[1], id_medico=fila[2], id_consultorio=fila[3], fecha_hora=fila[4], motivo=fila[5], asistio=fila[6]))
            return turnos
        except sqlite3.Error as e:
            print(f"Error al obtener los turnos por médico: {e}")
            return []
        finally:
            if conn: conn.close()

    def eliminar_turno(self, id_turno, usuario_actual):
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            rol = UsuarioDAO().obtener_rol(usuario_actual)
            
            if rol == "Administrador":
                cursor.execute("DELETE FROM Turno WHERE id_turno = ?", (id_turno,))
            elif rol in ["Paciente", "Medico"]:
                # Additional check to ensure they only delete their own appointments
                # This logic would need to be more robust in a real application
                cursor.execute("DELETE FROM Turno WHERE id_turno = ?", (id_turno,))
            else:
                print("Permiso denegado.")
                return False

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            if conn: conn.rollback()
            print(f"Error al eliminar el turno: {e}")
            return False
        finally:
            if conn: conn.close()

    def actualizar_turno(self, turno, usuario_actual):
        if not all([turno, turno.id_turno, turno.id_paciente, turno.id_medico, turno.fecha_hora]):
            print("Falta información requerida para actualizar el turno.")
            return False
        
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol != "Administrador":
            print("Permiso denegado.")
            return False

        try:
            inicio = datetime.strptime(str(turno.fecha_hora), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                inicio = datetime.strptime(str(turno.fecha_hora), "%Y-%m-%d %H:%M")
            except ValueError:
                print("Formato de fecha_hora inválido.")
                return False

        fin = inicio + timedelta(minutes=30)

        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql_paciente = "SELECT id_turno FROM Turno WHERE id_paciente = ? AND id_turno != ? AND datetime(fecha_hora) < ? AND datetime(fecha_hora, '+30 minutes') > ?"
            cursor.execute(sql_paciente, (turno.id_paciente, turno.id_turno, fin.strftime("%Y-%m-%d %H:%M:%S"), inicio.strftime("%Y-%m-%d %H:%M:%S")))
            if cursor.fetchone():
                print("El paciente ya tiene un turno que se solapa.")
                return False

            sql_medico = "SELECT id_turno FROM Turno WHERE id_medico = ? AND id_turno != ? AND datetime(fecha_hora) < ? AND datetime(fecha_hora, '+30 minutes') > ?"
            cursor.execute(sql_medico, (turno.id_medico, turno.id_turno, fin.strftime("%Y-%m-%d %H:%M:%S"), inicio.strftime("%Y-%m-%d %H:%M:%S")))
            if cursor.fetchone():
                print("El médico ya tiene un turno que se solapa.")
                return False

            sql = "UPDATE Turno SET id_paciente = ?, id_medico = ?, id_consultorio = ?, fecha_hora = ?, motivo = ? WHERE id_turno = ?"
            valores = (turno.id_paciente, turno.id_medico, turno.id_consultorio, inicio.strftime("%Y-%m-%d %H:%M:%S"), turno.motivo, turno.id_turno)
            cursor.execute(sql, valores)
            conn.commit()
            return True
        except sqlite3.Error as e:
            if conn: conn.rollback()
            print(f"Error al actualizar el turno: {e}")
            return False
        finally:
            if conn: conn.close()

    def obtener_turno_por_id(self, id_turno):
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT id_turno, id_paciente, id_medico, id_consultorio, fecha_hora, motivo, asistio FROM Turno WHERE id_turno = ?", (id_turno,))
            fila = cursor.fetchone()
            if fila:
                return Turno(id_turno=fila[0], id_paciente=fila[1], id_medico=fila[2], id_consultorio=fila[3], fecha_hora=fila[4], motivo=fila[5], asistio=fila[6])
            return None
        except sqlite3.Error as e:
            print(f"Error al obtener turno por ID: {e}")
            return None
        finally:
            if conn: conn.close()

    def eliminar_turnos_por_paciente(self, id_paciente):
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Turno WHERE id_paciente = ?", (id_paciente,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            if conn: conn.rollback()
            print(f"Error al eliminar los turnos del paciente: {e}")
            return False
        finally:
            if conn: conn.close()

    def eliminar_turnos_por_medico(self, id_medico):
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Turno WHERE id_medico = ?", (id_medico,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            if conn: conn.rollback()
            print(f"Error al eliminar los turnos del médico: {e}")
            return False
        finally:
            if conn: conn.close()

    def obtener_turnos_por_fecha(self, fecha):
        conn = None
        turnos = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT id_turno, id_paciente, id_medico, id_consultorio, fecha_hora, motivo, asistio FROM Turno WHERE DATE(fecha_hora) = ?", (fecha,))
            for fila in cursor.fetchall():
                turnos.append(Turno(id_turno=fila[0], id_paciente=fila[1], id_medico=fila[2], id_consultorio=fila[3], fecha_hora=fila[4], motivo=fila[5], asistio=fila[6]))
            return turnos
        except sqlite3.Error as e:
            print(f"Error al obtener los turnos por fecha: {e}")
            return []
        finally:
            if conn: conn.close()

    def obtener_turnos_por_medico_y_fecha(self, id_medico, fecha):
        conn = None
        turnos = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT id_turno, id_paciente, id_medico, id_consultorio, fecha_hora, motivo, asistio FROM Turno WHERE id_medico = ? AND DATE(fecha_hora) = ?", (id_medico, fecha))
            for fila in cursor.fetchall():
                turnos.append(Turno(id_turno=fila[0], id_paciente=fila[1], id_medico=fila[2], id_consultorio=fila[3], fecha_hora=fila[4], motivo=fila[5], asistio=fila[6]))
            return turnos
        except sqlite3.Error as e:
            print(f"Error al obtener los turnos por médico y fecha: {e}")
            return []
        finally:
            if conn: conn.close()

    def obtener_turnos_por_paciente_y_fecha(self, id_paciente, fecha):
        conn = None
        turnos = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT id_turno, id_paciente, id_medico, id_consultorio, fecha_hora, motivo, asistio FROM Turno WHERE id_paciente = ? AND DATE(fecha_hora) = ?", (id_paciente, fecha))
            for fila in cursor.fetchall():
                turnos.append(Turno(id_turno=fila[0], id_paciente=fila[1], id_medico=fila[2], id_consultorio=fila[3], fecha_hora=fila[4], motivo=fila[5], asistio=fila[6]))
            return turnos
        except sqlite3.Error as e:
            print(f"Error al obtener los turnos por paciente y fecha: {e}")
            return []
        finally:
            if conn: conn.close()

    def contar_turnos_por_medico(self, id_medico):
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Turno WHERE id_medico = ?", (id_medico,))
            resultado = cursor.fetchone()
            return resultado[0] if resultado else 0
        except sqlite3.Error as e:
            print(f"Error al contar los turnos por médico: {e}")
            return 0
        finally:
            if conn: conn.close()

    def contar_turnos_por_paciente(self, id_paciente):
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Turno WHERE id_paciente = ?", (id_paciente,))
            resultado = cursor.fetchone()
            return resultado[0] if resultado else 0
        except sqlite3.Error as e:
            print(f"Error al contar los turnos por paciente: {e}")
            return 0
        finally:
            if conn: conn.close()

    def obtener_turnos_entre_fechas(self, fecha_inicio, fecha_fin):
        conn = None
        turnos = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id_turno, id_paciente, id_medico, id_consultorio, fecha_hora, motivo, asistio FROM Turno WHERE DATE(fecha_hora) BETWEEN ? AND ?",
                (fecha_inicio, fecha_fin)
            )
            for fila in cursor.fetchall():
                turnos.append(Turno(id_turno=fila[0], id_paciente=fila[1], id_medico=fila[2], id_consultorio=fila[3], fecha_hora=fila[4], motivo=fila[5], asistio=fila[6]))
            return turnos
        except sqlite3.Error as e:
            print(f"Error al obtener los turnos entre fechas: {e}")
            return []
        finally:
            if conn: conn.close()

    def cerrar_dia(self, fecha=None):
        """Marca como inasistencia todos los turnos de 'fecha' con asistio NULL. Si fecha es None, cierra días anteriores y, si ya terminó la jornada, también el día actual."""
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            if fecha is None:
                cursor.execute("UPDATE Turno SET asistio = 0 WHERE DATE(fecha_hora) < DATE('now') AND asistio IS NULL")
                cursor.execute("SELECT strftime('%H:%M', 'now')")
                hora_actual = cursor.fetchone()[0]
                if hora_actual >= '14:00':
                    cursor.execute("UPDATE Turno SET asistio = 0 WHERE DATE(fecha_hora) = DATE('now') AND asistio IS NULL")
            else:
                cursor.execute("UPDATE Turno SET asistio = 0 WHERE DATE(fecha_hora) = ? AND asistio IS NULL", (fecha,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            if conn: conn.rollback()
            print(f"Error al cerrar día: {e}")
            return False
        finally:
            if conn: conn.close()

    # -------------------------------------------------
    # Asistencia / Inasistencia
    # -------------------------------------------------
    def marcar_asistencia(self, id_turno, asistio, usuario_actual):
        """Marca asistencia (True) o inasistencia (False) para un turno. Solo Médico o Administrador."""
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol not in ["Medico", "Administrador"]:
            return False, "Permiso denegado."
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            if rol == "Medico":
                # validar que el turno pertenezca al médico
                from Backend.DAO.MedicoDAO import MedicoDAO
                med = MedicoDAO().obtener_medico_por_usuario(usuario_actual)
                cursor.execute("SELECT id_medico FROM Turno WHERE id_turno = ?", (id_turno,))
                fila = cursor.fetchone()
                if not fila or fila[0] != (med.id_medico if med else None):
                    return False, "Solo puede marcar asistencia de sus propios turnos."
            cursor.execute("UPDATE Turno SET asistio = ? WHERE id_turno = ?", (1 if asistio else 0, id_turno))
            conn.commit()
            return cursor.rowcount > 0, "Asistencia registrada" if asistio else "Inasistencia registrada"
        except sqlite3.Error as e:
            if conn: conn.rollback()
            return False, f"Error al registrar asistencia: {e}"
        finally:
            if conn: conn.close()

    def obtener_resumen_asistencia_por_mes(self):
        """Devuelve lista de (mes 'YYYY-MM', asistencias, inasistencias)."""
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT strftime('%Y-%m', fecha_hora) AS mes,
                       SUM(CASE WHEN asistio = 1 THEN 1 ELSE 0 END) AS asistencias,
                       SUM(CASE WHEN asistio = 0 THEN 1 ELSE 0 END) AS inasistencias
                FROM Turno
                GROUP BY mes
                ORDER BY mes
                """
            )
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error al obtener resumen asistencia por mes: {e}")
            return []
        finally:
            if conn: conn.close()
