import sqlite3      

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
        """
        if not all([turno, turno.id_paciente, turno.id_medico, turno.fecha_hora]):
            print("Falta información requerida para crear el turno.")
            return None

        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol not in ["Administrador", "Paciente"]:
            print("Permiso denegado.")
            return None

        try:
            inicio = datetime.strptime(str(turno.fecha_hora), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                inicio = datetime.strptime(str(turno.fecha_hora), "%Y-%m-%d %H:%M")
            except ValueError:
                print("Formato de fecha_hora inválido.")
                return None

        fin = inicio + timedelta(minutes=30)

        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql_paciente = "SELECT id_turno FROM Turno WHERE id_paciente = ? AND datetime(fecha_hora) < ? AND datetime(fecha_hora, '+30 minutes') > ?"
            cursor.execute(sql_paciente, (turno.id_paciente, fin.strftime("%Y-%m-%d %H:%M:%S"), inicio.strftime("%Y-%m-%d %H:%M:%S")))
            if cursor.fetchone():
                print("El paciente ya tiene un turno en ese horario.")
                return None

            sql_medico = "SELECT id_turno FROM Turno WHERE id_medico = ? AND datetime(fecha_hora) < ? AND datetime(fecha_hora, '+30 minutes') > ?"
            cursor.execute(sql_medico, (turno.id_medico, fin.strftime("%Y-%m-%d %H:%M:%S"), inicio.strftime("%Y-%m-%d %H:%M:%S")))
            if cursor.fetchone():
                print("El médico ya tiene un turno en ese horario.")
                return None

            sql = "INSERT INTO Turno (id_paciente, id_medico, fecha_hora, motivo) VALUES (?, ?, ?, ?)"
            valores = (turno.id_paciente, turno.id_medico, inicio.strftime("%Y-%m-%d %H:%M:%S"), turno.motivo)
            cursor.execute(sql, valores)
            conn.commit()
            return cursor.lastrowid

        except sqlite3.Error as e:
            if conn: conn.rollback()
            print(f"Error al crear el turno: {e}")
            return None
        finally:
            if conn: conn.close()

    def obtener_todos_los_turnos(self): 
        conn = None
        turnos = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Turno")
            for fila in cursor.fetchall():
                turnos.append(Turno(id_turno=fila[0], id_paciente=fila[1], id_medico=fila[2], fecha_hora=fila[3], motivo=fila[4]))
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
            cursor.execute("SELECT * FROM Turno WHERE id_paciente = ?", (id_paciente,))
            for fila in cursor.fetchall():
                turnos.append(Turno(id_turno=fila[0], id_paciente=fila[1], id_medico=fila[2], fecha_hora=fila[3], motivo=fila[4]))
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
            cursor.execute("SELECT * FROM Turno WHERE id_medico = ?", (id_medico,))
            for fila in cursor.fetchall():
                turnos.append(Turno(id_turno=fila[0], id_paciente=fila[1], id_medico=fila[2], fecha_hora=fila[3], motivo=fila[4]))
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

            sql = "UPDATE Turno SET id_paciente = ?, id_medico = ?, fecha_hora = ?, motivo = ? WHERE id_turno = ?"
            valores = (turno.id_paciente, turno.id_medico, inicio.strftime("%Y-%m-%d %H:%M:%S"), turno.motivo, turno.id_turno)
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
            cursor.execute("SELECT * FROM Turno WHERE id_turno = ?", (id_turno,))
            fila = cursor.fetchone()
            if fila:
                return Turno(id_turno=fila[0], id_paciente=fila[1], id_medico=fila[2], fecha_hora=fila[3], motivo=fila[4])
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
            cursor.execute("SELECT * FROM Turno WHERE DATE(fecha_hora) = ?", (fecha,))
            for fila in cursor.fetchall():
                turnos.append(Turno(id_turno=fila[0], id_paciente=fila[1], id_medico=fila[2], fecha_hora=fila[3], motivo=fila[4]))
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
            cursor.execute("SELECT * FROM Turno WHERE id_medico = ? AND DATE(fecha_hora) = ?", (id_medico, fecha))
            for fila in cursor.fetchall():
                turnos.append(Turno(id_turno=fila[0], id_paciente=fila[1], id_medico=fila[2], fecha_hora=fila[3], motivo=fila[4]))
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
            cursor.execute("SELECT * FROM Turno WHERE id_paciente = ? AND DATE(fecha_hora) = ?", (id_paciente, fecha))
            for fila in cursor.fetchall():
                turnos.append(Turno(id_turno=fila[0], id_paciente=fila[1], id_medico=fila[2], fecha_hora=fila[3], motivo=fila[4]))
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
            cursor.execute("SELECT * FROM Turno WHERE DATE(fecha_hora) BETWEEN ? AND ?", (fecha_inicio, fecha_fin))
            for fila in cursor.fetchall():
                turnos.append(Turno(id_turno=fila[0], id_paciente=fila[1], id_medico=fila[2], fecha_hora=fila[3], motivo=fila[4]))
            return turnos
        except sqlite3.Error as e:
            print(f"Error al obtener los turnos entre fechas: {e}")
            return []
        finally:
            if conn: conn.close()
