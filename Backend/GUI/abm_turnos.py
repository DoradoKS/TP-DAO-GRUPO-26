import tkinter as tk
from tkinter import ttk, messagebox

# Imports absolutos desde Backend
from Backend.DAO.TurnoDAO import TurnoDAO
from Backend.DAO.PacienteDAO import PacienteDAO
from Backend.DAO.MedicoDAO import MedicoDAO
from Backend.DAO.EspecialidadDAO import EspecialidadDAO
from Backend.Model.Turno import Turno
from Backend.Validaciones.validaciones_turnos import validar_fecha, validar_hora
from tkcalendar import DateEntry  # <<--- AÑADIDO
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

    def create_widgets(self):
        form_frame = ttk.Frame(self)
        form_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(form_frame, text="Paciente:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.paciente_combo = ttk.Combobox(form_frame, width=30)
        self.paciente_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(form_frame, text="Especialidad:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.especialidad_combo = ttk.Combobox(form_frame, width=30)
        self.especialidad_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.especialidad_combo.bind("<<ComboboxSelected>>", self.cargar_medicos_por_especialidad)

        ttk.Label(form_frame, text="Médico:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.medico_combo = ttk.Combobox(form_frame, width=30)
        self.medico_combo.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # ----------- FECHA CON CALENDARIO -------------
        ttk.Label(form_frame, text="Fecha (YYYY-MM-DD):").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.fecha_entry = DateEntry(
            form_frame,
            width=18,
            date_pattern="yyyy-mm-dd",
            background="darkblue",
            foreground="white",
            borderwidth=2
        )
        self.fecha_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        self.mostrar_horarios_btn = ttk.Button(
            form_frame, 
            text="Mostrar horarios disponibles", 
            command=self.mostrar_horarios_disponibles
        )
        self.mostrar_horarios_btn.grid(row=3, column=2, padx=5, pady=5, sticky="w")
        # ------------------------------------------------

        ttk.Label(form_frame, text="Hora (HH:MM):").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.hora_entry = ttk.Entry(form_frame)
        self.hora_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # Lista de horarios
        horarios_frame = ttk.Frame(self)
        horarios_frame.pack(padx=10, pady=5, fill="x")
        ttk.Label(horarios_frame, text="Horarios disponibles:").pack(anchor="w")
        self.slots_listbox = tk.Listbox(horarios_frame, height=8)
        self.slots_listbox.pack(side="left", fill="x", expand=True, padx=(0,5))
        scrollbar = ttk.Scrollbar(horarios_frame, orient="vertical", command=self.slots_listbox.yview)
        scrollbar.pack(side="left", fill="y")
        self.slots_listbox.config(yscrollcommand=scrollbar.set)

        button_frame = ttk.Frame(self)
        button_frame.pack(padx=10, pady=10, fill="x")

        self.alta_button = ttk.Button(button_frame, text="Solicitar Turno", command=self.solicitar_turno)
        self.alta_button.pack(side="left", padx=5)

        self.cancelar_button = ttk.Button(button_frame, text="Cancelar Turno", command=self.cancelar_turno)
        self.cancelar_button.pack(side="left", padx=5)

        self.tree = ttk.Treeview(self, columns=("id", "paciente", "medico", "especialidad", "fecha", "hora"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("paciente", text="Paciente")
        self.tree.heading("medico", text="Médico")
        self.tree.heading("especialidad", text="Especialidad")
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("hora", text="Hora")
        self.tree.pack(padx=10, pady=10, fill="both", expand=True)


    # ==================== RESTO IGUAL ====================
    def cargar_turnos(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        self.turno_dao = TurnoDAO()
        self.paciente_dao = PacienteDAO()
        self.medico_dao = MedicoDAO()
        self.especialidad_dao = EspecialidadDAO()

        turnos = []
        if self.rol == "Administrador":
            turnos = self.turno_dao.obtener_todos_los_turnos()
        elif self.rol == "Medico":
            medico = self.medico_dao.obtener_medico_por_usuario(self.usuario)
            turnos = self.turno_dao.obtener_turnos_por_medico(medico.id_medico) if medico else []
        elif self.rol == "Paciente":
            paciente = self.paciente_dao.obtener_paciente_por_usuario(self.usuario)
            turnos = self.turno_dao.obtener_turnos_por_paciente(paciente.id_paciente) if paciente else []
        
        for t in turnos:
            paciente = self.paciente_dao.buscar_paciente_por_id_paciente(t.id_paciente)
            medico = self.medico_dao.obtener_medico_por_id(t.id_medico)
            especialidad = self.especialidad_dao.obtener_especialidad_por_id(medico.id_especialidad) if medico else None

            paciente_nombre = f"{paciente.nombre} {paciente.apellido}" if paciente else "N/A"
            medico_nombre = f"{medico.nombre} {medico.apellido}" if medico else "N/A"
            especialidad_nombre = especialidad.nombre if especialidad else "N/A"
            
            fecha_hora = t.fecha_hora.split(" ")
            fecha = fecha_hora[0]
            hora = fecha_hora[1][:5]

            self.tree.insert("", "end", values=(t.id_turno, paciente_nombre, medico_nombre, especialidad_nombre, fecha, hora))

    def cargar_combos(self):
        self.paciente_dao = PacienteDAO()
        self.pacientes = self.paciente_dao.obtener_todos_los_pacientes()
        self.paciente_combo["values"] = [f"{p.nombre} {p.apellido}" for p in self.pacientes]

        self.especialidad_dao = EspecialidadDAO()
        self.especialidades = self.especialidad_dao.obtener_todas_las_especialidades()
        self.especialidad_combo["values"] = [e.nombre for e in self.especialidades]

        if self.rol == "Paciente":
            paciente = self.paciente_dao.obtener_paciente_por_usuario(self.usuario)
            if paciente:
                self.paciente_combo.set(f"{paciente.nombre} {paciente.apellido}")
                self.paciente_combo.config(state="disabled")


    def cargar_medicos_por_especialidad(self, event):
        selected_especialidad_nombre = self.especialidad_combo.get()
        id_especialidad = None
        for esp in self.especialidades:
            if esp.nombre == selected_especialidad_nombre:
                id_especialidad = esp.id_especialidad
                break
        
        if id_especialidad:
            self.medico_dao = MedicoDAO()
            self.medicos = self.medico_dao.obtener_medicos_por_especialidad(id_especialidad)
            self.medico_combo["values"] = [f"{m.nombre} {m.apellido}" for m in self.medicos]
        else:
            self.medico_combo["values"] = []
            self.medico_combo.set('')


    def solicitar_turno(self):
        paciente_nombre_completo = self.paciente_combo.get()
        medico_nombre_completo = self.medico_combo.get()
        fecha = self.fecha_entry.get()   # << Calendar da el formato correcto
        hora = self.hora_entry.get()

        if not all([paciente_nombre_completo, medico_nombre_completo, fecha, hora]):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        if not validar_fecha(fecha):
            messagebox.showerror("Error", "La fecha debe tener el formato YYYY-MM-DD.")
            return
        
        if not validar_hora(hora):
            messagebox.showerror("Error", "La hora debe tener el formato HH:MM.")
            return

        id_paciente = None
        for p in self.pacientes:
            if f"{p.nombre} {p.apellido}" == paciente_nombre_completo:
                id_paciente = p.id_paciente
                break

        id_medico = None
        if hasattr(self, 'medicos'):
            for m in self.medicos:
                if f"{m.nombre} {m.apellido}" == medico_nombre_completo:
                    id_medico = m.id_medico
                    break
        
        selected_indices = self.slots_listbox.curselection()
        if selected_indices:
            hora_seleccionada = self.slots_listbox.get(selected_indices[0])
        else:
            hora_seleccionada = hora

        if not validar_hora(hora_seleccionada):
            messagebox.showerror("Error", "La hora debe tener el formato HH:MM.")
            return

        fecha_hora = f"{fecha} {hora_seleccionada}:00"
        turno = Turno(id_paciente=id_paciente, id_medico=id_medico, fecha_hora=fecha_hora)
        
        turno_dao = TurnoDAO()
        if turno_dao.crear_turno(turno, self.usuario):
            messagebox.showinfo("Turno solicitado", "El turno ha sido solicitado exitosamente.")
            self.cargar_turnos()
            self.mostrar_horarios_disponibles()
        else:
            messagebox.showerror("Error", "No se pudo solicitar el turno.")


    def cancelar_turno(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un turno para cancelar.")
            return

        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea cancelar este turno?"):
            item = self.tree.item(selected_item[0])
            id_turno = item["values"][0]
            
            turno_dao = TurnoDAO()
            if turno_dao.eliminar_turno(id_turno, self.usuario):
                messagebox.showinfo("Turno cancelado", "Turno cancelado exitosamente.")
                self.cargar_turnos()
                self.mostrar_horarios_disponibles()
            else:
                messagebox.showerror("Error", "No se pudo cancelar el turno.")


    def generar_franjas(self):
        franjas = []
        inicio = datetime.strptime("08:00", "%H:%M")
        fin = datetime.strptime("14:00", "%H:%M")
        actual = inicio
        while actual <= fin:
            franjas.append(actual.strftime("%H:%M"))
            actual += timedelta(minutes=30)
        return franjas


    def mostrar_horarios_disponibles(self):
        fecha = self.fecha_entry.get()
        medico_nombre_completo = self.medico_combo.get()

        if not validar_fecha(fecha):
            messagebox.showerror("Error de formato", "Fecha inválida.")
            return

        try:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
        except:
            messagebox.showerror("Error", "Fecha inválida.")
            return

        if fecha_obj.weekday() >= 5:
            messagebox.showwarning("Día no hábil", "Solo lunes a viernes.")
            return

        hoy = datetime.today().date()
        max_fecha = hoy + timedelta(days=30)
        if fecha_obj < hoy or fecha_obj > max_fecha:
            messagebox.showwarning("Rango inválido", f"Entre {hoy} y {max_fecha}.")
            return

        id_medico = None
        if hasattr(self, 'medicos'):
            for m in self.medicos:
                if f"{m.nombre} {m.apellido}" == medico_nombre_completo:
                    id_medico = m.id_medico
                    break

        if not id_medico:
            messagebox.showwarning("Advertencia", "Seleccione médico.")
            return

        turno_dao = TurnoDAO()
        ocupados = turno_dao.obtener_turnos_por_medico_y_fecha(id_medico, fecha)
        horas_ocupadas = { t.fecha_hora.split(" ")[1][:5] for t in ocupados }

        franjas = self.generar_franjas()
        disponibles = [h for h in franjas if h not in horas_ocupadas]

        self.slots_listbox.delete(0, tk.END)
        for h in disponibles:
            self.slots_listbox.insert(tk.END, h)
