
import sqlite3
# Mantenemos el estilo de importación que usa tu proyecto:
from Backend.BDD.Conexion import get_conexion 
from Backend.Model.FranjaHoraria import FranjaHoraria 
from datetime import datetime, time

class FranjaHorariaDAO:

    def validar_franja_laboral(self, id_medico, dia_semana, inicio, fin):
        """
        Verifica si el turno solicitado (inicio/fin) cae DENTRO de una franja laboral.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            hora_inicio_turno = inicio.strftime("%H:%M")
            hora_fin_turno = fin.strftime("%H:%M") 

            # Consulta: Busca una franja laboral que CUBRA el turno.
            sql = """
            SELECT id_franja FROM FranjaHoraria 
            WHERE id_medico = ? AND dia_semana = ?
              AND hora_inicio <= ? 
              AND hora_fin >= ? 
            """

            cursor.execute(sql, (id_medico, dia_semana, hora_inicio_turno, hora_fin_turno))

            resultado = cursor.fetchone()
            return resultado is not None, "Franja laboral válida." if resultado else "El médico no trabaja en ese horario o la hora solicitada está fuera de su franja laboral."

        except sqlite3.Error as e:
            print(f"Error en validación de franja laboral: {e}")
            return False, f"Error de base de datos al validar franja: {e}"
        finally:
            if conn: conn.close()

    # --- MÉTODOS CRUD BÁSICOS ---

    def insertar(self, franja):
        """Inserta una nueva franja horaria para un médico."""
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            sql = "INSERT INTO FranjaHoraria (id_medico, dia_semana, hora_inicio, hora_fin) VALUES (?, ?, ?, ?)"
            valores = (franja.id_medico, franja.dia_semana, franja.hora_inicio, franja.hora_fin)
            cursor.execute(sql, valores)
            conn.commit()
            return cursor.lastrowid, "Franja horaria insertada exitosamente."
        except sqlite3.Error as e:
            if conn: conn.rollback()
            print(f"Error al insertar franja horaria: {e}")
            return None, f"Error de base de datos al insertar franja: {e}"
        finally:
            if conn: conn.close()

    def obtener_por_medico(self, id_medico):
        """Obtiene TODAS las franjas horarias de un médico."""
        conn = None
        franjas = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            sql = "SELECT * FROM FranjaHoraria WHERE id_medico = ?"
            cursor.execute(sql, (id_medico,))

            for fila in cursor.fetchall():
                franjas.append(FranjaHoraria(id_franja=fila[0], id_medico=fila[1], 
                                           dia_semana=fila[2], hora_inicio=fila[3], 
                                           hora_fin=fila[4]))
            return franjas
        except sqlite3.Error as e:
            print(f"Error al obtener franjas por médico: {e}")
            return []
        finally:
            if conn: conn.close()


    def eliminar(self, id_franja):
        """Elimina una franja horaria específica por su ID."""
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            sql = "DELETE FROM FranjaHoraria WHERE id_franja = ?"
            cursor.execute(sql, (id_franja,))
            conn.commit()
            return cursor.rowcount > 0, "Franja horaria eliminada exitosamente." if cursor.rowcount > 0 else "No se encontró la franja horaria."
        except sqlite3.Error as e:
            if conn: conn.rollback()
            print(f"Error al eliminar franja horaria: {e}")
            return False, f"Error de base de datos al eliminar franja: {e}"
        finally:
            if conn: conn.close()

    def actualizar(self, id_franja, dia_semana, hora_inicio, hora_fin):
        """Actualiza una franja horaria existente."""
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            sql = """
            UPDATE FranjaHoraria SET dia_semana = ?, hora_inicio = ?, hora_fin = ?
            WHERE id_franja = ?
            """
            cursor.execute(sql, (dia_semana, hora_inicio, hora_fin, id_franja))
            conn.commit()
            return cursor.rowcount > 0, "Franja horaria actualizada exitosamente." if cursor.rowcount > 0 else "No se encontró la franja horaria."
        except sqlite3.Error as e:
            if conn: conn.rollback()
            print(f"Error al actualizar franja horaria: {e}")
            return False, f"Error de base de datos al actualizar franja: {e}"
        finally:
            if conn: conn.close()
