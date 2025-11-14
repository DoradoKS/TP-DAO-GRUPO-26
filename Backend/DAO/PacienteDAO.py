import sqlite3
from Backend.BDD.Conexion import get_conexion
from Backend.Model.Paciente import Paciente
from Backend.Validaciones.validaciones import Validaciones
from Backend.DAO.UsuarioDAO import UsuarioDAO
from Backend.DAO.TurnoDAO import TurnoDAO

class PacienteDAO:
    """
    DAO para la entidad Paciente.
    """

    def crear_paciente(self, paciente, usuario_actual):
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol not in ["Paciente", "Administrador"]:
            return None, "Permiso denegado."

        datos = {
            'usuario': paciente.usuario, 'nombre': paciente.nombre, 'apellido': paciente.apellido,
            'fecha_nacimiento': paciente.fecha_nacimiento, 'tipo_dni': paciente.tipo_dni,
            'dni': paciente.dni, 'email': paciente.email, 'telefono': paciente.telefono
        }
        es_valido, errores = Validaciones.validar_paciente_completo(datos)
        if not es_valido:
            return None, "\n".join(errores)

        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            sql = """
            INSERT INTO Paciente (id_barrio, usuario, nombre, apellido, fecha_nacimiento, 
                                  tipo_dni, dni, email, telefono, id_obra_social, calle, numero_calle)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            valores = (
                paciente.id_barrio, paciente.usuario, paciente.nombre, paciente.apellido,
                paciente.fecha_nacimiento, paciente.tipo_dni, paciente.dni, paciente.email,
                paciente.telefono, paciente.id_obra_social, paciente.calle, paciente.numero_calle
            )
            cursor.execute(sql, valores)
            conn.commit()
            return cursor.lastrowid, "Paciente creado exitosamente."
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: Paciente.dni" in str(e):
                return None, "El DNI ingresado ya pertenece a otro paciente."
            elif "UNIQUE constraint failed: Paciente.usuario" in str(e):
                return None, "El nombre de usuario ya está en uso."
            else:
                return None, f"Error de integridad: {e}"
        except sqlite3.Error as e:
            if conn: conn.rollback()
            return None, f"Error de base de datos: {e}"
        finally:
            if conn: conn.close()

    def actualizar_paciente(self, paciente, usuario_actual):
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol == "Paciente" and usuario_actual != paciente.usuario:
            return False, "Permiso denegado."
        if rol not in ["Paciente", "Administrador"]:
            return False, "Permiso denegado."

        datos = {
            'usuario': paciente.usuario, 'nombre': paciente.nombre, 'apellido': paciente.apellido,
            'fecha_nacimiento': paciente.fecha_nacimiento, 'tipo_dni': paciente.tipo_dni,
            'dni': paciente.dni, 'email': paciente.email, 'telefono': paciente.telefono
        }
        es_valido, errores = Validaciones.validar_paciente_completo(datos, id_paciente_actual=paciente.id_paciente)
        if not es_valido:
            return False, "\n".join(errores)

        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            sql = """
            UPDATE Paciente SET id_barrio = ?, usuario = ?, nombre = ?, apellido = ?, 
                                fecha_nacimiento = ?, tipo_dni = ?, dni = ?, email = ?, 
                                telefono = ?, id_obra_social = ?, calle = ?, numero_calle = ?
            WHERE id_paciente = ?
            """
            valores = (
                paciente.id_barrio, paciente.usuario, paciente.nombre, paciente.apellido,
                paciente.fecha_nacimiento, paciente.tipo_dni, paciente.dni, paciente.email,
                paciente.telefono, paciente.id_obra_social, paciente.calle, paciente.numero_calle,
                paciente.id_paciente
            )
            cursor.execute(sql, valores)
            conn.commit()
            return True, "Paciente actualizado exitosamente."
        except sqlite3.IntegrityError as e:
            return False, "Error de integridad: El DNI o usuario ya existen."
        except sqlite3.Error as e:
            if conn: conn.rollback()
            return False, f"Error de base de datos: {e}"
        finally:
            if conn: conn.close()

    def eliminar_paciente(self, id_paciente, usuario_actual):
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            
            rol = UsuarioDAO().obtener_rol(usuario_actual)
            cursor.execute("SELECT usuario FROM Paciente WHERE id_paciente = ?", (id_paciente,))
            fila = cursor.fetchone()
            if not fila:
                return False, "El paciente no existe."
            
            usuario_paciente = fila[0]
            if rol == "Paciente" and usuario_actual != usuario_paciente:
                return False, "No tiene permisos para eliminar a otro paciente."
            if rol not in ["Paciente", "Administrador"]:
                return False, "Permiso denegado."

            # Eliminar todas las entidades relacionadas con el paciente
            # 1. Eliminar historiales clínicos
            cursor.execute("DELETE FROM Historial WHERE id_paciente = ?", (id_paciente,))
            
            # 2. Eliminar recetas
            cursor.execute("DELETE FROM Receta WHERE id_paciente = ?", (id_paciente,))
            
            # 3. Eliminar turnos
            cursor.execute("DELETE FROM Turno WHERE id_paciente = ?", (id_paciente,))
            
            # 4. Finalmente, eliminar el paciente
            cursor.execute("DELETE FROM Paciente WHERE id_paciente = ?", (id_paciente,))
            conn.commit()
            return True, "Paciente y toda su información relacionada eliminados exitosamente."
        except sqlite3.Error as e:
            if conn: conn.rollback()
            return False, f"Error de base de datos al eliminar: {e}"
        finally:
            if conn: conn.close()

    def obtener_todos_los_pacientes(self):
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Paciente ORDER BY apellido, nombre")
            return [Paciente(id_paciente=f[0], id_barrio=f[1], usuario=f[2], nombre=f[3], apellido=f[4],
                             fecha_nacimiento=f[5], tipo_dni=f[6], dni=f[7], email=f[8], telefono=f[9],
                             id_obra_social=f[10], calle=f[11], numero_calle=f[12]) for f in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error al obtener todos los pacientes: {e}")
            return []
        finally:
            if conn: conn.close()

    def buscar_paciente_por_id_paciente(self, id_paciente):
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Paciente WHERE id_paciente = ?", (id_paciente,))
            fila = cursor.fetchone()
            if fila:
                return Paciente(
                    id_paciente=fila[0], id_barrio=fila[1], usuario=fila[2], nombre=fila[3], 
                    apellido=fila[4], fecha_nacimiento=fila[5], tipo_dni=fila[6], dni=fila[7], 
                    email=fila[8], telefono=fila[9], id_obra_social=fila[10], calle=fila[11], 
                    numero_calle=fila[12]
                )
            return None
        except sqlite3.Error as e:
            print("Error al buscar paciente:", e)
            return None
        finally:
            if conn:
                conn.close()

    def obtener_paciente_por_usuario(self, usuario):
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Paciente WHERE usuario = ?", (usuario,))
            fila = cursor.fetchone()
            if fila:
                return Paciente(id_paciente=fila[0], id_barrio=fila[1], usuario=fila[2], nombre=fila[3], apellido=fila[4],
                                fecha_nacimiento=fila[5], tipo_dni=fila[6], dni=fila[7], email=fila[8], telefono=fila[9],
                                id_obra_social=fila[10], calle=fila[11], numero_calle=fila[12])
            return None
        except sqlite3.Error as e:
            print(f"Error al obtener paciente por usuario: {e}")
            return None
        finally:
            if conn: conn.close()
            
    def obtener_pacientes_con_detalles(self):
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            sql = """
            SELECT p.id_paciente, p.usuario, p.nombre, p.apellido, p.tipo_dni, p.dni, 
                   p.fecha_nacimiento, o.nombre, b.nombre, p.calle, p.numero_calle, p.email, p.telefono
            FROM Paciente p
            LEFT JOIN ObraSocial o ON p.id_obra_social = o.id_obra_social
            LEFT JOIN Barrio b ON p.id_barrio = b.id_barrio
            ORDER BY p.apellido, p.nombre
            """
            cursor.execute(sql)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error al obtener pacientes con detalles: {e}")
            return []
        finally:
            if conn: conn.close()

    def buscar_pacientes(self, apellido=None, dni=None):
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            sql = """
            SELECT p.id_paciente, p.usuario, p.nombre, p.apellido, p.tipo_dni, p.dni, 
                   p.fecha_nacimiento, o.nombre, b.nombre, p.calle, p.numero_calle, p.email, p.telefono
            FROM Paciente p
            LEFT JOIN ObraSocial o ON p.id_obra_social = o.id_obra_social
            LEFT JOIN Barrio b ON p.id_barrio = b.id_barrio
            WHERE 1=1
            """
            params = []
            if apellido:
                sql += " AND p.apellido LIKE ?"
                params.append(f"%{apellido}%")
            if dni:
                sql += " AND p.dni LIKE ?"
                params.append(f"%{dni}%")
            
            sql += " ORDER BY p.apellido, p.nombre"
            
            cursor.execute(sql, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error al buscar pacientes: {e}")
            return []
        finally:
            if conn: conn.close()


    # --- MÉTODOS DE REPORTES ---

    def reporte_pacientes_atendidos_por_fecha(self, fecha_inicio, fecha_fin):
        """
        Reporte 3: Pacientes únicos que asistieron (asistio = 1) 
        en un rango de fechas.
        """
        conn = None
        pacientes = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            # Usamos DISTINCT para no repetir pacientes si tuvieron varios turnos
            sql = """
            SELECT DISTINCT P.id_paciente, P.nombre, P.apellido, P.dni, P.email
            FROM Paciente AS P
            JOIN Turno AS T ON P.id_paciente = T.id_paciente
            WHERE T.asistio = 1 
              AND DATE(T.fecha_hora) BETWEEN ? AND ?
            ORDER BY P.apellido, P.nombre
            """
            cursor.execute(sql, (fecha_inicio, fecha_fin))
            for fila in cursor.fetchall():
                # (Ajustá esto si tu constructor de Paciente es diferente)
                pacientes.append(Paciente(id_paciente=fila[0], nombre=fila[1], apellido=fila[2], dni=fila[3], email=fila[4]))
            return pacientes
        except sqlite3.Error as e:
            print(f"Error en reporte de pacientes atendidos: {e}")
            return []
        finally:
            if conn: conn.close()