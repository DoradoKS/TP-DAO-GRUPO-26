import sqlite3
from Backend.BDD.Conexion import get_conexion
from Backend.Model.Usuario import Usuario

class UsuarioDAO:
    def crear_usuario(self, usuario, contrasena, rol):
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Usuario (usuario, contrasenia, rol)
                VALUES (?, ?, ?)
            """, (usuario, contrasena, rol))
            conn.commit()
            return True, "Usuario creado correctamente."
        except sqlite3.IntegrityError:
            return False, "El nombre de usuario ya está registrado."
        except sqlite3.Error as e:
            if conn: conn.rollback()
            return False, f"Error de base de datos: {e}"
        finally:
            if conn: conn.close()

    def obtener_rol(self, usuario):
        conn = get_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT rol FROM Usuario WHERE usuario = ?", (usuario,))
        fila = cursor.fetchone()
        conn.close()
        return fila[0] if fila else None

    def obtener_usuario(self, usuario):
        """
        Retorna un objeto Usuario dado el nombre de usuario.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            sql = "SELECT usuario, contrasenia, rol FROM Usuario WHERE usuario = ?"
            cursor.execute(sql, (usuario,))
            fila = cursor.fetchone()
            if fila:
                return Usuario(usuario=fila[0], contrasenia=fila[1], rol=fila[2])
            else:
                return None
        except sqlite3.Error as e:
            print(f"Error al obtener usuario: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def autenticar_usuario(self, usuario, contrasenia):
        """
        Verifica usuario y contraseña. Retorna el rol si es válido, None si no.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            sql = "SELECT rol FROM Usuario WHERE usuario = ? AND contrasenia = ?"
            cursor.execute(sql, (usuario, contrasenia))
            fila = cursor.fetchone()
            if fila:
                return fila[0] # rol
            else:
                return None
        except sqlite3.Error as e:
            print(f"Error al autenticar usuario: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def obtener_rol(self, usuario):
        """
        Retorna el rol de un usuario.
        """
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            sql = "SELECT rol FROM Usuario WHERE usuario = ?"
            cursor.execute(sql, (usuario,))
            fila = cursor.fetchone()
            if fila:
                return fila[0]
            else:
                return None
        except sqlite3.Error as e:
            print(f"Error al obtener rol: {e}")
            return None
        finally:
            if conn:
                conn.close()
