import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from Backend.DAO.HistorialDAO import HistorialDAO
from Backend.DAO.PacienteDAO import PacienteDAO
from Backend.DAO.MedicoDAO import MedicoDAO
from Backend.Model.Historial import Historial


class RegistroHistorial(tk.Toplevel):
    """Ventana para que los médicos registren entradas en el historial clínico."""
    
    def __init__(self, parent, usuario, rol, id_paciente_fijo=None):
        super().__init__(parent)
        self.title("Registro de Historial Clínico")
        self.geometry("700x500")
        self.usuario = usuario
        self.rol = rol
        self.id_paciente_fijo = id_paciente_fijo
        self.pacientes = []
        
        if rol != "Medico":
            messagebox.showerror("Error", "Solo médicos pueden registrar en el historial.")
            self.destroy()
            return
        
        self.create_widgets()
        self.cargar_pacientes()

    def create_widgets(self):
        form_frame = ttk.LabelFrame(self, text="Nueva Entrada de Historial")
        form_frame.pack(padx=20, pady=15, fill="both", expand=True)

        # Selección de paciente
        ttk.Label(form_frame, text="Paciente:").grid(row=0, column=0, padx=10, pady=8, sticky="e")
        self.paciente_combo = ttk.Combobox(form_frame, width=45, state="readonly")
        self.paciente_combo.grid(row=0, column=1, padx=10, pady=8, sticky="w")

        # Fecha (automática, solo informativa)
        ttk.Label(form_frame, text="Fecha:").grid(row=1, column=0, padx=10, pady=8, sticky="e")
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.fecha_label = ttk.Label(form_frame, text=fecha_actual, font=("Arial", 10, "bold"))
        self.fecha_label.grid(row=1, column=1, padx=10, pady=8, sticky="w")

        # Diagnóstico
        ttk.Label(form_frame, text="Diagnóstico:*").grid(row=2, column=0, padx=10, pady=8, sticky="ne")
        self.diagnostico_text = tk.Text(form_frame, width=50, height=6, wrap="word")
        self.diagnostico_text.grid(row=2, column=1, padx=10, pady=8)

        # Observaciones
        ttk.Label(form_frame, text="Observaciones:").grid(row=3, column=0, padx=10, pady=8, sticky="ne")
        self.observaciones_text = tk.Text(form_frame, width=50, height=6, wrap="word")
        self.observaciones_text.grid(row=3, column=1, padx=10, pady=8)

        # Botones
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=15)
        
        ttk.Button(button_frame, text="Guardar Entrada", command=self.guardar_entrada).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Cancelar", command=self.destroy).pack(side="left", padx=10)

    def cargar_pacientes(self):
        if self.id_paciente_fijo is not None:
            paciente = PacienteDAO().buscar_paciente_por_id_paciente(self.id_paciente_fijo)
            if paciente:
                self.pacientes = [paciente]
                self.paciente_combo['values'] = [f"{paciente.apellido}, {paciente.nombre} (DNI: {paciente.dni})"]
                self.paciente_combo.current(0)
                self.paciente_combo.config(state="disabled")
            else:
                messagebox.showerror("Error", "Paciente no encontrado.")
                self.destroy()
        else:
            self.pacientes = PacienteDAO().obtener_todos_los_pacientes()
            self.paciente_combo['values'] = [f"{p.apellido}, {p.nombre} (DNI: {p.dni})" for p in self.pacientes]

    def guardar_entrada(self):
        sel_index = self.paciente_combo.current()
        if sel_index == -1:
            messagebox.showerror("Error", "Debe seleccionar un paciente.")
            return

        diagnostico = self.diagnostico_text.get("1.0", "end-1c").strip()
        if not diagnostico:
            messagebox.showerror("Error", "El diagnóstico es obligatorio.")
            return

        observaciones = self.observaciones_text.get("1.0", "end-1c").strip()
        
        # Obtener id_medico del usuario actual
        medico = MedicoDAO().obtener_medico_por_usuario(self.usuario)
        if not medico:
            messagebox.showerror("Error", "No se pudo identificar al médico.")
            return

        paciente = self.pacientes[sel_index]
        
        historial = Historial(
            id_paciente=paciente.id_paciente,
            id_medico=medico.id_medico,
            fecha=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            diagnostico=diagnostico,
            observaciones=observaciones
        )

        historial_dao = HistorialDAO()
        id_creado, mensaje = historial_dao.crear_entrada_historial(historial, self.usuario)

        if id_creado:
            messagebox.showinfo("Éxito", f"{mensaje} (ID: {id_creado})")
            self.destroy()
        else:
            messagebox.showerror("Error", mensaje)
