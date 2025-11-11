import sqlite3
# Importamos la función para conectarnos desde la carpeta BDD
from Backend.BDD.Conexion import get_conexion

# Importamos la clase Paciente desde la carpeta Model
# (Asumimos que tu archivo se llama paciente.py y la clase Paciente)
# Asegúrate de que tu clase Paciente tenga un __init__ que coincida
from Backend.Model.Paciente import Paciente

class PacienteDAO:
    """
    DAO (Data Access Object) para la entidad Paciente.
    Se encarga de todas las operaciones CRUD (Crear, Leer, Actualizar, Borrar)
    en la tabla Paciente de la base de datos.
    """

    def crear_paciente(self, paciente):
        """
        Recibe un objeto de tipo Paciente y lo inserta en la DB.
        Retorna el ID del nuevo paciente o None si falla.
        """
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

    # --- NUEVOS MÉTODOS ---

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
                # Creamos un objeto Paciente por cada fila
                # NOTA: ¡El orden aquí debe coincidir con tu clase Paciente!
                # Asumo que tu clase Paciente recibe los campos en este orden.
                # Ajusta el __init__ de tu Modelo si es necesario.
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

    def actualizar_paciente(self, paciente):
        """
        Recibe un objeto Paciente con datos actualizados
        y los aplica en la base de datos (busca por id_paciente).
        """
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

    def eliminar_paciente(self, id_paciente):
        """
        Elimina un paciente de la base de datos usando su ID.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "DELETE FROM Paciente WHERE id_paciente = ?"
            
            cursor.execute(sql, (id_paciente,))
            conn.commit()

            # Opcional: verificar cuántas filas se eliminaron
            if cursor.rowcount > 0:
                print(f"Paciente con ID {id_paciente} eliminado exitosamente.")
                return True
            else:
                print(f"No se encontró paciente con ID {id_paciente}.")
                return False

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            # Un error común aquí es si el paciente tiene turnos asignados
            # (Fallo de Foreign Key). ¡Esto es BUENO, es una validación!
            print(f"Error al eliminar el paciente (puede tener datos asociados): {e}")
            return False
        finally:
            if conn:
                conn.close()