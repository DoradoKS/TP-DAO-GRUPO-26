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
        # Validaciones básicas de campos requeridos
        if not turno or not turno.id_paciente or not turno.id_medico or not turno.fecha_hora:
            print("Falta información requerida para crear el turno (paciente, médico o fecha_hora).")
            return None
        # Permisos: solo Administrador puede crear turnos
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol != "Administrador":
            print("Permiso denegado: solo Administrador puede crear turnos.")
            return None

        # Parsear fecha/hora y calcular ventana (30 minutos)
        try:
            # Acepta 'YYYY-MM-DD HH:MM' o 'YYYY-MM-DD HH:MM:SS'
            try:
                inicio = datetime.strptime(str(turno.fecha_hora), "%Y-%m-%d %H:%M:%S")
            except ValueError:
                inicio = datetime.strptime(str(turno.fecha_hora), "%Y-%m-%d %H:%M")
        except ValueError:
            print("Formato de fecha_hora inválido. Use 'YYYY-MM-DD HH:MM' o 'YYYY-MM-DD HH:MM:SS'.")
            return None

        fin = inicio + timedelta(minutes=30)

        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            # 1) Verificar si el paciente ya tiene un turno que se solapa
            sql_paciente = (
                "SELECT id_turno, fecha_hora FROM Turno "
                "WHERE id_paciente = ? AND datetime(fecha_hora) < ? "
                "AND datetime(fecha_hora, '+30 minutes') > ?"
            )
            cursor.execute(sql_paciente, (turno.id_paciente, fin.strftime("%Y-%m-%d %H:%M:%S"), inicio.strftime("%Y-%m-%d %H:%M:%S")))
            conflicto_paciente = cursor.fetchone()
            if conflicto_paciente:
                print("El paciente ya tiene un turno en ese día/hora (conflicto con id_turno={} hora={}).".format(conflicto_paciente[0], conflicto_paciente[1]))
                return None

            # 2) Verificar si el médico ya tiene un turno que se solapa
            sql_medico = (
                "SELECT id_turno, fecha_hora FROM Turno "
                "WHERE id_medico = ? AND datetime(fecha_hora) < ? "
                "AND datetime(fecha_hora, '+30 minutes') > ?"
            )
            cursor.execute(sql_medico, (turno.id_medico, fin.strftime("%Y-%m-%d %H:%M:%S"), inicio.strftime("%Y-%m-%d %H:%M:%S")))
            conflicto_medico = cursor.fetchone()
            if conflicto_medico:
                print("El médico ya tiene un turno en ese día/hora (conflicto con id_turno={} hora={}).".format(conflicto_medico[0], conflicto_medico[1]))
                return None

            # Si no hay conflictos, insertar
            sql = """
            INSERT INTO Turno (
                id_paciente, id_medico, fecha_hora, motivo
            ) VALUES (?, ?, ?, ?)
            """
            
            valores = (
                turno.id_paciente, turno.id_medico,
                inicio.strftime("%Y-%m-%d %H:%M:%S"), turno.motivo
            )

            cursor.execute(sql, valores)
            conn.commit()
            print("Turno creado exitosamente.")
            return cursor.lastrowid # Retorna el ID del nuevo turno

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al crear el turno: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def obtener_todos_los_turnos(self): 
        """
        Retorna una lista de todos los turnos como objetos Turno.
        """
        conn = None
        turnos = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM Turno"
            cursor.execute(sql)
            filas = cursor.fetchall()

            for fila in filas:
                turno = Turno(
                    id_turno=fila[0],
                    id_paciente=fila[1],
                    id_medico=fila[2],
                    fecha_hora=fila[3],
                    motivo=fila[4]
                )
                turnos.append(turno)

            return turnos

        except sqlite3.Error as e:
            print(f"Error al obtener los turnos: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def obtener_turnos_por_paciente(self, id_paciente):
        """
        Retorna una lista de turnos para un paciente específico.
        """
        conn = None
        turnos = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM Turno WHERE id_paciente = ?"
            cursor.execute(sql, (id_paciente,))
            filas = cursor.fetchall()

            for fila in filas:
                turno = Turno(
                    id_turno=fila[0],
                    id_paciente=fila[1],
                    id_medico=fila[2],
                    fecha_hora=fila[3],
                    motivo=fila[4]
                )
                turnos.append(turno)

            return turnos

        except sqlite3.Error as e:
            print(f"Error al obtener los turnos por paciente: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def obtener_turnos_por_medico(self, id_medico):
        """
        Retorna una lista de turnos para un médico específico.
        """
        conn = None
        turnos = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM Turno WHERE id_medico = ?"
            cursor.execute(sql, (id_medico,))
            filas = cursor.fetchall()

            for fila in filas:
                turno = Turno(
                    id_turno=fila[0],
                    id_paciente=fila[1],
                    id_medico=fila[2],
                    fecha_hora=fila[3],
                    motivo=fila[4]
                )
                turnos.append(turno)

            return turnos

        except sqlite3.Error as e:
            print(f"Error al obtener los turnos por médico: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def eliminar_turno(self, id_turno, usuario_actual):
        """
        Elimina un turno dado su ID.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            # Permisos: solo Administrador puede eliminar turnos
            rol = UsuarioDAO().obtener_rol(usuario_actual)
            if rol != "Administrador":
                print("Permiso denegado: solo Administrador puede eliminar turnos.")
                return False
            sql = "DELETE FROM Turno WHERE id_turno = ?"
            cursor.execute(sql, (id_turno,))
            conn.commit()
            print("Turno eliminado exitosamente.")
            return True

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al eliminar el turno: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def actualizar_turno(self, turno, usuario_actual):
        """
        Actualiza los datos de un turno en la DB, buscando por id_turno.
        """
        # Validaciones básicas
        if not turno or not turno.id_turno or not turno.id_paciente or not turno.id_medico or not turno.fecha_hora:
            print("Falta información requerida para actualizar el turno.")
            return False
        # Permisos: solo Administrador puede actualizar turnos
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol != "Administrador":
            print("Permiso denegado: solo Administrador puede actualizar turnos.")
            return False

        # Parsear fecha/hora y calcular ventana (30 minutos)
        try:
            try:
                inicio = datetime.strptime(str(turno.fecha_hora), "%Y-%m-%d %H:%M:%S")
            except ValueError:
                inicio = datetime.strptime(str(turno.fecha_hora), "%Y-%m-%d %H:%M")
        except ValueError:
            print("Formato de fecha_hora inválido. Use 'YYYY-MM-DD HH:MM' o 'YYYY-MM-DD HH:MM:SS'.")
            # Permisos: solo Administrador puede eliminar turnos
            rol = UsuarioDAO().obtener_rol(usuario_actual)
            if rol != "Administrador":
                print("Permiso denegado: solo Administrador puede eliminar turnos.")
                return False
            return False

        fin = inicio + timedelta(minutes=30)

        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            # Verificar conflictos para paciente (excluyendo el turno actual)
            sql_paciente = (
                "SELECT id_turno, fecha_hora FROM Turno "
                "WHERE id_paciente = ? AND id_turno != ? AND datetime(fecha_hora) < ? "
                "AND datetime(fecha_hora, '+30 minutes') > ?"
            )
            cursor.execute(sql_paciente, (turno.id_paciente, turno.id_turno, fin.strftime("%Y-%m-%d %H:%M:%S"), inicio.strftime("%Y-%m-%d %H:%M:%S")))
            conflicto_paciente = cursor.fetchone()
            if conflicto_paciente:
                print("❌ El paciente ya tiene un turno que se solapa (id_turno={} hora={}).".format(conflicto_paciente[0], conflicto_paciente[1]))
                return False

            # Verificar conflictos para medico (excluyendo el turno actual)
            sql_medico = (
                "SELECT id_turno, fecha_hora FROM Turno "
                "WHERE id_medico = ? AND id_turno != ? AND datetime(fecha_hora) < ? "
                "AND datetime(fecha_hora, '+30 minutes') > ?"
            )
            cursor.execute(sql_medico, (turno.id_medico, turno.id_turno, fin.strftime("%Y-%m-%d %H:%M:%S"), inicio.strftime("%Y-%m-%d %H:%M:%S")))
            conflicto_medico = cursor.fetchone()
            if conflicto_medico:
                print("❌ El médico ya tiene un turno que se solapa (id_turno={} hora={}).".format(conflicto_medico[0], conflicto_medico[1]))
                return False

            # Si no hay conflictos, actualizar
            sql = """
            UPDATE Turno SET 
                id_paciente = ?, id_medico = ?, fecha_hora = ?, motivo = ?
            WHERE id_turno = ?
            """
            
            valores = (
                turno.id_paciente, turno.id_medico,
                inicio.strftime("%Y-%m-%d %H:%M:%S"), turno.motivo,
                turno.id_turno # ID para el WHERE
            )

            cursor.execute(sql, valores)
            conn.commit()
            print("Turno actualizado exitosamente.")
            return True

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al actualizar el turno: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def obtener_turno_por_id(self, id_turno):
        """
        Retorna un objeto Turno dado su ID.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM Turno WHERE id_turno = ?"
            cursor.execute(sql, (id_turno,))
            fila = cursor.fetchone()

            if fila:
                turno = Turno(
                    id_turno=fila[0],
                    id_paciente=fila[1],
                    id_medico=fila[2],
                    fecha_hora=fila[3],
                    motivo=fila[4]
                )
                return turno
            else:
                return None

        except sqlite3.Error as e:
            print(f"Error al obtener turno por ID: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def eliminar_turnos_por_paciente(self, id_paciente):
        """
        Elimina todos los turnos asociados a un paciente específico.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "DELETE FROM Turno WHERE id_paciente = ?"
            cursor.execute(sql, (id_paciente,))
            conn.commit()
            print("Turnos del paciente eliminados exitosamente.")
            return True

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al eliminar los turnos del paciente: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def eliminar_turnos_por_medico(self, id_medico):
        """
        Elimina todos los turnos asociados a un médico específico.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "DELETE FROM Turno WHERE id_medico = ?"
            cursor.execute(sql, (id_medico,))
            conn.commit()
            print("Turnos del médico eliminados exitosamente.")
            return True

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al eliminar los turnos del médico: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def obtener_turnos_por_fecha(self, fecha):
        """
        Retorna una lista de turnos para una fecha específica.
        """
        conn = None
        turnos = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM Turno WHERE DATE(fecha_hora) = ?"
            cursor.execute(sql, (fecha,))
            filas = cursor.fetchall()

            for fila in filas:
                turno = Turno(
                    id_turno=fila[0],
                    id_paciente=fila[1],
                    id_medico=fila[2],
                    fecha_hora=fila[3],
                    motivo=fila[4]
                )
                turnos.append(turno)

            return turnos

        except sqlite3.Error as e:
            print(f"Error al obtener los turnos por fecha: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def obtener_turnos_por_medico_y_fecha(self, id_medico, fecha):
        """
        Retorna una lista de turnos para un médico específico en una fecha dada.
        """
        conn = None
        turnos = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM Turno WHERE id_medico = ? AND DATE(fecha_hora) = ?"
            cursor.execute(sql, (id_medico, fecha))
            filas = cursor.fetchall()

            for fila in filas:
                turno = Turno(
                    id_turno=fila[0],
                    id_paciente=fila[1],
                    id_medico=fila[2],
                    fecha_hora=fila[3],
                    motivo=fila[4]
                )
                turnos.append(turno)

            return turnos

        except sqlite3.Error as e:
            print(f"Error al obtener los turnos por médico y fecha: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def obtener_turnos_por_paciente_y_fecha(self, id_paciente, fecha):
        """
        Retorna una lista de turnos para un paciente específico en una fecha dada.
        """
        conn = None
        turnos = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM Turno WHERE id_paciente = ? AND DATE(fecha_hora) = ?"
            cursor.execute(sql, (id_paciente, fecha))
            filas = cursor.fetchall()

            for fila in filas:
                turno = Turno(
                    id_turno=fila[0],
                    id_paciente=fila[1],
                    id_medico=fila[2],
                    fecha_hora=fila[3],
                    motivo=fila[4]
                )
                turnos.append(turno)

            return turnos

        except sqlite3.Error as e:
            print(f"Error al obtener los turnos por paciente y fecha: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def contar_turnos_por_medico(self, id_medico):
        """
        Retorna el número total de turnos asignados a un médico específico.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT COUNT(*) FROM Turno WHERE id_medico = ?"
            cursor.execute(sql, (id_medico,))
            resultado = cursor.fetchone()

            if resultado:
                return resultado[0]  # Retorna el conteo
            else:
                return 0

        except sqlite3.Error as e:
            print(f"Error al contar los turnos por médico: {e}")
            return 0
        finally:    
            if conn:
                conn.close()

    def contar_turnos_por_paciente(self, id_paciente):
        """
        Retorna el número total de turnos asignados a un paciente específico.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT COUNT(*) FROM Turno WHERE id_paciente = ?"
            cursor.execute(sql, (id_paciente,))
            resultado = cursor.fetchone()

            if resultado:
                return resultado[0]  # Retorna el conteo
            else:
                return 0

        except sqlite3.Error as e:
            print(f"Error al contar los turnos por paciente: {e}")
            return 0
        finally:    
            if conn:
                conn.close()

    def obtener_turnos_entre_fechas(self, fecha_inicio, fecha_fin):
        """
        Retorna una lista de turnos entre dos fechas específicas.
        """
        conn = None
        turnos = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM Turno WHERE DATE(fecha_hora) BETWEEN ? AND ?"
            cursor.execute(sql, (fecha_inicio, fecha_fin))
            filas = cursor.fetchall()

            for fila in filas:
                turno = Turno(
                    id_turno=fila[0],
                    id_paciente=fila[1],
                    id_medico=fila[2],
                    fecha_hora=fila[3],
                    motivo=fila[4]
                )
                turnos.append(turno)

            return turnos

        except sqlite3.Error as e:
            print(f"Error al obtener los turnos entre fechas: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def obtener_turnos_por_estado(self, estado):
        """
        Retorna una lista de turnos según su estado (por ejemplo, 'confirmado', 'cancelado').
        """
        conn = None
        turnos = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM Turno WHERE estado = ?"
            cursor.execute(sql, (estado,))
            filas = cursor.fetchall()

            for fila in filas:
                turno = Turno(
                    id_turno=fila[0],
                    id_paciente=fila[1],
                    id_medico=fila[2],
                    fecha_hora=fila[3],
                    motivo=fila[4]
                )
                turnos.append(turno)

            return turnos

        except sqlite3.Error as e:
            print(f"Error al obtener los turnos por estado: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def actualizar_estado_turno(self, id_turno, nuevo_estado):
        """
        Actualiza el estado de un turno dado su ID.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "UPDATE Turno SET estado = ? WHERE id_turno = ?"
            cursor.execute(sql, (nuevo_estado, id_turno))
            conn.commit()
            print("Estado del turno actualizado exitosamente.")
            return True

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al actualizar el estado del turno: {e}")
            return False
        finally:
            if conn:
                conn.close()

    