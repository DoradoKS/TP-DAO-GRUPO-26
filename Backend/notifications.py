import os
import time
import smtplib
from email.mime.text import MIMEText
from threading import Thread
from datetime import datetime, timedelta

from Backend.DAO.TurnoDAO import TurnoDAO
from Backend.DAO.PacienteDAO import PacienteDAO
from Backend.DAO.MedicoDAO import MedicoDAO
from Backend.DAO.ConsultorioDAO import ConsultorioDAO
from Backend.BDD.Conexion import get_conexion


# Configuración leída desde variables de entorno
# DESPUES DE PROBAR EL PROYECTO, TENGO QUE SACAR MIS DATOS Y DEJAR LAS VARIABLES EN DEFAULTTT !
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USER = os.environ.get('EMAIL_USER', 'mateo.bianchi78@gmail.com')
EMAIL_PASS = os.environ.get('EMAIL_PASS', 'ignfrjkimrylpdjf')
EMAIL_FROM = os.environ.get('EMAIL_FROM', EMAIL_USER)
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() in ('1', 'true', 'yes')


def _ensure_table():
    conn = None
    try:
        conn = get_conexion()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS NotificacionTurno (
                id_turno INTEGER PRIMARY KEY,
                enviado_en TEXT
            )
        """)
        conn.commit()
    except Exception as e:
        print(f"Error creando tabla de notificaciones: {e}")
    finally:
        if conn: conn.close()


def _already_sent(id_turno):
    conn = None
    try:
        conn = get_conexion()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM NotificacionTurno WHERE id_turno = ?", (id_turno,))
        return cur.fetchone() is not None
    except Exception as e:
        print(f"Error comprobando notificación existente: {e}")
        return False
    finally:
        if conn: conn.close()


def _mark_sent(id_turno):
    conn = None
    try:
        conn = get_conexion()
        cur = conn.cursor()
        cur.execute("INSERT OR REPLACE INTO NotificacionTurno (id_turno, enviado_en) VALUES (?, ?)", (id_turno, datetime.now().isoformat()))
        conn.commit()
    except Exception as e:
        print(f"Error registrando notificación enviada: {e}")
    finally:
        if conn: conn.close()


def _send_email(to_email, subject, body):
    if not EMAIL_HOST or not EMAIL_PORT or not EMAIL_USER or not EMAIL_PASS:
        # Modo seguro: si no hay configuración SMTP, solo loguear el mail
        print("[Notificaciones] SMTP no configurado. Mostrando email en consola:")
        print(f"Para: {to_email}\nAsunto: {subject}\n\n{body}\n")
        return True

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM
    msg['To'] = to_email

    try:
        if EMAIL_USE_TLS:
            server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=10)
            server.ehlo()
            server.starttls()
            server.ehlo()
        else:
            server = smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT, timeout=10)

        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_FROM, [to_email], msg.as_string())
        server.quit()
        print(f"[Notificaciones] Email enviado a {to_email}")
        return True
    except Exception as e:
        print(f"[Notificaciones] Error enviando email a {to_email}: {e}")
        return False


def send_welcome_email(to_email, username, password, nombre=None):
    """Envía un email de bienvenida con usuario y contraseña al paciente recién registrado."""
    if not to_email:
        print("[Notificaciones] No se envió welcome email: paciente sin email.")
        return False
    nombre_saludo = nombre or "Paciente"
    subject = "Registro exitoso en la plataforma"
    body = (
        f"Hola {nombre_saludo},\n\n"
        "Su cuenta ha sido creada correctamente en la plataforma de la clínica.\n\n"
        f"Usuario: {username}\n"
        f"Contraseña: {password}\n\n"
        "Saludos,\nEl equipo de la clínica"
    )
    return _send_email(to_email, subject, body)


def send_turno_created(id_turno):
    """Envía email al paciente informando que se creó un turno (usa id_turno para recuperar datos)."""
    try:
        turno = TurnoDAO().obtener_turno_por_id(id_turno)
        if not turno:
            print(f"[Notificaciones] No se encontró turno {id_turno} para notificar creación.")
            return False
        paciente = PacienteDAO().buscar_paciente_por_id_paciente(turno.id_paciente)
        medico = MedicoDAO().obtener_medico_por_id(turno.id_medico)
        if not paciente or not paciente.email:
            print(f"[Notificaciones] Paciente sin email para turno {id_turno}")
            return False

        hora = None
        try:
            hora = datetime.strptime(turno.fecha_hora, "%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M')
        except Exception:
            hora = str(turno.fecha_hora)

        medico_nombre = f"{medico.nombre} {medico.apellido}" if medico else "el médico"
        subject = "Turno confirmado"
        body = (
            f"Hola {paciente.nombre} {paciente.apellido},\n\n"
            f"Su turno ha sido registrado con éxito.\n\n"
            f"Fecha y hora: {hora}\n"
            f"Médico: {medico_nombre}\n\n"
            "Si desea cancelar el turno puede hacerlo desde la plataforma o contactando al centro.\n\n"
            "Saludos,\nEl equipo de la clínica"
        )
        return _send_email(paciente.email, subject, body)
    except Exception as e:
        print(f"[Notificaciones] Error al preparar email de turno creado: {e}")
        return False


def send_turno_cancelled(turno_or_id, quien='El sistema'):
    """Envía email al paciente informando que su turno fue cancelado.

    Acepta un objeto Turno o un id_turno. Si recibe el id y no encuentra el turno,
    intenta informar y retorna False.
    """
    try:
        # Aceptar tanto objeto Turno como id_turno
        if hasattr(turno_or_id, 'id_turno'):
            turno = turno_or_id
        else:
            turno = TurnoDAO().obtener_turno_por_id(turno_or_id)

        if not turno:
            print(f"[Notificaciones] No se encontró turno {turno_or_id} para notificar cancelación.")
            return False

        paciente = PacienteDAO().buscar_paciente_por_id_paciente(turno.id_paciente)
        medico = MedicoDAO().obtener_medico_por_id(turno.id_medico)
        if not paciente or not paciente.email:
            print(f"[Notificaciones] Paciente sin email para turno {getattr(turno, 'id_turno', 'N/A')}")
            return False

        hora = None
        try:
            hora = datetime.strptime(turno.fecha_hora, "%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M')
        except Exception:
            hora = str(turno.fecha_hora)

        medico_nombre = f"{medico.nombre} {medico.apellido}" if medico else "el médico"
        subject = "Turno cancelado"
        body = (
            f"Hola {paciente.nombre} {paciente.apellido},\n\n"
            f"Le informamos que su turno programado para {hora} con {medico_nombre} ha sido CANCELADO por {quien}.\n\n"
            f"Motivo: {turno.motivo or 'No especificado'}\n\n"
            "Si lo desea, puede solicitar un nuevo turno desde la plataforma.\n\n"
            "Saludos,\nEl equipo de la clínica"
        )
        return _send_email(paciente.email, subject, body)
    except Exception as e:
        print(f"[Notificaciones] Error al preparar email de turno cancelado: {e}")
        return False


def _find_and_send(window_start_dt, window_end_dt):
    """Busca turnos cuya fecha_hora esté entre window_start_dt y window_end_dt y envía notificaciones."""
    # Usamos TurnoDAO para obtener turnos del día (optimización simple)
    fecha_str = window_start_dt.strftime("%Y-%m-%d")
    turnos = TurnoDAO().obtener_turnos_por_fecha(fecha_str)

    paciente_dao = PacienteDAO()
    medico_dao = MedicoDAO()
    consultorio_dao = ConsultorioDAO()

    for t in turnos:
        try:
            turno_dt = datetime.strptime(t.fecha_hora, "%Y-%m-%d %H:%M:%S")
        except Exception:
            try:
                turno_dt = datetime.strptime(t.fecha_hora, "%Y-%m-%d %H:%M")
            except Exception:
                print(f"[Notificaciones] Fecha inválida para turno {t}")
                continue

        if not (window_start_dt <= turno_dt < window_end_dt):
            continue

        if _already_sent(t.id_turno):
            print(f"[Notificaciones] Ya se envió notificación para turno {t.id_turno}")
            continue

        paciente = paciente_dao.buscar_paciente_por_id_paciente(t.id_paciente)
        medico = medico_dao.obtener_medico_por_id(t.id_medico)
        consultorio_desc = None
        if hasattr(t, 'id_consultorio') and t.id_consultorio:
            cons = consultorio_dao.obtener_por_id(t.id_consultorio)
            if cons:
                consultorio_desc = cons.descripcion

        if not paciente or not paciente.email:
            print(f"[Notificaciones] Paciente sin email para turno {t.id_turno}")
            continue

        hora_str = turno_dt.strftime('%H:%M')
        medico_nombre = f"{medico.nombre} {medico.apellido}" if medico else "el médico"

        subject = "Recordatorio de turno"
        if consultorio_desc:
            body = f"Recordatorio: mañana a las {hora_str} en {consultorio_desc} tiene su turno con {medico_nombre}."
        else:
            body = f"Recordatorio: mañana a las {hora_str} tiene su turno con {medico_nombre}."

        ok = _send_email(paciente.email, subject, body)
        if ok:
            _mark_sent(t.id_turno)


def _scheduler_loop(interval_minutes=1):
    print("[Notificaciones] Scheduler iniciado (daemon). Intervalo (min):", interval_minutes)
    _ensure_table()
    interval_td = timedelta(minutes=interval_minutes)
    while True:
        try:
            now = datetime.now()
            window_start = now + timedelta(hours=24)
            # el scheduler se ejecuta cada `interval_minutes`, por lo que cubrimos ese intervalo
            window_end = window_start + interval_td
            print(f"[Notificaciones] Buscando turnos entre {window_start} y {window_end}")
            _find_and_send(window_start, window_end)
        except Exception as e:
            print(f"[Notificaciones] Error en el loop: {e}")
        time.sleep(interval_minutes * 60)


def start_scheduler(interval_minutes=1):
    thread = Thread(target=_scheduler_loop, args=(interval_minutes,), daemon=True)
    thread.start()
    return thread


if __name__ == '__main__':
    # Arranque de prueba
    start_scheduler(1)
    print('Scheduler corriendo en background. Ctrl-C para terminar.')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Saliendo...')
