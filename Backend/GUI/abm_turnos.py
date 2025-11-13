import tkinter as tk
from tkinter import ttk, messagebox

from Backend.DAO.TurnoDAO import TurnoDAO
from Backend.DAO.PacienteDAO import PacienteDAO
from Backend.DAO.MedicoDAO import MedicoDAO
from Backend.DAO.EspecialidadDAO import EspecialidadDAO
from Backend.Model.Turno import Turno

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

        # ---------------------- FECHA ----------------------
        ttk.Label(form_frame, text="Fecha (YYYY-MM-DD):").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.fecha_entry = DateEntry(
            form_frame,
            width=20,
            date_pattern="yyyy-mm-dd",
            background="darkblue",
            foreground="white"
        )
        self.fecha_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        self.mostrar_horarios_btn = ttk.Button(
            form_frame,
            text="Mostrar horarios disponibles",
            command=self.mostrar_horarios_disponibles
        )
        self.mostrar_horarios_btn.grid(row=3, column=2, padx=5, pady=5, sticky="w")

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

        # ------------------ TREEVIEW ------------------
        self.tree = ttk.Treeview(self, columns=("id", "paciente", "medico", "especialidad", "fecha", "hora"), show="headings")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("paciente", width=150)
        self.tree.column("medico", width=150)
        self.tree.column("especialidad", width=120)
        self.tree.column("fecha", width=90, anchor="center")
        self.tree.column("hora", width=70, anchor="center")


        self.tree.pack(padx=10, pady=10, fill="both", expand=True)


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

            paciente_nombre = f"{pac.nombre} {pac.apellido}" if pac else "N/A"
            medico_nombre = f"{med.nombre} {med.apellido}" if med else "N/A"
            especialidad_nombre = esp.nombre if esp else "N/A"

            fecha, hora = t.fecha_hora.split(" ")

            self.tree.insert("", "end", values=(
                t.id_turno,
                paciente_nombre,
                medico_nombre,
                especialidad_nombre,
                fecha,
                hora
            ))



    # ---------------------------------------------------------
    # MOSTRAR HORARIOS DISPONIBLES
    # ---------------------------------------------------------
    def generar_franjas(self):
        franjas = []
        actual = datetime.strptime("08:00", "%H:%M")
        fin = datetime.strptime("14:00", "%H:%M")

        while actual <= fin:
            franjas.append(actual.strftime("%H:%M"))
            actual += timedelta(minutes=30)

        return franjas


    def mostrar_horarios_disponibles(self):
        fecha = self.fecha_entry.get()

        if not validar_fecha(fecha):
            messagebox.showerror("Error", "Fecha inválida.")
            return

        medico_nombre = self.medico_combo.get()
        med = next((m for m in getattr(self, "medicos", []) if f"{m.nombre} {m.apellido}" == medico_nombre), None)

        if not med:
            messagebox.showwarning("Advertencia", "Seleccione un médico.")
            return

        turno_dao = TurnoDAO()

        ocupados = turno_dao.obtener_turnos_por_medico_y_fecha(med.id_medico, fecha)
        horas_ocupadas = {t.fecha_hora.split(" ")[1][:5] for t in ocupados}

        franjas = self.generar_franjas()
        disponibles = [f for f in franjas if f not in horas_ocupadas]

        self.slots_listbox.delete(0, tk.END)
        for h in disponibles:
            self.slots_listbox.insert(tk.END, h)


    # ---------------------------------------------------------
    # SOLICITAR TURNO
    # ---------------------------------------------------------
    def solicitar_turno(self):
        fecha = self.fecha_entry.get()
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
            fecha_hora=fecha_hora
        )

        if TurnoDAO().crear_turno(turno, self.usuario):
            messagebox.showinfo("OK", "Turno creado correctamente.")
            self.cargar_turnos()
            self.mostrar_horarios_disponibles()
        else:
            messagebox.showerror("Error", "No se pudo crear el turno.")


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
