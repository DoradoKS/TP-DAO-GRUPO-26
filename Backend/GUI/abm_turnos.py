import tkinter as tk
from tkinter import ttk, messagebox
from Backend.DAO.TurnoDAO import TurnoDAO
from Backend.DAO.PacienteDAO import PacienteDAO
from Backend.DAO.MedicoDAO import MedicoDAO
from Backend.DAO.EspecialidadDAO import EspecialidadDAO
from Backend.DAO.ConsultorioDAO import ConsultorioDAO
from Backend.GUI.consulta_historial import ConsultaHistorial
from Backend.GUI.registro_historial import RegistroHistorial
from Backend.Model.Turno import Turno
from tkcalendar import DateEntry
from datetime import datetime, timedelta, date
import calendar


def _add_one_month(dt_date):
    """Return a date one month after dt_date, preserving day when possible.
    If the next month has fewer days, use the month's last day."""
    year = dt_date.year
    month = dt_date.month + 1
    if month == 13:
        month = 1
        year += 1
    day = dt_date.day
    last_day = calendar.monthrange(year, month)[1]
    if day > last_day:
        day = last_day
    return date(year, month, day)

class ABMTurnos(tk.Toplevel):
    def __init__(self, parent, rol, usuario):
        super().__init__(parent)
        self.title("Gestión de Turnos")
        self.geometry("1000x600")
        self.configure(bg="#333333")

        self.rol = rol
        self.usuario = usuario

        self.create_widgets()
        self.cargar_combos()
        self.cargar_turnos()

    def create_widgets(self):
        main_frame = tk.Frame(self, bg="#333333")
        main_frame.pack(expand=True, fill="both")

        form_frame = tk.Frame(main_frame, bg="#333333")
        form_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(form_frame, text="Paciente:", bg="#333333", fg="white").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.paciente_combo = ttk.Combobox(form_frame, width=30)
        self.paciente_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(form_frame, text="Especialidad:", bg="#333333", fg="white").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.especialidad_combo = ttk.Combobox(form_frame, width=30)
        self.especialidad_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.especialidad_combo.bind("<<ComboboxSelected>>", self.cargar_medicos_por_especialidad)

        tk.Label(form_frame, text="Médico:", bg="#333333", fg="white").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.medico_combo = ttk.Combobox(form_frame, width=30)
        self.medico_combo.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        self.consultorio_combo = None

        tk.Label(form_frame, text="Fecha:", bg="#333333", fg="white").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        # Limitar fecha máxima a 1 mes desde hoy
        hoy = date.today()
        self.fecha_max = _add_one_month(hoy)
        self.fecha_entry = DateEntry(form_frame, width=20, date_pattern="yyyy-mm-dd", state="readonly", maxdate=self.fecha_max)
        self.fecha_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        self.mostrar_horarios_btn = ttk.Button(form_frame, text="Mostrar horarios disponibles", command=self.mostrar_horarios_disponibles)
        self.mostrar_horarios_btn.grid(row=4, column=2, padx=5, pady=5, sticky="w")

        horarios_frame = tk.Frame(main_frame, bg="#333333")
        horarios_frame.pack(padx=10, pady=5, fill="x")

        tk.Label(horarios_frame, text="Horarios disponibles:", bg="#333333", fg="white").pack(anchor="w")

        self.slots_listbox = tk.Listbox(horarios_frame, height=8)
        self.slots_listbox.pack(side="left", fill="x", expand=True)

        scrollbar = ttk.Scrollbar(horarios_frame, orient="vertical", command=self.slots_listbox.yview)
        scrollbar.pack(side="left", fill="y")
        self.slots_listbox.config(yscrollcommand=scrollbar.set)

        button_frame = tk.Frame(main_frame, bg="#333333")
        button_frame.pack(padx=10, pady=10, fill="x")

        ttk.Button(button_frame, text="Solicitar Turno", command=self.solicitar_turno).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancelar Turno", command=self.cancelar_turno).pack(side="left", padx=5)

        self.btn_ver_hist = ttk.Button(button_frame, text="Ver Historial del Paciente", command=self.ver_historial_paciente)
        self.btn_reg_hist = ttk.Button(button_frame, text="Registrar Historial del Paciente", command=self.registrar_historial_paciente)
        self.btn_ver_hist.pack(side="right", padx=5)
        self.btn_reg_hist.pack(side="right", padx=5)

        self.btn_asist = ttk.Button(button_frame, text="Marcar Asistencia", command=self.marcar_asistencia)
        self.btn_inasist = ttk.Button(button_frame, text="Marcar Inasistencia", command=self.marcar_inasistencia)
        self.btn_asist.pack(side="right", padx=5)
        self.btn_inasist.pack(side="right", padx=5)

        # Botón para que el médico genere una receta al atender (solo visible para rol Medico)
        self.btn_generar_receta = ttk.Button(button_frame, text="Generar Receta", command=self.generar_receta)
        if self.rol == "Medico":
            self.btn_generar_receta.pack(side="right", padx=5)

        style = ttk.Style()
        style.configure("Treeview", background="#DDDDDD", foreground="black", fieldbackground="#DDDDDD")
        style.configure("Treeview.Heading", background="#CCCCCC", foreground="black")

        self.tree = ttk.Treeview(main_frame, columns=("id", "paciente", "medico", "especialidad", "consultorio", "fecha", "hora", "estado"), show="headings")
        self.tree.column("id", width=60, anchor="center")
        self.tree.column("paciente", width=150)
        self.tree.column("medico", width=150)
        self.tree.column("especialidad", width=120)
        self.tree.column("consultorio", width=120)
        self.tree.column("fecha", width=90, anchor="center")
        self.tree.column("hora", width=70, anchor="center")
        self.tree.column("estado", width=110, anchor="center")
        self.tree.heading("id", text="ID")
        self.tree.heading("paciente", text="Paciente")
        self.tree.heading("medico", text="Médico")
        self.tree.heading("especialidad", text="Especialidad")
        self.tree.heading("consultorio", text="Consultorio")
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("hora", text="Hora")
        self.tree.heading("estado", text="Estado")
        self.tree.pack(padx=10, pady=10, fill="both", expand=True)
        self.tree.tag_configure('asistio', background='#c7f0c1')
        self.tree.tag_configure('inasistencia', background='#f8c0c0')
        self.tree.tag_configure('pendiente', background='#fff3b0')

        if self.rol == "Medico":
            for w in [self.paciente_combo, self.especialidad_combo, self.medico_combo, self.fecha_entry, self.mostrar_horarios_btn, self.slots_listbox]:
                if w: w.configure(state="disabled")
            for child in button_frame.winfo_children():
                if isinstance(child, ttk.Button) and child.cget("text") == "Solicitar Turno":
                    child.pack_forget()
        else:
            for child in [self.btn_ver_hist, self.btn_reg_hist, self.btn_asist, self.btn_inasist]:
                child.pack_forget()

    def cargar_combos(self):
        self.paciente_dao = PacienteDAO()
        self.pacientes = self.paciente_dao.obtener_todos_los_pacientes()
        self.paciente_combo["values"] = [f"{p.nombre} {p.apellido}" for p in self.pacientes]

        self.especialidad_dao = EspecialidadDAO()
        self.especialidades = self.especialidad_dao.obtener_todas_las_especialidades()
        self.especialidad_combo["values"] = [e.nombre for e in self.especialidades]

        self.consultorios = ConsultorioDAO().obtener_todos()

        if self.rol == "Paciente":
            paciente = self.paciente_dao.obtener_paciente_por_usuario(self.usuario)
            if paciente:
                self.paciente_combo.set(f"{paciente.nombre} {paciente.apellido}")
                self.paciente_combo.config(state="disabled")

    def cargar_medicos_por_especialidad(self, event):
        nombre_esp = self.especialidad_combo.get()
        esp = next((e for e in self.especialidades if e.nombre == nombre_esp), None)
        if not esp:
            self.medico_combo["values"] = []
            return
        med_dao = MedicoDAO()
        self.medicos = med_dao.obtener_medicos_por_especialidad(esp.id_especialidad)
        self.medico_combo["values"] = [f"{m.nombre} {m.apellido}" for m in self.medicos]

    def cargar_turnos(self):
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

            self.tree.insert("", "end", values=(t.id_turno, paciente_nombre, medico_nombre, especialidad_nombre, cons_desc, fecha, hora, estado), tags=(tag,))

    def mostrar_horarios_disponibles(self, event=None):
        medico_nombre_completo = self.medico_combo.get()
        try:
            fecha_obj = self.fecha_entry.get_date() 
            fecha = fecha_obj.strftime("%Y-%m-%d")
        except Exception as e:
            messagebox.showerror("Error de fecha", "Fecha inválida. Seleccione una fecha del calendario.")
            return

        # Validar límite de 1 mes
        if fecha_obj > getattr(self, 'fecha_max', fecha_obj):
            messagebox.showerror("Fecha fuera de rango", f"No se pueden solicitar turnos con más de un mes de anticipación. Fecha máxima: {self.fecha_max.strftime('%Y-%m-%d')}")
            self.slots_listbox.delete(0, tk.END)
            return

        if fecha_obj.weekday() >= 5:
            messagebox.showwarning("Día no hábil", "Seleccione un día entre lunes y viernes.")
            self.slots_listbox.delete(0, tk.END) 
            return
        
        id_medico = None
        if hasattr(self, 'medicos'):
            for m in self.medicos:
                if f"{m.nombre} {m.apellido}" == medico_nombre_completo:
                    id_medico = m.id_medico
                    break

        if not id_medico:
            messagebox.showwarning("Advertencia", "Seleccione un médico para ver horarios.")
            return

        if not hasattr(self, 'turno_dao'):
             self.turno_dao = TurnoDAO()
        disponibles = self.turno_dao.calcular_horarios_disponibles(id_medico, fecha)

        self.slots_listbox.delete(0, tk.END)
        if disponibles:
            for h in disponibles:
                self.slots_listbox.insert(tk.END, h)
        else:
            self.slots_listbox.insert(tk.END, "No hay horarios disponibles para este día.")

    def solicitar_turno(self):
        fecha_obj = self.fecha_entry.get_date()
        fecha = fecha_obj.strftime("%Y-%m-%d")
        # Validar límite de 1 mes antes de continuar
        if fecha_obj > getattr(self, 'fecha_max', fecha_obj):
            messagebox.showerror("Fecha fuera de rango", f"No se pueden solicitar turnos con más de un mes de anticipación. Fecha máxima: {self.fecha_max.strftime('%Y-%m-%d')}")
            return
        pac_nombre = self.paciente_combo.get()
        med_nombre = self.medico_combo.get()
        if not (fecha and pac_nombre and med_nombre):
            messagebox.showerror("Error", "Complete todos los campos.")
            return

        selected = self.slots_listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "Seleccione un horario de la lista.")
            return

        hora_seleccionada = self.slots_listbox.get(selected[0])

        pac = next((p for p in self.pacientes if f"{p.nombre} {p.apellido}" == pac_nombre), None)
        med = next((m for m in getattr(self, "medicos", []) if f"{m.nombre} {m.apellido}" == med_nombre), None)

        fecha_hora = f"{fecha} {hora_seleccionada}:00"

        turno = Turno(id_paciente=pac.id_paciente, id_medico=med.id_medico, id_consultorio=None, fecha_hora=fecha_hora)

        id_creado, mensaje = TurnoDAO().crear_turno(turno, self.usuario)
        if id_creado:
            messagebox.showinfo("Éxito", mensaje)
            self.cargar_turnos()
            self.mostrar_horarios_disponibles()
        else:
            messagebox.showerror("Error", mensaje)

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
        if self.rol != "Medico": return
        id_paciente = self._obtener_paciente_seleccionado_de_turno()
        if id_paciente is None: return
        ConsultaHistorial(self, self.usuario, self.rol, id_paciente_fijo=id_paciente)

    def registrar_historial_paciente(self):
        if self.rol != "Medico": return
        id_paciente = self._obtener_paciente_seleccionado_de_turno()
        if id_paciente is None: return
        RegistroHistorial(self, self.usuario, self.rol, id_paciente_fijo=id_paciente)

    def _obtener_id_turno_seleccionado(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Advertencia", "Seleccione un turno de la tabla.")
            return None
        item = self.tree.item(sel[0])
        return item["values"][0]

    def marcar_asistencia(self):
        if self.rol != "Medico": return
        id_turno = self._obtener_id_turno_seleccionado()
        if id_turno is None: return
        ok, msg = TurnoDAO().marcar_asistencia(id_turno, True, self.usuario)
        if ok: messagebox.showinfo("OK", msg)
        else: messagebox.showerror("Error", msg)

    def marcar_inasistencia(self):
        if self.rol != "Medico": return
        id_turno = self._obtener_id_turno_seleccionado()
        if id_turno is None: return
        ok, msg = TurnoDAO().marcar_asistencia(id_turno, False, self.usuario)
        if ok: messagebox.showinfo("OK", msg)
        else: messagebox.showerror("Error", msg)

    def generar_receta(self):
        """Abre un diálogo simple para que el médico ingrese la descripción y genere una receta para el turno seleccionado."""
        if self.rol != "Medico":
            return
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Advertencia", "Seleccione un turno para generar la receta.")
            return
        item = self.tree.item(sel[0])
        id_turno = item['values'][0]
        turno = TurnoDAO().obtener_turno_por_id(id_turno)
        if not turno:
            messagebox.showerror("Error", "No se pudo cargar el turno seleccionado.")
            return

        # Crear ventana modal sencilla
        top = tk.Toplevel(self)
        top.title("Generar Receta")
        top.geometry("500x350")

        ttk.Label(top, text="Descripción / Medicamentos:").pack(padx=10, pady=8, anchor='w')
        text = tk.Text(top, width=60, height=10)
        text.pack(padx=10, pady=5)

        def on_guardar():
            detalles = text.get('1.0', 'end-1c').strip()
            if not detalles:
                if not messagebox.askyesno("Confirmar", "La receta está vacía. Desea crearla igual?"):
                    return
            # Construir objeto receta con atributos que espera RecetaDAO
            class _R: pass
            r = _R()
            r.id_paciente = turno.id_paciente
            r.id_medico = turno.id_medico
            # Validaciones actuales esperan formato YYYY-MM-DD
            r.fecha_emision = datetime.now().strftime("%Y-%m-%d")
            r.detalles = detalles

            from Backend.DAO.RecetaDAO import RecetaDAO
            receta_id = RecetaDAO().crear_receta(r, self.usuario)
            if receta_id:
                messagebox.showinfo("Éxito", f"Receta creada (ID: {receta_id})")
                top.destroy()
            else:
                messagebox.showerror("Error", "No se pudo crear la receta. Revise la consola para más detalles.")

        btn_frame = ttk.Frame(top)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Guardar Receta", command=on_guardar).pack(side='left', padx=8)
        ttk.Button(btn_frame, text="Cancelar", command=top.destroy).pack(side='left', padx=8)
