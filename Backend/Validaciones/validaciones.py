import re
from datetime import datetime, date
from Backend.BDD.Conexion import get_conexion
import sqlite3


class Validaciones:
    """Funciones de validación centralizadas para el proyecto."""

    # ---------- Utilidades ----------
    @staticmethod
    def _parse_fecha(fecha):
        """Acepta date o string 'YYYY-MM-DD' y devuelve datetime.date.
        Retorna None si fecha es None o cadena vacía.
        Lanza ValueError si el formato no es válido.
        """
        if fecha is None:
            return None
        if isinstance(fecha, date):
            return fecha
        fecha_str = str(fecha).strip()
        if fecha_str == "":
            return None
        try:
            return datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("La fecha debe tener formato YYYY-MM-DD.")

    # ---------- Campos requeridos ----------
    @staticmethod
    def validar_campos_requeridos(obj_dict, campos_requeridos):
        """Verifica que todos los campos en campos_requeridos estén presentes y no vacíos.
        Retorna (True, []) o (False, [mensajes])
        """
        errores = []
        for campo in campos_requeridos:
            if campo not in obj_dict:
                errores.append(f"Falta el campo requerido: {campo}.")
            else:
                val = obj_dict[campo]
                if val is None or (isinstance(val, str) and val.strip() == ""):
                    errores.append(f"El campo {campo} no puede estar vacío.")
        return len(errores) == 0, errores

    # ---------- DNI ----------
    @staticmethod
    def validar_dni_formato(dni):
        if dni is None or str(dni).strip() == "":
            return False, "El DNI es obligatorio."
        dni_str = str(dni).strip()
        if not dni_str.isdigit():
            return False, "El DNI debe contener solo números."
        if len(dni_str) not in (7, 8):
            return False, "El DNI debe tener 7 u 8 dígitos."
        return True, "DNI con formato válido."

    @staticmethod
    def validar_dni_unico(dni, tabla, id_excluir=None):
        """Verifica unicidad del DNI en la tabla indicada ('Paciente' o 'Medico').
        id_excluir: id a excluir (útil para actualizaciones)
        Retorna (True, mensaje) o (False, mensaje)
        """
        if tabla not in ("Paciente", "Medico"):
            return False, "Tabla inválida para validar DNI."
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            if id_excluir:
                # Las columnas PK se llaman id_paciente / id_medico según tabla
                id_col = 'id_paciente' if tabla == 'Paciente' else 'id_medico'
                sql = f"SELECT COUNT(*) FROM {tabla} WHERE dni = ? AND {id_col} != ?"
                cursor.execute(sql, (str(dni).strip(), id_excluir))
            else:
                sql = f"SELECT COUNT(*) FROM {tabla} WHERE dni = ?"
                cursor.execute(sql, (str(dni).strip(),))
            cantidad = cursor.fetchone()[0]
            if cantidad > 0:
                return False, f"El DNI ya está registrado en {tabla}."
            return True, "DNI único."
        except sqlite3.Error as e:
            return False, f"Error al verificar unicidad del DNI: {e}"
        finally:
            if conn:
                conn.close()

    # ---------- Nombres / Apellidos ----------
    @staticmethod
    def validar_nombre(nombre):
        if nombre is None or str(nombre).strip() == "":
            return False, "El nombre es obligatorio."
        s = str(nombre).strip()
        if len(s) < 2:
            return False, "El nombre debe tener al menos 2 caracteres."
        if len(s) > 100:
            return False, "El nombre no puede exceder 100 caracteres."
        patron = r"^[a-zA-ZÁÉÍÓÚáéíóúÑñ\s\-']+$"
        if not re.match(patron, s):
            return False, "El nombre contiene caracteres inválidos."
        return True, "Nombre válido."

    @staticmethod
    def validar_apellido(apellido):
        if apellido is None or str(apellido).strip() == "":
            return False, "El apellido es obligatorio."
        s = str(apellido).strip()
        if len(s) < 2:
            return False, "El apellido debe tener al menos 2 caracteres."
        if len(s) > 100:
            return False, "El apellido no puede exceder 100 caracteres."
        patron = r"^[a-zA-ZÁÉÍÓÚáéíóúÑñ\s\-']+$"
        if not re.match(patron, s):
            return False, "El apellido contiene caracteres inválidos."
        return True, "Apellido válido."

    # ---------- Email ----------
    @staticmethod
    def validar_email(email):
        if email is None or str(email).strip() == "":
            return False, "El email es obligatorio."
        s = str(email).strip()
        if len(s) > 100:
            return False, "El email no puede exceder 100 caracteres."
        patron = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(patron, s):
            return False, "El email no tiene un formato válido."
        return True, "Email válido."

    # ---------- Teléfono ----------
    @staticmethod
    def validar_telefono(telefono):
        if telefono is None or str(telefono).strip() == "":
            return False, "El teléfono es obligatorio."
        s = str(telefono).strip()
        if len(s) > 20:
            return False, "El teléfono no puede exceder 20 caracteres."
        patron = r"^[0-9\s\-\(\)\+]+$"
        if not re.match(patron, s):
            return False, "El teléfono contiene caracteres inválidos."
        solo_digitos = ''.join(c for c in s if c.isdigit())
        if len(solo_digitos) < 7:
            return False, "El teléfono debe contener al menos 7 dígitos."
        return True, "Teléfono válido."

    # ---------- Fechas ----------
    @staticmethod
    def validar_fecha_nacimiento_no_futura(fecha_nacimiento):
        """Valida que la fecha de nacimiento no sea mayor a la fecha actual."""
        try:
            f = Validaciones._parse_fecha(fecha_nacimiento)
        except ValueError as e:
            return False, str(e)
        if f is None:
            return False, "La fecha de nacimiento es obligatoria."
        hoy = date.today()
        if f > hoy:
            return False, "La fecha de nacimiento no puede ser mayor a la fecha actual."
        return True, "Fecha de nacimiento válida."

    @staticmethod
    def validar_fecha_emision_receta_no_futura(fecha_emision):
        try:
            f = Validaciones._parse_fecha(fecha_emision)
        except ValueError as e:
            return False, str(e)
        if f is None:
            return False, "La fecha de emisión es obligatoria."
        hoy = date.today()
        if f > hoy:
            return False, "La fecha de emisión no puede ser mayor a la fecha actual."
        return True, "Fecha de emisión válida."

    # ---------- Validaciones completas por entidad ----------
    @staticmethod
    def validar_paciente_completo(paciente_dict, id_paciente_actual=None):
        errores = []

        # Campos requeridos (ajustar según definición de la tabla)
        campos_req = ['usuario', 'nombre', 'apellido', 'fecha_nacimiento', 'tipo_dni', 'dni', 'email', 'telefono']
        ok, errs = Validaciones.validar_campos_requeridos(paciente_dict, campos_req)
        if not ok:
            errores.extend(errs)

        # DNI
        if 'dni' in paciente_dict:
            es, msg = Validaciones.validar_dni_formato(paciente_dict['dni'])
            if not es:
                errores.append(msg)
            else:
                es_u, msg_u = Validaciones.validar_dni_unico(paciente_dict['dni'], 'Paciente', id_excluir=id_paciente_actual)
                if not es_u:
                    errores.append(msg_u)

        # Nombre
        if 'nombre' in paciente_dict:
            es, msg = Validaciones.validar_nombre(paciente_dict['nombre'])
            if not es:
                errores.append(msg)

        # Apellido
        if 'apellido' in paciente_dict:
            es, msg = Validaciones.validar_apellido(paciente_dict['apellido'])
            if not es:
                errores.append(msg)

        # Fecha nacimiento
        if 'fecha_nacimiento' in paciente_dict:
            es, msg = Validaciones.validar_fecha_nacimiento_no_futura(paciente_dict['fecha_nacimiento'])
            if not es:
                errores.append(msg)

        # Email
        if 'email' in paciente_dict:
            es, msg = Validaciones.validar_email(paciente_dict['email'])
            if not es:
                errores.append(msg)

        # Teléfono
        if 'telefono' in paciente_dict:
            es, msg = Validaciones.validar_telefono(paciente_dict['telefono'])
            if not es:
                errores.append(msg)

        return len(errores) == 0, errores

    @staticmethod
    def validar_medico_completo(medico_dict, id_medico_actual=None):
        errores = []

        campos_req = ['usuario', 'matricula', 'nombre', 'apellido', 'tipo_dni', 'dni', 'email', 'telefono']
        ok, errs = Validaciones.validar_campos_requeridos(medico_dict, campos_req)
        if not ok:
            errores.extend(errs)

        # DNI
        if 'dni' in medico_dict:
            es, msg = Validaciones.validar_dni_formato(medico_dict['dni'])
            if not es:
                errores.append(msg)
            else:
                es_u, msg_u = Validaciones.validar_dni_unico(medico_dict['dni'], 'Medico', id_excluir=id_medico_actual)
                if not es_u:
                    errores.append(msg_u)

        # Nombre
        if 'nombre' in medico_dict:
            es, msg = Validaciones.validar_nombre(medico_dict['nombre'])
            if not es:
                errores.append(msg)

        # Apellido
        if 'apellido' in medico_dict:
            es, msg = Validaciones.validar_apellido(medico_dict['apellido'])
            if not es:
                errores.append(msg)

        # Fecha nacimiento (opcional en medico, si existe validar)
        if 'fecha_nacimiento' in medico_dict and medico_dict['fecha_nacimiento']:
            es, msg = Validaciones.validar_fecha_nacimiento_no_futura(medico_dict['fecha_nacimiento'])
            if not es:
                errores.append(msg)

        # Email
        if 'email' in medico_dict:
            es, msg = Validaciones.validar_email(medico_dict['email'])
            if not es:
                errores.append(msg)

        # Teléfono
        if 'telefono' in medico_dict:
            es, msg = Validaciones.validar_telefono(medico_dict['telefono'])
            if not es:
                errores.append(msg)

        return len(errores) == 0, errores

    @staticmethod
    def validar_receta_completa(receta_dict):
        errores = []
        campos_req = ['id_paciente', 'id_medico', 'fecha_emision', 'detalles']
        ok, errs = Validaciones.validar_campos_requeridos(receta_dict, campos_req)
        if not ok:
            errores.extend(errs)

        if 'fecha_emision' in receta_dict:
            es, msg = Validaciones.validar_fecha_emision_receta_no_futura(receta_dict['fecha_emision'])
            if not es:
                errores.append(msg)

        return len(errores) == 0, errores


if __name__ == '__main__':
    # Pequeños ejemplos manuales
    print(Validaciones.validar_dni_formato('12345678'))
    print(Validaciones.validar_telefono('+54 9 11 4444-5555'))

