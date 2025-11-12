import sqlite3
from Backend.BDD.Conexion import get_conexion
from Backend.Model.Paciente import Paciente
from Backend.Validaciones.validaciones import Validaciones

from Backend.DAO.UsuarioDAO import UsuarioDAO

class PacienteDAO:
    """
    DAO (Data Access Object) para la entidad Paciente.
    Se encarga de todas las operaciones CRUD (Crear, Leer, Actualizar, Borrar)
    en la tabla Paciente de la base de datos.
    """

    def crear_paciente(self, paciente, usuario_actual):
        """
        Recibe un objeto de tipo Paciente y lo inserta en la DB.
        Retorna el ID del nuevo paciente o None si falla.
        """
        # Permisos: solo Paciente o Administrador pueden crear
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol not in ["Paciente", "Administrador"]:
            print("Permiso denegado: solo Paciente o Administrador pueden crear pacientes.")
            return None
        # Validaciones previas
        datos = {
            'usuario': paciente.usuario,
            'nombre': paciente.nombre,
            'apellido': paciente.apellido,
            'fecha_nacimiento': paciente.fecha_nacimiento,
            'tipo_dni': paciente.tipo_dni,
            'dni': paciente.dni,
            'email': paciente.email,
            'telefono': paciente.telefono
        }

        es_valido, errores = Validaciones.validar_paciente_completo(datos)
        if not es_valido:
            print("❌ Errores de validación al crear paciente:")
            for err in errores:
                print(f"   - {err}")
            return None

        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = """
            INSERT INTO Paciente (
                id_barrio, usuario, nombre, apellido, fecha_nacimiento, 
                tipo_dni, dni, email, telefono, id_obra_social, 
                calle, numero_calle
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            valores = (
                paciente.id_barrio, paciente.usuario, paciente.nombre,
                paciente.apellido, paciente.fecha_nacimiento, paciente.tipo_dni,
                paciente.dni, paciente.email, paciente.telefono,
                paciente.id_obra_social, paciente.calle, paciente.numero_calle
            )

            cursor.execute(sql, valores)
            conn.commit()
            print("Paciente creado exitosamente.")
            
            return cursor.lastrowid # Retorna el ID del nuevo registro

        except sqlite3.Error as e:
            if conn:
                conn.rollback() # Revertir cambios si hay un error
            print(f"Error al crear el paciente: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def obtener_todos_los_pacientes(self):
        """
        Retorna una lista de objetos Paciente con todos los registros.
        """
        conn = None
        pacientes = [] # Lista para almacenar los objetos Paciente
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM Paciente"
            cursor.execute(sql)
            filas = cursor.fetchall()

            for fila in filas:
                p = Paciente(
                    id_paciente=fila[0],
                    id_barrio=fila[1],
                    usuario=fila[2],
                    nombre=fila[3],
                    apellido=fila[4],
                    fecha_nacimiento=fila[5],
                    tipo_dni=fila[6],
                    dni=fila[7],
                    email=fila[8],
                    telefono=fila[9],
                    id_obra_social=fila[10],
                    calle=fila[11],
                    numero_calle=fila[12]
                )
                pacientes.append(p)
            
            return pacientes

        except sqlite3.Error as e:
            print(f"Error al obtener todos los pacientes: {e}")
            return [] # Retorna lista vacía en caso de error
        finally:
            if conn:
                conn.close()

    def obtener_paciente_por_dni(self, dni):
        """
        Busca un paciente por su DNI y retorna un objeto Paciente.
        Retorna None si no lo encuentra.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            # El '?' es un placeholder para el DNI
            sql = "SELECT * FROM Paciente WHERE dni = ?"
            cursor.execute(sql, (dni,)) # El DNI se pasa como una tupla
            
            fila = cursor.fetchone() # Obtener solo el primer resultado

            if fila:
                # Si encontramos un resultado, creamos el objeto
                p = Paciente(
                    id_paciente=fila[0], id_barrio=fila[1], usuario=fila[2],
                    nombre=fila[3], apellido=fila[4], fecha_nacimiento=fila[5],
                    tipo_dni=fila[6], dni=fila[7], email=fila[8],
                    telefono=fila[9], id_obra_social=fila[10],
                    calle=fila[11], numero_calle=fila[12]
                )
                return p
            else:
                return None # No se encontró el paciente

        except sqlite3.Error as e:
            print(f"Error al obtener paciente por DNI: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def actualizar_paciente(self, paciente, usuario_actual):
        """
        Recibe un objeto Paciente con datos actualizados
        y los aplica en la base de datos (busca por id_paciente).
        """
        # Permisos: solo el propio Paciente o Administrador pueden actualizar
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol == "Paciente" and usuario_actual != paciente.usuario:
            print("Permiso denegado: solo el propio paciente puede actualizar sus datos.")
            return False
        if rol not in ["Paciente", "Administrador"]:
            print("Permiso denegado: solo Paciente o Administrador pueden actualizar pacientes.")
            return False
        # Validaciones previas (excluir el propio registro en la verificación de unicidad)
        datos = {
            'usuario': paciente.usuario,
            'nombre': paciente.nombre,
            'apellido': paciente.apellido,
            'fecha_nacimiento': paciente.fecha_nacimiento,
            'tipo_dni': paciente.tipo_dni,
            'dni': paciente.dni,
            'email': paciente.email,
            'telefono': paciente.telefono
        }

        es_valido, errores = Validaciones.validar_paciente_completo(datos, id_paciente_actual=paciente.id_paciente)
        if not es_valido:
            print("❌ Errores de validación al actualizar paciente:")
            for err in errores:
                print(f"   - {err}")
            return False

        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = """
            UPDATE Paciente SET 
                id_barrio = ?, usuario = ?, nombre = ?, apellido = ?, 
                fecha_nacimiento = ?, tipo_dni = ?, dni = ?, email = ?, 
                telefono = ?, id_obra_social = ?, calle = ?, numero_calle = ?
            WHERE id_paciente = ?
            """
            
            valores = (
                paciente.id_barrio, paciente.usuario, paciente.nombre,
                paciente.apellido, paciente.fecha_nacimiento, paciente.tipo_dni,
                paciente.dni, paciente.email, paciente.telefono,
                paciente.id_obra_social, paciente.calle, paciente.numero_calle,
                paciente.id_paciente # El ID va al final para el WHERE
            )

            cursor.execute(sql, valores)
            conn.commit()
            print("Paciente actualizado exitosamente.")
            return True # Retorna True si la actualización fue exitosa

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al actualizar el paciente: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def eliminar_paciente(self, id_paciente, usuario_actual):
        """
        Elimina un paciente de la base de datos usando su ID.
        """
        conn = None
        # Permisos: solo el propio Paciente o Administrador pueden eliminar
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        # Obtener usuario del paciente
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT usuario FROM Paciente WHERE id_paciente = ?", (id_paciente,))
            fila = cursor.fetchone()
            usuario_paciente = fila[0] if fila else None
            if rol == "Paciente" and usuario_actual != usuario_paciente:
                print("Permiso denegado: solo el propio paciente puede eliminar su registro.")
                return False
            if rol not in ["Paciente", "Administrador"]:
                print("Permiso denegado: solo Paciente o Administrador pueden eliminar pacientes.")
                return False
            sql = "DELETE FROM Paciente WHERE id_paciente = ?"
            cursor.execute(sql, (id_paciente,))
            conn.commit()
            if cursor.rowcount > 0:
                print(f"Paciente con ID {id_paciente} eliminado exitosamente.")
                return True
            else:
                print(f"No se encontró paciente con ID {id_paciente}.")
                return False
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error al eliminar el paciente (puede tener datos asociados): {e}")
            return False
        finally:
            if conn:
                conn.close()

    def buscar_paciente_por_apellido(self, apellido):
        """
        Busca pacientes cuyo apellido coincida parcialmente con el proporcionado.
        Retorna una lista de objetos Paciente.
        """
        conn = None
        pacientes = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM Paciente WHERE apellido LIKE ?"
            patron_busqueda = f"%{apellido}%" # Para búsqueda parcial
            cursor.execute(sql, (patron_busqueda,))

            filas = cursor.fetchall()
            for fila in filas:
                p = Paciente(
                    id_paciente=fila[0],
                    id_barrio=fila[1],
                    usuario=fila[2],
                    nombre=fila[3],
                    apellido=fila[4],
                    fecha_nacimiento=fila[5],
                    tipo_dni=fila[6],
                    dni=fila[7],
                    email=fila[8],
                    telefono=fila[9],
                    id_obra_social=fila[10],
                    calle=fila[11],
                    numero_calle=fila[12]
                )
                pacientes.append(p)
            
            return pacientes

        except sqlite3.Error as e:
            print(f"Error al buscar pacientes por apellido: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def buscar_paciente_por_id_paciente(self, id_paciente):
        """
        Busca un paciente por su ID y retorna un objeto Paciente.
        Retorna None si no lo encuentra.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM Paciente WHERE id_paciente = ?"
            cursor.execute(sql, (id_paciente,))
            
            fila = cursor.fetchone()

            if fila:
                p = Paciente(
                    id_paciente=fila[0], id_barrio=fila[1], usuario=fila[2],
                    nombre=fila[3], apellido=fila[4], fecha_nacimiento=fila[5],
                    tipo_dni=fila[6], dni=fila[7], email=fila[8],
                    telefono=fila[9], id_obra_social=fila[10],
                    calle=fila[11], numero_calle=fila[12]
                )
                return p
            else:
                return None

        except sqlite3.Error as e:
            print(f"Error al obtener paciente por ID: {e}")
            return None
        finally:
            if conn:
                conn.close()