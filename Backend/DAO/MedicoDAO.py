import sqlite3
from Backend.BDD.Conexion import get_conexion
from Backend.Model.Medico import Medico
from Backend.Validaciones.validaciones import Validaciones
from Backend.DAO.UsuarioDAO import UsuarioDAO
from Backend.DAO.TurnoDAO import TurnoDAO

class MedicoDAO:
    """
    DAO para la entidad Medico.
    """

    def crear_medico(self, medico, usuario_actual):
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol not in ["Administrador"]:
            return None, "Permiso denegado."

        datos = {
            'usuario': medico.usuario, 'matricula': medico.matricula, 'nombre': medico.nombre,
            'apellido': medico.apellido, 'tipo_dni': medico.tipo_dni, 'dni': medico.dni,
            'email': medico.email, 'telefono': medico.telefono
        }
        es_valido, errores = Validaciones.validar_medico_completo(datos)
        if not es_valido:
            return None, "\n".join(errores)

        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            sql = """
            INSERT INTO Medico (usuario, matricula, nombre, apellido, tipo_dni, dni, 
                                calle, numero_calle, email, telefono, id_especialidad)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            valores = (
                medico.usuario, medico.matricula, medico.nombre, medico.apellido,
                medico.tipo_dni, medico.dni, medico.calle, medico.numero_calle,
                medico.email, medico.telefono, medico.id_especialidad
            )
            cursor.execute(sql, valores)
            conn.commit()
            return cursor.lastrowid, "Médico creado exitosamente."
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: Medico.dni" in str(e):
                return None, "El DNI ya pertenece a otro médico."
            elif "UNIQUE constraint failed: Medico.matricula" in str(e):
                return None, "La matrícula ya pertenece a otro médico."
            elif "UNIQUE constraint failed: Medico.usuario" in str(e):
                return None, "El nombre de usuario ya está en uso."
            else:
                return None, f"Error de integridad: {e}"
        except sqlite3.Error as e:
            if conn: conn.rollback()
            return None, f"Error de base de datos: {e}"
        finally:
            if conn: conn.close()

    def actualizar_medico(self, medico, usuario_actual):
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol not in ["Administrador"]:
            return False, "Permiso denegado."

        datos = {
            'usuario': medico.usuario, 'matricula': medico.matricula, 'nombre': medico.nombre,
            'apellido': medico.apellido, 'tipo_dni': medico.tipo_dni, 'dni': medico.dni,
            'email': medico.email, 'telefono': medico.telefono
        }
        es_valido, errores = Validaciones.validar_medico_completo(datos, id_medico_actual=medico.id_medico)
        if not es_valido:
            return False, "\n".join(errores)

        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            
            cursor.execute("SELECT id_medico FROM Medico WHERE dni = ? AND id_medico != ?", (medico.dni, medico.id_medico))
            if cursor.fetchone():
                return False, "Error: El DNI ya pertenece a otro médico."
            
            cursor.execute("SELECT id_medico FROM Medico WHERE matricula = ? AND id_medico != ?", (medico.matricula, medico.id_medico))
            if cursor.fetchone():
                return False, "Error: La matrícula ya pertenece a otro médico."
            
            cursor.execute("SELECT id_medico FROM Medico WHERE usuario = ? AND id_medico != ?", (medico.usuario, medico.id_medico))
            if cursor.fetchone():
                return False, "Error: El nombre de usuario ya está en uso por otro médico."
            
            sql = """
            UPDATE Medico SET usuario = ?, matricula = ?, nombre = ?, apellido = ?, tipo_dni = ?, 
                               dni = ?, calle = ?, numero_calle = ?, email = ?, telefono = ?, 
                               id_especialidad = ?
            WHERE id_medico = ?
            """
            valores = (
                medico.usuario, medico.matricula, medico.nombre, medico.apellido,
                medico.tipo_dni, medico.dni, medico.calle, medico.numero_calle,
                medico.email, medico.telefono, medico.id_especialidad, medico.id_medico
            )
            cursor.execute(sql, valores)
            conn.commit()
            return True, "Médico actualizado exitosamente."
        except sqlite3.IntegrityError as e:
            return False, f"Error de integridad: {e}"
        except sqlite3.Error as e:
            if conn: conn.rollback()
            return False, f"Error de base de datos: {e}"
        finally:
            if conn: conn.close()

    def eliminar_medico(self, id_medico, usuario_actual):
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol not in ["Administrador"]:
            return False, "Permiso denegado."

        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            
            TurnoDAO().eliminar_turnos_por_medico(id_medico)
            
            cursor.execute("DELETE FROM Medico WHERE id_medico = ?", (id_medico,))
            conn.commit()
            
            if cursor.rowcount > 0:
                return True, "Médico eliminado exitosamente."
            else:
                return False, "No se encontró el médico."
        except sqlite3.Error as e:
            if conn: conn.rollback()
            return False, f"Error de base de datos: {e}"
        finally:
            if conn: conn.close()

    def obtener_todos_los_medicos(self):
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Medico ORDER BY apellido, nombre")
            return [Medico(id_medico=f[0], usuario=f[1], matricula=f[2], nombre=f[3], apellido=f[4],
                             tipo_dni=f[5], dni=f[6], calle=f[7], numero_calle=f[8], email=f[9],
                             telefono=f[10], id_especialidad=f[11]) for f in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error al obtener todos los médicos: {e}")
            return []
        finally:
            if conn: conn.close()

    def obtener_medico_por_id(self, id_medico):
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Medico WHERE id_medico = ?", (id_medico,))
            fila = cursor.fetchone()
            if fila:
                return Medico(id_medico=fila[0], usuario=fila[1], matricula=fila[2], nombre=fila[3],
                                apellido=fila[4], tipo_dni=fila[5], dni=fila[6], calle=fila[7],
                                numero_calle=fila[8], email=fila[9], telefono=fila[10], id_especialidad=fila[11])
            return None
        except sqlite3.Error as e:
            print(f"Error al obtener médico por ID: {e}")
            return None
        finally:
            if conn: conn.close()
            
    def obtener_medicos_por_especialidad(self, id_especialidad):
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Medico WHERE id_especialidad = ?", (id_especialidad,))
            return [Medico(id_medico=f[0], usuario=f[1], matricula=f[2], nombre=f[3], apellido=f[4],
                             tipo_dni=f[5], dni=f[6], calle=f[7], numero_calle=f[8], email=f[9],
                             telefono=f[10], id_especialidad=f[11]) for f in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error al obtener médicos por especialidad: {e}")
            return []
        finally:
            if conn: conn.close()
            
    def obtener_medico_por_usuario(self, usuario):
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Medico WHERE usuario = ?", (usuario,))
            fila = cursor.fetchone()
            if fila:
                return Medico(id_medico=fila[0], usuario=fila[1], matricula=fila[2], nombre=fila[3],
                                apellido=fila[4], tipo_dni=fila[5], dni=fila[6], calle=fila[7],
                                numero_calle=fila[8], email=fila[9], telefono=fila[10], id_especialidad=fila[11])
            return None
        except sqlite3.Error as e:
            print(f"Error al obtener médico por usuario: {e}")
            return None
        finally:
            if conn: conn.close()

    def obtener_medicos_con_especialidad(self):
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            sql = """
            SELECT m.id_medico, m.usuario, m.matricula, m.nombre, m.apellido, m.tipo_dni, m.dni, 
                   m.calle, m.numero_calle, m.email, m.telefono, e.nombre 
            FROM Medico m
            LEFT JOIN Especialidad e ON m.id_especialidad = e.id_especialidad
            ORDER BY m.id_medico
            """
            cursor.execute(sql)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error al obtener médicos con especialidad: {e}")
            return []
        finally:
            if conn: conn.close()

    def buscar_medicos(self, especialidad=None, apellido=None, dni=None):
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            sql = """
            SELECT m.id_medico, m.usuario, m.matricula, m.nombre, m.apellido, m.tipo_dni, m.dni, 
                   m.calle, m.numero_calle, m.email, m.telefono, e.nombre 
            FROM Medico m
            LEFT JOIN Especialidad e ON m.id_especialidad = e.id_especialidad
            WHERE 1=1
            """
            params = []
            if especialidad:
                sql += " AND e.nombre LIKE ?"
                params.append(f"%{especialidad}%")
            if apellido:
                sql += " AND m.apellido LIKE ?"
                params.append(f"%{apellido}%")
            if dni:
                sql += " AND m.dni LIKE ?"
                params.append(f"%{dni}%")
            
            sql += " ORDER BY m.id_medico"
            
            cursor.execute(sql, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error al buscar médicos: {e}")
            return []
        finally:
            if conn: conn.close()
