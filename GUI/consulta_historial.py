import tkinter as tk
from tkinter import ttk, messagebox
from Backend.DAO.HistorialDAO import HistorialDAO
from Backend.DAO.PacienteDAO import PacienteDAO

class ConsultaHistorial(tk.Toplevel):
    def __init__(self, parent, usuario, rol, id_paciente_fijo=None):
        super().__init__(parent)
        self.title("Consulta de Historial Clínico")
        self.geometry("800x500")
        self.configure(bg="#333333")

        self.usuario = usuario
        self.rol = rol
        self.id_paciente_fijo = id_paciente_fijo

        self.create_widgets()
        self.cargar_pacientes()

        if self.id_paciente_fijo:
            self.paciente_combo.config(state='disabled')
            self.cargar_historial_fijo()

    def create_widgets(self):
        main_frame = tk.Frame(self, bg="#333333")
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        filter_frame = tk.Frame(main_frame, bg="#333333")
        filter_frame.pack(fill='x', pady=5)

        tk.Label(filter_frame, text="Seleccionar Paciente:", bg="#333333", fg="white").pack(side='left', padx=(0, 5))
        self.paciente_combo = ttk.Combobox(filter_frame, width=40, state='readonly')
        self.paciente_combo.pack(side='left')
        self.paciente_combo.bind('<<ComboboxSelected>>', self.on_paciente_select)

        self.tree = ttk.Treeview(main_frame, columns=('fecha', 'medico', 'diagnostico'), show='headings')
        self.tree.heading('fecha', text='Fecha')
        self.tree.heading('medico', text='Médico')
        self.tree.heading('diagnostico', text='Diagnóstico y Observaciones')
        self.tree.column('fecha', width=120)
        self.tree.column('medico', width=150)
        self.tree.column('diagnostico', width=500)
        self.tree.pack(fill='both', expand=True, pady=(10, 0))

    def cargar_pacientes(self):
        if self.rol == 'Paciente':
            paciente = PacienteDAO().obtener_paciente_por_usuario(self.usuario)
            if paciente:
                self.pacientes = [paciente]
                self.paciente_combo['values'] = [f"{paciente.nombre} {paciente.apellido}"]
                self.paciente_combo.current(0)
                self.paciente_combo.config(state='disabled')
                self.on_paciente_select(None)
        else: # Admin o Medico
            self.pacientes = PacienteDAO().obtener_todos_los_pacientes()
            self.paciente_combo['values'] = [f"{p.nombre} {p.apellido}" for p in self.pacientes]

    def cargar_historial_fijo(self):
        paciente = PacienteDAO().buscar_paciente_por_id_paciente(self.id_paciente_fijo)
        if paciente:
            self.paciente_combo['values'] = [f"{paciente.nombre} {paciente.apellido}"]
            self.paciente_combo.current(0)
            self.on_paciente_select(None)

    def on_paciente_select(self, event):
        for i in self.tree.get_children():
            self.tree.delete(i)

        idx = self.paciente_combo.current()
        if idx < 0: return

        id_paciente = self.pacientes[idx].id_paciente
        historial_data, msg = HistorialDAO().obtener_historial_por_paciente(id_paciente, self.usuario)

        if not historial_data:
            messagebox.showinfo("Información", "El paciente no tiene historial clínico registrado.", parent=self)
            return

        for entrada in historial_data:
            self.tree.insert('', 'end', values=(entrada["fecha"], entrada["medico"], entrada["diagnostico"]))
