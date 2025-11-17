import sqlite3      
import random

from Backend.BDD.Conexion import get_conexion
from Backend.Model.Turno import Turno
from Backend.DAO.UsuarioDAO import UsuarioDAO
from Backend.DAO.FranjaHorariaDAO import FranjaHorariaDAO
import calendar
from datetime import datetime, timedelta

def _add_one_month(dt_date):
    """Return a date one month after dt_date, preserving day when possible.
    If the next month has fewer days, use the month's last day."""
    year = dt_date.year
    month = dt_date.month + 1
    if month == 13:
        month = 1
        year += 1
    day = dt_date.day
    import calendar
    last_day = calendar.monthrange(year, month)[1]
    if day > last_day:
        day = last_day
    from datetime import date
    return date(year, month, day)

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

        # Validación: no permitir turnos con fecha mayor a 1 mes desde hoy
        hoy = datetime.now().date()
        fecha_max = _add_one_month(hoy)
        if inicio.date() > fecha_max:
            return None, f"No se puede reservar un turno con más de un mes de anticipación. Fecha máxima permitida: {fecha_max.strftime('%Y-%m-%d')}"

        fin = inicio + timedelta(minutes=30)
        # --- NUEVA VALIDACIÓN: FRONTAL DE LA TRANSACCIÓN (FRANJA LABORAL) ---
        dia_semana_py = inicio.weekday() + 1 # Monday=0, so add 1 (1=Lunes)

        # Llama al nuevo DAO para verificar si el médico trabaja en ese slot
        franja_valida, franja_msg = FranjaHorariaDAO().validar_franja_laboral(turno.id_medico, dia_semana_py, inicio, fin)
        if not franja_valida:
            print(franja_msg) # Para debug
            return None, franja_msg # Aseguramos que siempre devuelve una tupla
        # ---------------------------------------------------------------------

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
            new_id = cursor.lastrowid
            # Notificar al paciente (no bloquear la creación si falla el email)
            try:
                import Backend.notifications as notifications
                try:
                    notifications.send_turno_created(new_id)
                except Exception as e:
                    print(f"Advertencia: no se pudo enviar email de creación de turno: {e}")
            except Exception:
                # Si no se puede importar el módulo de notificaciones, ignoramos
                pass
            return new_id, "Turno creado exitosamente."

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

            # Obtener datos del turno antes de borrarlo para notificar
            turno_obj = None
            try:
                turno_obj = self.obtener_turno_por_id(id_turno)
            except Exception:
                turno_obj = None

            if rol == "Administrador":
                cursor.execute("DELETE FROM Turno WHERE id_turno = ?", (id_turno,))
            elif rol in ["Paciente", "Medico"]:
                cursor.execute("DELETE FROM Turno WHERE id_turno = ?", (id_turno,))
            else:
                print("Permiso denegado.")
                return False

            conn.commit()
            deleted = cursor.rowcount > 0
            if deleted:
                # Notificar al paciente sobre la cancelación (usando el objeto turno obtenido antes de borrarlo)
                try:
                    import Backend.notifications as notifications
                    quien = 'el administrador' if rol == 'Administrador' else ('el paciente' if rol == 'Paciente' else 'el médico')
                    try:
                        if turno_obj:
                            notifications.send_turno_cancelled(turno_obj, quien=quien)
                        else:
                            notifications.send_turno_cancelled(id_turno, quien=quien)
                    except Exception as e:
                        print(f"Advertencia: no se pudo enviar email de cancelación de turno: {e}")
                except Exception:
                    pass
            return deleted
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

        # Validación: no permitir turnos con fecha mayor a 1 mes desde hoy
        hoy = datetime.now().date()
        fecha_max = _add_one_month(hoy)
        if inicio.date() > fecha_max:
            print(f"No se puede reservar un turno con más de un mes de anticipación. Fecha máxima permitida: {fecha_max.strftime('%Y-%m-%d')}")
            return False

        fin = inicio + timedelta(minutes=30)
        # --- NUEVA VALIDACIÓN: FRONTAL DE LA TRANSACCIÓN (FRANJA LABORAL) ---
        dia_semana_py = inicio.weekday() + 1 # Monday=0, so add 1 (1=Lunes)

        # Llama al nuevo DAO para verificar si el médico trabaja en ese slot
        franja_valida, franja_msg = FranjaHorariaDAO().validar_franja_laboral(turno.id_medico, dia_semana_py, inicio, fin)
        if not franja_valida:
            print(franja_msg) # Para debug
            return False, franja_msg # Aseguramos que siempre devuelve una tupla
        # ---------------------------------------------------------------------

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

# --- NUEVO MÉTODO CRUCIAL: CÁLCULO DE DISPONIBILIDAD ---

    def calcular_horarios_disponibles(self, id_medico, fecha):
        """
        Calcula los slots libres (30 min) combinando franjas laborales y turnos ocupados.
        Retorna una lista de strings con los horarios disponibles ('HH:MM').
        """
        DURACION_MINUTOS = 30
        
        try:
            # Convertir la fecha solicitada a día de la semana (1-7)
            fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
            dia_semana_py = fecha_dt.weekday() + 1 # Lunes=1
        except ValueError:
            print("Formato de fecha de entrada inválido. Use YYYY-MM-DD.")
            return [] # Retorna lista vacía si la fecha es mala

        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            
            # 1. Obtener Franjas de Trabajo (Las "Franjas Largas")
            sql_franja = "SELECT hora_inicio, hora_fin FROM FranjaHoraria WHERE id_medico = ? AND dia_semana = ?"
            cursor.execute(sql_franja, (id_medico, dia_semana_py))
            franjas_trabajo = cursor.fetchall()
            
            if not franjas_trabajo:
                 print(f"Debug: No se encontraron franjas laborales para el médico {id_medico} el día {dia_semana_py}.")
                 return [] # El médico no trabaja ese día
            
            # 2. Obtener Horarios Reservados (Las "Excepciones")
            sql_reservados = "SELECT strftime('%H:%M', fecha_hora) FROM Turno WHERE id_medico = ? AND DATE(fecha_hora) = ?"
            cursor.execute(sql_reservados, (id_medico, fecha))
            # Usamos un 'set' para que la búsqueda sea ultra-rápida
            turnos_reservados = {row[0] for row in cursor.fetchall()} 
            
            horarios_libres = []
            
            # 3. Calcular Slots Libres (Lógica Python)
            for inicio_str, fin_str in franjas_trabajo:
                
                # Convertimos los strings de hora a objetos datetime para poder sumarles tiempo
                hora_actual = datetime.strptime(f"{fecha} {inicio_str}", "%Y-%m-%d %H:%M")
                hora_fin = datetime.strptime(f"{fecha} {fin_str}", "%Y-%m-%d %H:%M")
                
                # Iteramos cada slot de 30 minutos
                while hora_actual < hora_fin:
                    slot_inicio_str = hora_actual.strftime('%H:%M')
                    
                    # Si el slot NO está en la lista de reservados, lo agregamos
                    if slot_inicio_str not in turnos_reservados:
                        horarios_libres.append(slot_inicio_str)
                        
                    # Avanzamos al siguiente slot
                    hora_actual += timedelta(minutes=DURACION_MINUTOS) 
                    
            print(f"Debug: Horarios libres encontrados: {horarios_libres}")
            return horarios_libres
        except sqlite3.Error as e:
            print(f"Error al calcular disponibilidad: {e}")
            return []
        finally:
            if conn: conn.close()

    def calcular_horarios_con_estado(self, id_medico, fecha):
        """
        Devuelve todos los slots (de 30 minutos) del día para el médico indicando si están ocupados.
        Retorna una lista de tuplas: (hora 'HH:MM', ocupado_bool, dict_info)
        dict_info puede contener: {'id_turno':..., 'id_paciente':..., 'paciente_nombre':...} cuando esté ocupado, o None cuando esté libre.
        """
        DURACION_MINUTOS = 30
        try:
            fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
            dia_semana_py = fecha_dt.weekday() + 1
        except ValueError:
            print("Formato de fecha de entrada inválido. Use YYYY-MM-DD.")
            return []

        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            # Obtener franjas laborales
            sql_franja = "SELECT hora_inicio, hora_fin FROM FranjaHoraria WHERE id_medico = ? AND dia_semana = ?"
            cursor.execute(sql_franja, (id_medico, dia_semana_py))
            franjas_trabajo = cursor.fetchall()
            if not franjas_trabajo:
                return []

            # Obtener turnos reservados con la hora exacta (HH:MM) y datos de paciente
            # Traemos también el nombre del paciente para mostrarlo en la UI
            sql_reservados = ("SELECT T.id_turno, T.id_paciente, P.nombre, P.apellido, strftime('%H:%M', T.fecha_hora) as hora "
                              "FROM Turno T LEFT JOIN Paciente P ON T.id_paciente = P.id_paciente "
                              "WHERE T.id_medico = ? AND DATE(T.fecha_hora) = ?")
            cursor.execute(sql_reservados, (id_medico, fecha))
            reservados = {row[4]: {'id_turno': row[0], 'id_paciente': row[1], 'paciente_nombre': f"{row[2]} {row[3]}".strip()} for row in cursor.fetchall()}

            horarios = []
            for inicio_str, fin_str in franjas_trabajo:
                hora_actual = datetime.strptime(f"{fecha} {inicio_str}", "%Y-%m-%d %H:%M")
                hora_fin = datetime.strptime(f"{fecha} {fin_str}", "%Y-%m-%d %H:%M")
                while hora_actual < hora_fin:
                    slot_inicio_str = hora_actual.strftime('%H:%M')
                    info = None
                    ocupado = False
                    if slot_inicio_str in reservados:
                        ocupado = True
                        info = reservados[slot_inicio_str]
                    horarios.append((slot_inicio_str, ocupado, info))
                    hora_actual += timedelta(minutes=DURACION_MINUTOS)

            return horarios
        except sqlite3.Error as e:
            print(f"Error al calcular disponibilidad con estado: {e}")
            return []
        finally:
            if conn: conn.close()
    # --- MÉTODOS DE REPORTES ---

    def reporte_turnos_por_medico_y_periodo(self, id_medico, fecha_inicio, fecha_fin):
        """
        Reporte 1: Listado de turnos para un médico en un rango de fechas.
        """
        conn = None
        turnos = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            sql = """
            SELECT * FROM Turno 
            WHERE id_medico = ? 
              AND DATE(fecha_hora) BETWEEN ? AND ?
            ORDER BY fecha_hora
            """
            cursor.execute(sql, (id_medico, fecha_inicio, fecha_fin))
            for fila in cursor.fetchall():
                # Asumo la estructura de tu constructor de Turno
                turnos.append(Turno(id_turno=fila[0], id_paciente=fila[1], id_medico=fila[2], 
                                  id_consultorio=fila[3], fecha_hora=fila[4], motivo=fila[5], asistio=fila[6]))
            return turnos
        except sqlite3.Error as e:
            print(f"Error en reporte de turnos por médico: {e}")
            return []
        finally:
            if conn: conn.close()

    def reporte_cantidad_turnos_por_especialidad(self):
        """
        Reporte 2: Cantidad de turnos agrupados por especialidad.
        Usa JOIN para conectar Turno -> Medico -> Especialidad.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            # Esta es una consulta compleja que une 3 tablas
            sql = """
            SELECT E.nombre, COUNT(T.id_turno) AS Cantidad
            FROM Turno AS T
            JOIN Medico AS M ON T.id_medico = M.id_medico
            JOIN Especialidad AS E ON M.id_especialidad = E.id_especialidad
            GROUP BY E.nombre
            ORDER BY Cantidad DESC
            """
            cursor.execute(sql)
            return cursor.fetchall() # Retorna una lista de tuplas (nombre_especialidad, cantidad)
        except sqlite3.Error as e:
            print(f"Error en reporte de turnos por especialidad: {e}")
            return []
        finally:
            if conn: conn.close()

    def reporte_cantidad_turnos_por_especialidad_periodo(self, fecha_inicio, fecha_fin):
        """
        Reporte: Cantidad de turnos por especialidad dentro de un rango de fechas.
        Retorna lista de tuplas (nombre_especialidad, cantidad)
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            sql = (
                "SELECT E.nombre, COUNT(T.id_turno) AS Cantidad\n"
                "FROM Turno AS T\n"
                "JOIN Medico AS M ON T.id_medico = M.id_medico\n"
                "JOIN Especialidad AS E ON M.id_especialidad = E.id_especialidad\n"
                "WHERE DATE(T.fecha_hora) BETWEEN ? AND ?\n"
                "GROUP BY E.nombre\n"
                "ORDER BY Cantidad DESC"
            )
            cursor.execute(sql, (fecha_inicio, fecha_fin))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error en reporte de turnos por especialidad (periodo): {e}")
            return []
        finally:
            if conn: conn.close()

    def reporte_asistencia_por_periodo(self, fecha_inicio, fecha_fin):
        """Devuelve tupla (asistencias, inasistencias, pendientes) para el rango de fechas dado."""
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            sql = (
                "SELECT\n"
                "  SUM(CASE WHEN asistio = 1 THEN 1 ELSE 0 END) AS Asistencias,\n"
                "  SUM(CASE WHEN asistio = 0 THEN 1 ELSE 0 END) AS Inasistencias,\n"
                "  SUM(CASE WHEN asistio IS NULL THEN 1 ELSE 0 END) AS Pendientes\n"
                "FROM Turno\n"
                "WHERE DATE(fecha_hora) BETWEEN ? AND ?"
            )
            cursor.execute(sql, (fecha_inicio, fecha_fin))
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error en reporte de asistencias por periodo: {e}")
            return []
        finally:
            if conn: conn.close()

    def reporte_asistencia_global(self):
        """
        Reporte 4: Conteo global de asistencias vs. inasistencias.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            sql = """
            SELECT
                SUM(CASE WHEN asistio = 1 THEN 1 ELSE 0 END) AS Asistencias,
                SUM(CASE WHEN asistio = 0 THEN 1 ELSE 0 END) AS Inasistencias,
                SUM(CASE WHEN asistio IS NULL THEN 1 ELSE 0 END) AS Pendientes
            FROM Turno
            """
            cursor.execute(sql)
            return cursor.fetchone() # Retorna una tupla (asist, inasist, pend)
        except sqlite3.Error as e:
            print(f"Error en reporte de asistencias: {e}")
            return []
        finally:
            if conn: conn.close()