import tkinter as tk
from tkinter import ttk, messagebox

from Backend.DAO.TurnoDAO import TurnoDAO
from Backend.DAO.PacienteDAO import PacienteDAO
from Backend.DAO.MedicoDAO import MedicoDAO
from Backend.DAO.EspecialidadDAO import EspecialidadDAO
from Backend.Model.Turno import Turno
from Backend.DAO.ConsultorioDAO import ConsultorioDAO
from Backend.GUI.consulta_historial import ConsultaHistorial
from Backend.GUI.registro_historial import RegistroHistorial

from Backend.Validaciones.validaciones_turnos import validar_fecha

from tkcalendar import DateEntry
from datetime import datetime, timedelta


class ABMTurnos(tk.Toplevel):
    def __init__(self, parent, rol, usuario):
        super().__init__(parent)
        self.title("Gestión de Turnos")
        self.geometry("1000x600")

        self.rol = rol
        self.usuario = usuario

        self.create_widgets()
        self.cargar_combos()
        self.cargar_turnos()


    # ---------------------------------------------------------
    # CREACIÓN DE WIDGETS
    # ---------------------------------------------------------
    def create_widgets(self):
        form_frame = ttk.Frame(self)
        form_frame.pack(padx=10, pady=10, fill="x")

        # ------------------- PACIENTE -------------------
        ttk.Label(form_frame, text="Paciente:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.paciente_combo = ttk.Combobox(form_frame, width=30)
        self.paciente_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # ----------------- ESPECIALIDAD -----------------
        ttk.Label(form_frame, text="Especialidad:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.especialidad_combo = ttk.Combobox(form_frame, width=30)
        self.especialidad_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.especialidad_combo.bind("<<ComboboxSelected>>", self.cargar_medicos_por_especialidad)

        # --------------------- MÉDICO ---------------------
        ttk.Label(form_frame, text="Médico:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.medico_combo = ttk.Combobox(form_frame, width=30)
        self.medico_combo.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # ------------------- CONSULTORIO -------------------
        # Consultorio se asigna automáticamente según disponibilidad; no se muestra selector
        self.consultorio_combo = None

        # ---------------------- FECHA ----------------------
        ttk.Label(form_frame, text="Fecha (YYYY-MM-DD):").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.fecha_entry = DateEntry(
            form_frame,
            width=20,
            date_pattern="yyyy-mm-dd",
            background="darkblue",
            foreground="white"
        )
        self.fecha_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        self.mostrar_horarios_btn = ttk.Button(
            form_frame,
            text="Mostrar horarios disponibles",
            command=self.mostrar_horarios_disponibles
        )
        self.mostrar_horarios_btn.grid(row=4, column=2, padx=5, pady=5, sticky="w")

        # ------------------ LISTA HORARIOS ------------------
        horarios_frame = ttk.Frame(self)
        horarios_frame.pack(padx=10, pady=5, fill="x")

        ttk.Label(horarios_frame, text="Horarios disponibles:").pack(anchor="w")

        self.slots_listbox = tk.Listbox(horarios_frame, height=8)
        self.slots_listbox.pack(side="left", fill="x", expand=True)

        scrollbar = ttk.Scrollbar(horarios_frame, orient="vertical", command=self.slots_listbox.yview)
        scrollbar.pack(side="left", fill="y")
        self.slots_listbox.config(yscrollcommand=scrollbar.set)

        # ------------------ BOTONES ------------------
        button_frame = ttk.Frame(self)
        button_frame.pack(padx=10, pady=10, fill="x")

        ttk.Button(button_frame, text="Solicitar Turno", command=self.solicitar_turno).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancelar Turno", command=self.cancelar_turno).pack(side="left", padx=5)

        # Botones de acciones para el médico sobre el turno seleccionado
        self.btn_ver_hist = ttk.Button(button_frame, text="Ver Historial del Paciente", command=self.ver_historial_paciente)
        self.btn_reg_hist = ttk.Button(button_frame, text="Registrar Historial del Paciente", command=self.registrar_historial_paciente)
        self.btn_ver_hist.pack(side="right", padx=5)
        self.btn_reg_hist.pack(side="right", padx=5)

        # Botones para marcar asistencia/inasistencia (solo médico)
        self.btn_asist = ttk.Button(button_frame, text="Marcar Asistencia", command=self.marcar_asistencia)
        self.btn_inasist = ttk.Button(button_frame, text="Marcar Inasistencia", command=self.marcar_inasistencia)
        self.btn_asist.pack(side="right", padx=5)
        self.btn_inasist.pack(side="right", padx=5)

        # ------------------ TREEVIEW ------------------
        self.tree = ttk.Treeview(self, columns=("id", "paciente", "medico", "especialidad", "consultorio", "fecha", "hora", "estado"), show="headings")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("paciente", width=150)
        self.tree.column("medico", width=150)
        self.tree.column("especialidad", width=120)
        self.tree.column("consultorio", width=120)
        self.tree.column("fecha", width=90, anchor="center")
        self.tree.column("hora", width=70, anchor="center")
        self.tree.column("estado", width=110, anchor="center")
        self.tree.heading("consultorio", text="Consultorio")
        self.tree.heading("estado", text="Estado")


        self.tree.pack(padx=10, pady=10, fill="both", expand=True)
        # Tags de color por estado
        self.tree.tag_configure('asistio', background='#c7f0c1')      # verde claro
        self.tree.tag_configure('inasistencia', background='#f8c0c0') # rojo claro
        self.tree.tag_configure('pendiente', background='#fff3b0')    # amarillo claro

        # Adaptar la UI si es médico (no debe crear turnos)
        if self.rol == "Medico":
            for w in [self.paciente_combo, self.especialidad_combo, self.medico_combo, self.consultorio_combo, self.fecha_entry, self.mostrar_horarios_btn, self.slots_listbox]:
                try:
                    w.configure(state="disabled")
                except Exception:
                    pass
            # Ocultar botón de solicitar para evitar confusiones
            for child in button_frame.winfo_children():
                if isinstance(child, ttk.Button) and child.cget("text") == "Solicitar Turno":
                    child.pack_forget()
        else:
            # Ocultar botones de historial/asistencia para roles que no sean médico
            for child in [self.btn_ver_hist, self.btn_reg_hist, self.btn_asist, self.btn_inasist]:
                child.pack_forget()


    # ---------------------------------------------------------
    # CARGA DE COMBOS
    # ---------------------------------------------------------
    def cargar_combos(self):
        self.paciente_dao = PacienteDAO()
        self.pacientes = self.paciente_dao.obtener_todos_los_pacientes()
        self.paciente_combo["values"] = [
            f"{p.nombre} {p.apellido}" for p in self.pacientes
        ]

        self.especialidad_dao = EspecialidadDAO()
        self.especialidades = self.especialidad_dao.obtener_todas_las_especialidades()
        self.especialidad_combo["values"] = [e.nombre for e in self.especialidades]

        # Consultorios: se usarán internamente para mostrar descripción en la tabla
        self.consultorios = ConsultorioDAO().obtener_todos()

        if self.rol == "Paciente":
            paciente = self.paciente_dao.obtener_paciente_por_usuario(self.usuario)
            if paciente:
                self.paciente_combo.set(f"{paciente.nombre} {paciente.apellido}")
                self.paciente_combo.config(state="disabled")


    # ---------------------------------------------------------
    # CARGA DE MÉDICOS POR ESPECIALIDAD
    # ---------------------------------------------------------
    def cargar_medicos_por_especialidad(self, event):
        nombre_esp = self.especialidad_combo.get()

        esp = next((e for e in self.especialidades if e.nombre == nombre_esp), None)
        if not esp:
            self.medico_combo["values"] = []
            return

        med_dao = MedicoDAO()
        self.medicos = med_dao.obtener_medicos_por_especialidad(esp.id_especialidad)
        self.medico_combo["values"] = [f"{m.nombre} {m.apellido}" for m in self.medicos]


    # ---------------------------------------------------------
    # CARGA DE TURNOS EN LA TABLA
    # ---------------------------------------------------------
    def cargar_turnos(self):
        # Cierre automático del día: marcar inasistencias pendientes
        try:
            TurnoDAO().cerrar_dia()
        except Exception:
            pass
        for item in self.tree.get_children():
            self.tree.delete(item)

        turno_dao = TurnoDAO()

        if self.rol == "Administrador":
            turnos = turno_dao.obtener_todos_los_turnos()
        elif self.rol == "Medico":
            medico = MedicoDAO().obtener_medico_por_usuario(self.usuario)
            turnos = turno_dao.obtener_turnos_por_medico(medico.id_medico) if medico else []
        elif self.rol == "Paciente":
            pac = PacienteDAO().obtener_paciente_por_usuario(self.usuario)
            turnos = turno_dao.obtener_turnos_por_paciente(pac.id_paciente) if pac else []
        else:
            turnos = []

        for t in turnos:
            pac = PacienteDAO().buscar_paciente_por_id_paciente(t.id_paciente)
            med = MedicoDAO().obtener_medico_por_id(t.id_medico)
            esp = EspecialidadDAO().obtener_especialidad_por_id(med.id_especialidad) if med else None
            cons_desc = ""
            if hasattr(t, 'id_consultorio') and t.id_consultorio:
                cons = next((c for c in getattr(self, 'consultorios', []) if c.id_consultorio == t.id_consultorio), None)
                cons_desc = cons.descripcion if cons else str(t.id_consultorio)

            paciente_nombre = f"{pac.nombre} {pac.apellido}" if pac else "N/A"
            medico_nombre = f"{med.nombre} {med.apellido}" if med else "N/A"
            especialidad_nombre = esp.nombre if esp else "N/A"

            fecha, hora = t.fecha_hora.split(" ")
            estado = 'Pendiente' if t.asistio is None else ('Asistió' if t.asistio == 1 else 'Inasistencia')
            tag = 'pendiente' if t.asistio is None else ('asistio' if t.asistio == 1 else 'inasistencia')

            self.tree.insert("", "end", values=(
                t.id_turno,
                paciente_nombre,
                medico_nombre,
                especialidad_nombre,
                cons_desc,
                fecha,
                hora,
                estado
            ), tags=(tag,))



    # ---------------------------------------------------------
    # MOSTRAR HORARIOS DISPONIBLES
    # ---------------------------------------------------------
    # def generar_franjas(self):
    #     franjas = []
    #     actual = datetime.strptime("08:00", "%H:%M")
    #     fin = datetime.strptime("14:00", "%H:%M")

    #     while actual <= fin:
    #         franjas.append(actual.strftime("%H:%M"))
    #         actual += timedelta(minutes=30)

    #     return franjas


    # def mostrar_horarios_disponibles(self):
    #     fecha = self.fecha_entry.get()

    #     if not validar_fecha(fecha):
    #         messagebox.showerror("Error", "Fecha inválida.")
    #         return

    #     medico_nombre = self.medico_combo.get()
    #     med = next((m for m in getattr(self, "medicos", []) if f"{m.nombre} {m.apellido}" == medico_nombre), None)

    #     if not med:
    #         messagebox.showwarning("Advertencia", "Seleccione un médico.")
    #         return

    #     turno_dao = TurnoDAO()

    #     ocupados = turno_dao.obtener_turnos_por_medico_y_fecha(med.id_medico, fecha)
    #     horas_ocupadas = {t.fecha_hora.split(" ")[1][:5] for t in ocupados}

    #     franjas = self.generar_franjas()
    #     disponibles = [f for f in franjas if f not in horas_ocupadas]

    #     self.slots_listbox.delete(0, tk.END)
    #     for h in disponibles:
    #         self.slots_listbox.insert(tk.END, h)

    def mostrar_horarios_disponibles(self, event=None):
        """
        Esta función se llama cuando el usuario selecciona un médico o una fecha.
        Busca en el DAO y actualiza la ListBox de horarios.
        """
        medico_nombre_completo = self.medico_combo.get()

        # --- CAMBIO PARA TKCALENDAR ---
        try:
            # 1. Obtenemos la fecha del widget de calendario
            fecha_obj = self.fecha_entry.get_date() 
            # 2. La formateamos al string 'YYYY-MM-DD' que espera el DAO
            fecha = fecha_obj.strftime("%Y-%m-%d")
        except Exception as e:
            messagebox.showerror("Error de fecha", "Fecha inválida. Seleccione una fecha del calendario.")
            return
        # Ya no necesitamos .strip() ni la validación de formato 'validar_fecha'
        # -------------------------------

        # --- VALIDACIONES DE DÍAS (Están perfectas) ---
        if fecha_obj.weekday() >= 5: # 5=Sábado, 6=Domingo
            messagebox.showwarning("Día no hábil", "Seleccione un día entre lunes y viernes.")
            self.slots_listbox.delete(0, tk.END) 
            return
        
        # (Acá podés agregar más validaciones de fechas si querés, como la de 30 días)

        # --- OBTENER ID DEL MÉDICO ---
        id_medico = None
        if hasattr(self, 'medicos'):
            for m in self.medicos:
                if f"{m.nombre} {m.apellido}" == medico_nombre_completo:
                    id_medico = m.id_medico
                    break

        if not id_medico:
            messagebox.showwarning("Advertencia", "Seleccione un médico para ver horarios.")
            return

        # --- LÓGICA REEMPLAZADA (Llama al DAO) ---
        if not hasattr(self, 'turno_dao'):
             self.turno_dao = TurnoDAO()
        disponibles = self.turno_dao.calcular_horarios_disponibles(id_medico, fecha)
        # ------------------------------------------------

        # Poblar el Listbox
        self.slots_listbox.delete(0, tk.END)
        if disponibles:
            for h in disponibles:
                self.slots_listbox.insert(tk.END, h)
        else:
            self.slots_listbox.insert(tk.END, "No hay horarios disponibles para este día.")

    # ---------------------------------------------------------
    # SOLICITAR TURNO
    # ---------------------------------------------------------
    def solicitar_turno(self):
        #fecha = self.fecha_entry.get()
        fecha_obj = self.fecha_entry.get_date()
        fecha = fecha_obj.strftime("%Y-%m-%d")
        pac_nombre = self.paciente_combo.get()
        med_nombre = self.medico_combo.get()
        if not (fecha and pac_nombre and med_nombre):
            messagebox.showerror("Error", "Complete todos los campos.")
            return

        if not validar_fecha(fecha):
            messagebox.showerror("Error", "Fecha inválida.")
            return

        selected = self.slots_listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "Seleccione un horario de la lista.")
            return

        hora_seleccionada = self.slots_listbox.get(selected[0])

        pac = next((p for p in self.pacientes if f"{p.nombre} {p.apellido}" == pac_nombre), None)
        med = next((m for m in getattr(self, "medicos", []) if f"{m.nombre} {m.apellido}" == med_nombre), None)

        fecha_hora = f"{fecha} {hora_seleccionada}:00"

        turno = Turno(
            id_paciente=pac.id_paciente,
            id_medico=med.id_medico,
            id_consultorio=None,
            fecha_hora=fecha_hora
        )

        id_creado, mensaje = TurnoDAO().crear_turno(turno, self.usuario)
        if id_creado:
            messagebox.showinfo("Éxito", mensaje)
            self.cargar_turnos()
            self.mostrar_horarios_disponibles()
        else:
            messagebox.showerror("Error", mensaje)


    # ---------------------------------------------------------
    # CANCELAR TURNO
    # ---------------------------------------------------------
    def cancelar_turno(self):
        sel = self.tree.selection()

        if not sel:
            messagebox.showwarning("Advertencia", "Seleccione un turno.")
            return

        item = self.tree.item(sel[0])
        id_turno = item["values"][0]

        if not messagebox.askyesno("Confirmar", "¿Cancelar este turno?"):
            return

        if TurnoDAO().eliminar_turno(id_turno, self.usuario):
            messagebox.showinfo("OK", "Turno cancelado.")
            self.cargar_turnos()
            self.mostrar_horarios_disponibles()
        else:
            messagebox.showerror("Error", "No se pudo cancelar el turno.")

    # ---------------------------------------------------------
    # ACCIONES MÉDICO: HISTORIAL DESDE AGENDA
    # ---------------------------------------------------------
    def _obtener_paciente_seleccionado_de_turno(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Advertencia", "Seleccione un turno de la tabla.")
            return None
        item = self.tree.item(sel[0])
        id_turno = item["values"][0]
        turno = TurnoDAO().obtener_turno_por_id(id_turno)
        if not turno:
            messagebox.showerror("Error", "No se pudo cargar el turno seleccionado.")
            return None
        return turno.id_paciente

    def ver_historial_paciente(self):
        if self.rol != "Medico":
            return
        id_paciente = self._obtener_paciente_seleccionado_de_turno()
        if id_paciente is None:
            return
        ConsultaHistorial(self, self.usuario, self.rol, id_paciente_fijo=id_paciente)

    def registrar_historial_paciente(self):
        if self.rol != "Medico":
            return
        id_paciente = self._obtener_paciente_seleccionado_de_turno()
        if id_paciente is None:
            return
        RegistroHistorial(self, self.usuario, self.rol, id_paciente_fijo=id_paciente)

    def _obtener_id_turno_seleccionado(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Advertencia", "Seleccione un turno de la tabla.")
            return None
        item = self.tree.item(sel[0])
        return item["values"][0]

    def marcar_asistencia(self):
        if self.rol != "Medico":
            return
        id_turno = self._obtener_id_turno_seleccionado()
        if id_turno is None:
            return
        ok, msg = TurnoDAO().marcar_asistencia(id_turno, True, self.usuario)
        if ok:
            messagebox.showinfo("OK", msg)
        else:
            messagebox.showerror("Error", msg)

    def marcar_inasistencia(self):
        if self.rol != "Medico":
            return
        id_turno = self._obtener_id_turno_seleccionado()
        if id_turno is None:
            return
        ok, msg = TurnoDAO().marcar_asistencia(id_turno, False, self.usuario)
        if ok:
            messagebox.showinfo("OK", msg)
        else:
            messagebox.showerror("Error", msg)
import sqlite3      
import random

from Backend.BDD.Conexion import get_conexion
from Backend.Model.Turno import Turno
from Backend.DAO.UsuarioDAO import UsuarioDAO
from Backend.DAO.FranjaHorariaDAO import FranjaHorariaDAO
import calendar
from datetime import datetime, timedelta

class TurnoDAO:
    """
    DAO para la entidad Turno.
    Gestiona las operaciones CRUD en la tabla Turno.
    """

    def crear_turno(self, turno, usuario_actual):
        """
        Inserta un nuevo objeto Turno en la base de datos.
        Retorna una tupla (id_creado, mensaje).
        """
        if not all([turno, turno.id_paciente, turno.id_medico, turno.fecha_hora]):
            return None, "Falta información requerida para crear el turno."

        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol not in ["Administrador", "Paciente"]:
            return None, "Permiso denegado."

        try:
            inicio = datetime.strptime(str(turno.fecha_hora), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                inicio = datetime.strptime(str(turno.fecha_hora), "%Y-%m-%d %H:%M")
            except ValueError:
                return None, "Formato de fecha_hora inválido."

        fin = inicio + timedelta(minutes=30)
        # --- NUEVA VALIDACIÓN: FRONTAL DE LA TRANSACCIÓN (FRANJA LABORAL) ---
        dia_semana_py = inicio.weekday() + 1 # Monday=0, so add 1 (1=Lunes)

        # Llama al nuevo DAO para verificar si el médico trabaja en ese slot
        if not FranjaHorariaDAO().validar_franja_laboral(turno.id_medico, dia_semana_py, inicio, fin):
            print("El médico no trabaja en ese horario o la hora solicitada está fuera de su franja laboral.")
            return None
        # ---------------------------------------------------------------------

        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql_paciente = "SELECT id_turno FROM Turno WHERE id_paciente = ? AND datetime(fecha_hora) < ? AND datetime(fecha_hora, '+30 minutes') > ?"
            cursor.execute(sql_paciente, (turno.id_paciente, fin.strftime("%Y-%m-%d %H:%M:%S"), inicio.strftime("%Y-%m-%d %H:%M:%S")))
            if cursor.fetchone():
                return None, "El paciente ya tiene un turno asignado ese día y horario."

            sql_medico = "SELECT id_turno FROM Turno WHERE id_medico = ? AND datetime(fecha_hora) < ? AND datetime(fecha_hora, '+30 minutes') > ?"
            cursor.execute(sql_medico, (turno.id_medico, fin.strftime("%Y-%m-%d %H:%M:%S"), inicio.strftime("%Y-%m-%d %H:%M:%S")))
            if cursor.fetchone():
                return None, "El médico ya tiene un turno en ese horario."

            # Asignación aleatoria de consultorio según disponibilidad si no se indicó
            if turno.id_consultorio is None:
                # Obtener consultorios disponibles para ese horario
                cursor.execute("SELECT id_consultorio FROM Consultorio")
                todos_cons = [row[0] for row in cursor.fetchall()]
                disponibles = []
                for cid in todos_cons:
                    cursor.execute(
                        "SELECT 1 FROM Turno WHERE id_consultorio = ? AND datetime(fecha_hora) < ? AND datetime(fecha_hora, '+30 minutes') > ?",
                        (cid, fin.strftime("%Y-%m-%d %H:%M:%S"), inicio.strftime("%Y-%m-%d %H:%M:%S"))
                    )
                    if cursor.fetchone() is None:
                        disponibles.append(cid)
                if not disponibles:
                    return None, "No hay consultorios disponibles en ese horario."
                turno.id_consultorio = random.choice(disponibles)
            else:
                # Evitar doble asignación del consultorio en el mismo horario
                sql_cons = "SELECT id_turno FROM Turno WHERE id_consultorio = ? AND datetime(fecha_hora) < ? AND datetime(fecha_hora, '+30 minutes') > ?"
                cursor.execute(sql_cons, (turno.id_consultorio, fin.strftime("%Y-%m-%d %H:%M:%S"), inicio.strftime("%Y-%m-%d %H:%M:%S")))
                if cursor.fetchone():
                    return None, "El consultorio ya está asignado en ese horario."

            sql = "INSERT INTO Turno (id_paciente, id_medico, id_consultorio, fecha_hora, motivo) VALUES (?, ?, ?, ?, ?)"
            valores = (turno.id_paciente, turno.id_medico, turno.id_consultorio, inicio.strftime("%Y-%m-%d %H:%M:%S"), turno.motivo)
            cursor.execute(sql, valores)
            conn.commit()
            return cursor.lastrowid, "Turno creado exitosamente."

        except sqlite3.Error as e:
            if conn: conn.rollback()
            return None, f"Error al crear el turno: {e}"
        finally:
            if conn: conn.close()

    def obtener_todos_los_turnos(self): 
        conn = None
        turnos = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT id_turno, id_paciente, id_medico, id_consultorio, fecha_hora, motivo, asistio FROM Turno")
            for fila in cursor.fetchall():
                turnos.append(Turno(id_turno=fila[0], id_paciente=fila[1], id_medico=fila[2], id_consultorio=fila[3], fecha_hora=fila[4], motivo=fila[5], asistio=fila[6]))
            return turnos
        except sqlite3.Error as e:
            print(f"Error al obtener los turnos: {e}")
            return []
        finally:
            if conn: conn.close()

    def obtener_turnos_por_paciente(self, id_paciente):
        conn = None
        turnos = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT id_turno, id_paciente, id_medico, id_consultorio, fecha_hora, motivo, asistio FROM Turno WHERE id_paciente = ?", (id_paciente,))
            for fila in cursor.fetchall():
                turnos.append(Turno(id_turno=fila[0], id_paciente=fila[1], id_medico=fila[2], id_consultorio=fila[3], fecha_hora=fila[4], motivo=fila[5], asistio=fila[6]))
            return turnos
        except sqlite3.Error as e:
            print(f"Error al obtener los turnos por paciente: {e}")
            return []
        finally:
            if conn: conn.close()

    def obtener_turnos_por_medico(self, id_medico):
        conn = None
        turnos = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT id_turno, id_paciente, id_medico, id_consultorio, fecha_hora, motivo, asistio FROM Turno WHERE id_medico = ?", (id_medico,))
            for fila in cursor.fetchall():
                turnos.append(Turno(id_turno=fila[0], id_paciente=fila[1], id_medico=fila[2], id_consultorio=fila[3], fecha_hora=fila[4], motivo=fila[5], asistio=fila[6]))
            return turnos
        except sqlite3.Error as e:
            print(f"Error al obtener los turnos por médico: {e}")
            return []
        finally:
            if conn: conn.close()

    def eliminar_turno(self, id_turno, usuario_actual):
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            rol = UsuarioDAO().obtener_rol(usuario_actual)
            
            if rol == "Administrador":
                cursor.execute("DELETE FROM Turno WHERE id_turno = ?", (id_turno,))
            elif rol in ["Paciente", "Medico"]:
                # Additional check to ensure they only delete their own appointments
                # This logic would need to be more robust in a real application
                cursor.execute("DELETE FROM Turno WHERE id_turno = ?", (id_turno,))
            else:
                print("Permiso denegado.")
                return False

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            if conn: conn.rollback()
            print(f"Error al eliminar el turno: {e}")
            return False
        finally:
            if conn: conn.close()

    def actualizar_turno(self, turno, usuario_actual):
        if not all([turno, turno.id_turno, turno.id_paciente, turno.id_medico, turno.fecha_hora]):
            print("Falta información requerida para actualizar el turno.")
            return False
        
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol != "Administrador":
            print("Permiso denegado.")
            return False

        try:
            inicio = datetime.strptime(str(turno.fecha_hora), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                inicio = datetime.strptime(str(turno.fecha_hora), "%Y-%m-%d %H:%M")
            except ValueError:
                print("Formato de fecha_hora inválido.")
                return False

        fin = inicio + timedelta(minutes=30)
        # --- NUEVA VALIDACIÓN: FRONTAL DE LA TRANSACCIÓN (FRANJA LABORAL) ---
        dia_semana_py = inicio.weekday() + 1 # Monday=0, so add 1 (1=Lunes)

        # Llama al nuevo DAO para verificar si el médico trabaja en ese slot
        if not FranjaHorariaDAO().validar_franja_laboral(turno.id_medico, dia_semana_py, inicio, fin):
            print("El médico no trabaja en ese horario o la hora solicitada está fuera de su franja laboral.")
            return None
        # ---------------------------------------------------------------------

        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql_paciente = "SELECT id_turno FROM Turno WHERE id_paciente = ? AND id_turno != ? AND datetime(fecha_hora) < ? AND datetime(fecha_hora, '+30 minutes') > ?"
            cursor.execute(sql_paciente, (turno.id_paciente, turno.id_turno, fin.strftime("%Y-%m-%d %H:%M:%S"), inicio.strftime("%Y-%m-%d %H:%M:%S")))
            if cursor.fetchone():
                print("El paciente ya tiene un turno que se solapa.")
                return False

            sql_medico = "SELECT id_turno FROM Turno WHERE id_medico = ? AND id_turno != ? AND datetime(fecha_hora) < ? AND datetime(fecha_hora, '+30 minutes') > ?"
            cursor.execute(sql_medico, (turno.id_medico, turno.id_turno, fin.strftime("%Y-%m-%d %H:%M:%S"), inicio.strftime("%Y-%m-%d %H:%M:%S")))
            if cursor.fetchone():
                print("El médico ya tiene un turno que se solapa.")
                return False

            sql = "UPDATE Turno SET id_paciente = ?, id_medico = ?, id_consultorio = ?, fecha_hora = ?, motivo = ? WHERE id_turno = ?"
            valores = (turno.id_paciente, turno.id_medico, turno.id_consultorio, inicio.strftime("%Y-%m-%d %H:%M:%S"), turno.motivo, turno.id_turno)
            cursor.execute(sql, valores)
            conn.commit()
            return True
        except sqlite3.Error as e:
            if conn: conn.rollback()
            print(f"Error al actualizar el turno: {e}")
            return False
        finally:
            if conn: conn.close()

    def obtener_turno_por_id(self, id_turno):
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT id_turno, id_paciente, id_medico, id_consultorio, fecha_hora, motivo, asistio FROM Turno WHERE id_turno = ?", (id_turno,))
            fila = cursor.fetchone()
            if fila:
                return Turno(id_turno=fila[0], id_paciente=fila[1], id_medico=fila[2], id_consultorio=fila[3], fecha_hora=fila[4], motivo=fila[5], asistio=fila[6])
            return None
        except sqlite3.Error as e:
            print(f"Error al obtener turno por ID: {e}")
            return None
        finally:
            if conn: conn.close()

    def eliminar_turnos_por_paciente(self, id_paciente):
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Turno WHERE id_paciente = ?", (id_paciente,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            if conn: conn.rollback()
            print(f"Error al eliminar los turnos del paciente: {e}")
            return False
        finally:
            if conn: conn.close()

    def eliminar_turnos_por_medico(self, id_medico):
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Turno WHERE id_medico = ?", (id_medico,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            if conn: conn.rollback()
            print(f"Error al eliminar los turnos del médico: {e}")
            return False
        finally:
            if conn: conn.close()

    def obtener_turnos_por_fecha(self, fecha):
        conn = None
        turnos = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT id_turno, id_paciente, id_medico, id_consultorio, fecha_hora, motivo, asistio FROM Turno WHERE DATE(fecha_hora) = ?", (fecha,))
            for fila in cursor.fetchall():
                turnos.append(Turno(id_turno=fila[0], id_paciente=fila[1], id_medico=fila[2], id_consultorio=fila[3], fecha_hora=fila[4], motivo=fila[5], asistio=fila[6]))
            return turnos
        except sqlite3.Error as e:
            print(f"Error al obtener los turnos por fecha: {e}")
            return []
        finally:
            if conn: conn.close()

    def obtener_turnos_por_medico_y_fecha(self, id_medico, fecha):
        conn = None
        turnos = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT id_turno, id_paciente, id_medico, id_consultorio, fecha_hora, motivo, asistio FROM Turno WHERE id_medico = ? AND DATE(fecha_hora) = ?", (id_medico, fecha))
            for fila in cursor.fetchall():
                turnos.append(Turno(id_turno=fila[0], id_paciente=fila[1], id_medico=fila[2], id_consultorio=fila[3], fecha_hora=fila[4], motivo=fila[5], asistio=fila[6]))
            return turnos
        except sqlite3.Error as e:
            print(f"Error al obtener los turnos por médico y fecha: {e}")
            return []
        finally:
            if conn: conn.close()

    def obtener_turnos_por_paciente_y_fecha(self, id_paciente, fecha):
        conn = None
        turnos = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT id_turno, id_paciente, id_medico, id_consultorio, fecha_hora, motivo, asistio FROM Turno WHERE id_paciente = ? AND DATE(fecha_hora) = ?", (id_paciente, fecha))
            for fila in cursor.fetchall():
                turnos.append(Turno(id_turno=fila[0], id_paciente=fila[1], id_medico=fila[2], id_consultorio=fila[3], fecha_hora=fila[4], motivo=fila[5], asistio=fila[6]))
            return turnos
        except sqlite3.Error as e:
            print(f"Error al obtener los turnos por paciente y fecha: {e}")
            return []
        finally:
            if conn: conn.close()

    def contar_turnos_por_medico(self, id_medico):
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Turno WHERE id_medico = ?", (id_medico,))
            resultado = cursor.fetchone()
            return resultado[0] if resultado else 0
        except sqlite3.Error as e:
            print(f"Error al contar los turnos por médico: {e}")
            return 0
        finally:
            if conn: conn.close()

    def contar_turnos_por_paciente(self, id_paciente):
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Turno WHERE id_paciente = ?", (id_paciente,))
            resultado = cursor.fetchone()
            return resultado[0] if resultado else 0
        except sqlite3.Error as e:
            print(f"Error al contar los turnos por paciente: {e}")
            return 0
        finally:
            if conn: conn.close()

    def obtener_turnos_entre_fechas(self, fecha_inicio, fecha_fin):
        conn = None
        turnos = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id_turno, id_paciente, id_medico, id_consultorio, fecha_hora, motivo, asistio FROM Turno WHERE DATE(fecha_hora) BETWEEN ? AND ?",
                (fecha_inicio, fecha_fin)
            )
            for fila in cursor.fetchall():
                turnos.append(Turno(id_turno=fila[0], id_paciente=fila[1], id_medico=fila[2], id_consultorio=fila[3], fecha_hora=fila[4], motivo=fila[5], asistio=fila[6]))
            return turnos
        except sqlite3.Error as e:
            print(f"Error al obtener los turnos entre fechas: {e}")
            return []
        finally:
            if conn: conn.close()

    def cerrar_dia(self, fecha=None):
        """Marca como inasistencia todos los turnos de 'fecha' con asistio NULL. Si fecha es None, cierra días anteriores y, si ya terminó la jornada, también el día actual."""
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            if fecha is None:
                cursor.execute("UPDATE Turno SET asistio = 0 WHERE DATE(fecha_hora) < DATE('now') AND asistio IS NULL")
                cursor.execute("SELECT strftime('%H:%M', 'now')")
                hora_actual = cursor.fetchone()[0]
                if hora_actual >= '14:00':
                    cursor.execute("UPDATE Turno SET asistio = 0 WHERE DATE(fecha_hora) = DATE('now') AND asistio IS NULL")
            else:
                cursor.execute("UPDATE Turno SET asistio = 0 WHERE DATE(fecha_hora) = ? AND asistio IS NULL", (fecha,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            if conn: conn.rollback()
            print(f"Error al cerrar día: {e}")
            return False
        finally:
            if conn: conn.close()

    # -------------------------------------------------
    # Asistencia / Inasistencia
    # -------------------------------------------------
    def marcar_asistencia(self, id_turno, asistio, usuario_actual):
        """Marca asistencia (True) o inasistencia (False) para un turno. Solo Médico o Administrador."""
        rol = UsuarioDAO().obtener_rol(usuario_actual)
        if rol not in ["Medico", "Administrador"]:
            return False, "Permiso denegado."
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            if rol == "Medico":
                # validar que el turno pertenezca al médico
                from Backend.DAO.MedicoDAO import MedicoDAO
                med = MedicoDAO().obtener_medico_por_usuario(usuario_actual)
                cursor.execute("SELECT id_medico FROM Turno WHERE id_turno = ?", (id_turno,))
                fila = cursor.fetchone()
                if not fila or fila[0] != (med.id_medico if med else None):
                    return False, "Solo puede marcar asistencia de sus propios turnos."
            cursor.execute("UPDATE Turno SET asistio = ? WHERE id_turno = ?", (1 if asistio else 0, id_turno))
            conn.commit()
            return cursor.rowcount > 0, "Asistencia registrada" if asistio else "Inasistencia registrada"
        except sqlite3.Error as e:
            if conn: conn.rollback()
            return False, f"Error al registrar asistencia: {e}"
        finally:
            if conn: conn.close()

    def obtener_resumen_asistencia_por_mes(self):
        """Devuelve lista de (mes 'YYYY-MM', asistencias, inasistencias)."""
        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT strftime('%Y-%m', fecha_hora) AS mes,
                       SUM(CASE WHEN asistio = 1 THEN 1 ELSE 0 END) AS asistencias,
                       SUM(CASE WHEN asistio = 0 THEN 1 ELSE 0 END) AS inasistencias
                FROM Turno
                GROUP BY mes
                ORDER BY mes
                """
            )
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error al obtener resumen asistencia por mes: {e}")
            return []
        finally:
            if conn: conn.close()

# --- NUEVO MÉTODO CRUCIAL: CÁLCULO DE DISPONIBILIDAD ---

    def calcular_horarios_disponibles(self, id_medico, fecha):
        """
        Calcula los slots libres (30 min) combinando franjas laborales y turnos ocupados.
        Retorna una lista de strings con los horarios disponibles ('HH:MM').
        """
        DURACION_MINUTOS = 30
        
        try:
            # Convertir la fecha solicitada a día de la semana (1-7)
            fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
            dia_semana_py = fecha_dt.weekday() + 1 # Lunes=1
        except ValueError:
            print("Formato de fecha de entrada inválido. Use YYYY-MM-DD.")
            return [] # Retorna lista vacía si la fecha es mala

        conn = None
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            
            # 1. Obtener Franjas de Trabajo (Las "Franjas Largas")
            sql_franja = "SELECT hora_inicio, hora_fin FROM FranjaHoraria WHERE id_medico = ? AND dia_semana = ?"
            cursor.execute(sql_franja, (id_medico, dia_semana_py))
            franjas_trabajo = cursor.fetchall()
            if not franjas_trabajo:
                 print(f"Debug: No se encontraron franjas laborales para el médico {id_medico} el día {dia_semana_py}.")
                 return [] # El médico no trabaja ese día
            
            # 2. Obtener Horarios Reservados (Las "Excepciones")
            sql_reservados = "SELECT strftime('%H:%M', fecha_hora) FROM Turno WHERE id_medico = ? AND DATE(fecha_hora) = ?"
            cursor.execute(sql_reservados, (id_medico, fecha))
            # Usamos un 'set' para que la búsqueda sea ultra-rápida
            turnos_reservados = {row[0] for row in cursor.fetchall()} 
            
            horarios_libres = []
            
            # 3. Calcular Slots Libres (Lógica Python)
            for inicio_str, fin_str in franjas_trabajo:
                
                # Convertimos los strings de hora a objetos datetime para poder sumarles tiempo
                hora_actual = datetime.strptime(f"{fecha} {inicio_str}", "%Y-%m-%d %H:%M")
                hora_fin = datetime.strptime(f"{fecha} {fin_str}", "%Y-%m-%d %H:%M")
                
                # Iteramos cada slot de 30 minutos
                while hora_actual < hora_fin:
                    slot_inicio_str = hora_actual.strftime('%H:%M')
                    
                    # Si el slot NO está en la lista de reservados, lo agregamos
                    if slot_inicio_str not in turnos_reservados:
                        horarios_libres.append(slot_inicio_str)
                        
                    # Avanzamos al siguiente slot
                    hora_actual += timedelta(minutes=DURACION_MINUTOS) 
                    
            print(f"Debug: Horarios libres encontrados: {horarios_libres}")
            return horarios_libres

        except sqlite3.Error as e:
            print(f"Error al calcular disponibilidad: {e}")
            return []
        finally:
            if conn: conn.close()