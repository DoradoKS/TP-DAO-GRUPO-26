import sqlite3
# En DAO/MedicoDAO.py

from Backend.BDD.Conexion import get_conexion
from Backend.Model.Medico import Medico # Asegúrate de que el archivo se llame Medico.py
from Backend.Validaciones.validaciones import Validaciones

from Backend.DAO.UsuarioDAO import UsuarioDAO

class MedicoDAO:
    """
    DAO para la entidad Medico.
    Gestiona las operaciones CRUD en la tabla Medico.
    """

    def crear_medico(self, medico, usuario_actual):
        """
        Inserta un nuevo objeto Medico en la base de datos.
        """
        # Permisos: solo Medico o Administrador pueden crear
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol not in ["Medico", "Administrador"]:
            print("Permiso denegado: solo Medico o Administrador pueden crear médicos.")
            return None
        # Validaciones previas
        datos = {
            'usuario': medico.usuario,
            'matricula': medico.matricula,
            'nombre': medico.nombre,
            'apellido': medico.apellido,
            'tipo_dni': medico.tipo_dni,
            'dni': medico.dni,
            'email': medico.email,
            'telefono': medico.telefono
        }

        es_valido, errores = Validaciones.validar_medico_completo(datos)
        if not es_valido:
            print("❌ Errores de validación al crear médico:")
            for err in errores:
                print(f"   - {err}")
            return None

        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = """
            INSERT INTO Medico (
                usuario, matricula, nombre, apellido, tipo_dni, dni, 
                calle, numero_calle, email, telefono, id_especialidad
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            valores = (
                medico.usuario, medico.matricula, medico.nombre,
                medico.apellido, medico.tipo_dni, medico.dni,
                medico.calle, medico.numero_calle, medico.email,
                medico.telefono, medico.id_especialidad
            )

            cursor.execute(sql, valores)
            conn.commit()
            print("Medico creado exitosamente.")
            return cursor.lastrowid # Retorna el ID del nuevo médico

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al crear el médico: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def obtener_todos_los_medicos(self):
        """
        Retorna una lista de todos los médicos como objetos Medico.
        """
        conn = None
        medicos = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM Medico"
            cursor.execute(sql)
            filas = cursor.fetchall()

            for fila in filas:
                # El orden debe coincidir con el __init__ de la clase Medico
                m = Medico(
                    id_medico=fila[0], usuario=fila[1], matricula=fila[2],
                    nombre=fila[3], apellido=fila[4], tipo_dni=fila[5],
                    dni=fila[6], calle=fila[7], numero_calle=fila[8],
                    email=fila[9], telefono=fila[10], id_especialidad=fila[11]
                )
                medicos.append(m)
            
            return medicos

        except sqlite3.Error as e:
            print(f"Error al obtener todos los médicos: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def obtener_medico_por_matricula(self, matricula):
        """
        Busca un médico por su matrícula (que es UNIQUE).
        Retorna un objeto Medico o None.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM Medico WHERE matricula = ?"
            cursor.execute(sql, (matricula,))
            
            fila = cursor.fetchone()

            if fila:
                m = Medico(
                    id_medico=fila[0], usuario=fila[1], matricula=fila[2],
                    nombre=fila[3], apellido=fila[4], tipo_dni=fila[5],
                    dni=fila[6], calle=fila[7], numero_calle=fila[8],
                    email=fila[9], telefono=fila[10], id_especialidad=fila[11]
                )
                return m
            else:
                return None # No se encontró el médico

        except sqlite3.Error as e:
            print(f"Error al obtener médico por matrícula: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def actualizar_medico(self, medico, usuario_actual):
        """
        Actualiza los datos de un médico en la DB, buscando por id_medico.
        """
        # Permisos: solo el propio Medico o Administrador pueden actualizar
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol == "Medico" and usuario_actual != medico.usuario:
            print("Permiso denegado: solo el propio médico puede actualizar sus datos.")
            return False
        if rol not in ["Medico", "Administrador"]:
            print("Permiso denegado: solo Medico o Administrador pueden actualizar médicos.")
            return False
        # Validaciones previas (excluir el propio registro en la verificación de unicidad)
        datos = {
            'usuario': medico.usuario,
            'matricula': medico.matricula,
            'nombre': medico.nombre,
            'apellido': medico.apellido,
            'tipo_dni': medico.tipo_dni,
            'dni': medico.dni,
            'email': medico.email,
            'telefono': medico.telefono
        }

        es_valido, errores = Validaciones.validar_medico_completo(datos, id_medico_actual=medico.id_medico)
        if not es_valido:
            print("❌ Errores de validación al actualizar médico:")
            for err in errores:
                print(f"   - {err}")
            return False

        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = """
            UPDATE Medico SET 
                usuario = ?, matricula = ?, nombre = ?, apellido = ?, tipo_dni = ?, 
                dni = ?, calle = ?, numero_calle = ?, email = ?, telefono = ?, 
                id_especialidad = ?
            WHERE id_medico = ?
            """
            
            valores = (
                medico.usuario, medico.matricula, medico.nombre,
                medico.apellido, medico.tipo_dni, medico.dni,
                medico.calle, medico.numero_calle, medico.email,
                medico.telefono, medico.id_especialidad,
                medico.id_medico # ID para el WHERE
            )

            cursor.execute(sql, valores)
            conn.commit()
            print("Medico actualizado exitosamente.")
            return True

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al actualizar el médico: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def eliminar_medico(self, id_medico, usuario_actual):
        """
        Elimina un médico de la base de datos usando su ID.
        """
        conn = None
        # Permisos: solo el propio Medico o Administrador pueden eliminar
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        # Obtener usuario del medico
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT usuario FROM Medico WHERE id_medico = ?", (id_medico,))
            fila = cursor.fetchone()
            usuario_medico = fila[0] if fila else None
            if rol == "Medico" and usuario_actual != usuario_medico:
                print("Permiso denegado: solo el propio médico puede eliminar su registro.")
                return False
            if rol not in ["Medico", "Administrador"]:
                print("Permiso denegado: solo Medico o Administrador pueden eliminar médicos.")
                return False
            sql = "DELETE FROM Medico WHERE id_medico = ?"
            cursor.execute(sql, (id_medico,))
            conn.commit()
            if cursor.rowcount > 0:
                print(f"Medico con ID {id_medico} eliminado exitosamente.")
                return True
            else:
                print(f"No se encontró médico con ID {id_medico}.")
                return False
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al eliminar el médico (puede tener turnos): {e}")
            return False
        finally:
            if conn:
                conn.close()

    def buscar_medico_por_apellido(self, apellido):
        """
        Busca médicos por su apellido.
        Retorna una lista de objetos Medico.
        """
        conn = None
        medicos = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM Medico WHERE apellido LIKE ?"
            cursor.execute(sql, (f"%{apellido}%",))
            filas = cursor.fetchall()

            for fila in filas:
                m = Medico(
                    id_medico=fila[0], usuario=fila[1], matricula=fila[2],
                    nombre=fila[3], apellido=fila[4], tipo_dni=fila[5],
                    dni=fila[6], calle=fila[7], numero_calle=fila[8],
                    email=fila[9], telefono=fila[10], id_especialidad=fila[11]
                )
                medicos.append(m)
            
            return medicos

        except sqlite3.Error as e:
            print(f"Error al buscar médicos por apellido: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def obtener_medicos_por_especialidad(self, id_especialidad):
        """
        Retorna una lista de médicos que pertenecen a una especialidad específica.
        """
        conn = None
        medicos = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM Medico WHERE id_especialidad = ?"
            cursor.execute(sql, (id_especialidad,))
            filas = cursor.fetchall()

            for fila in filas:
                m = Medico(
                    id_medico=fila[0], usuario=fila[1], matricula=fila[2],
                    nombre=fila[3], apellido=fila[4], tipo_dni=fila[5],
                    dni=fila[6], calle=fila[7], numero_calle=fila[8],
                    email=fila[9], telefono=fila[10], id_especialidad=fila[11]
                )
                medicos.append(m)

            return medicos

        except sqlite3.Error as e:
            print(f"Error al obtener los médicos por especialidad: {e}")
            return []
        finally:
            if conn:
                conn.close()