import tkinter as tk
from tkinter import ttk, messagebox
from Backend.DAO.HistorialDAO import HistorialDAO
from Backend.DAO.PacienteDAO import PacienteDAO
from Backend.DAO.MedicoDAO import MedicoDAO


class ConsultaHistorial(tk.Toplevel):
    """Ventana para consultar el historial clínico de un paciente."""
    
    def __init__(self, parent, usuario, rol, id_paciente_fijo=None):
        super().__init__(parent)
        self.title("Consulta de Historial Clínico")
        self.geometry("900x650")
        self.usuario = usuario
        self.rol = rol
        self.id_paciente_fijo = id_paciente_fijo
        self.pacientes = []
        self.historiales = []
        
        self.create_widgets()
        self.configurar_acceso()

    def create_widgets(self):
        # Frame superior - Selección de paciente
        top_frame = ttk.LabelFrame(self, text="Seleccionar Paciente")
        top_frame.pack(padx=15, pady=10, fill="x")

        ttk.Label(top_frame, text="Paciente:").pack(side="left", padx=10, pady=10)
        self.paciente_combo = ttk.Combobox(top_frame, width=50, state="readonly")
        self.paciente_combo.pack(side="left", padx=10, pady=10)
        
        ttk.Button(top_frame, text="Consultar Historial", command=self.consultar_historial).pack(side="left", padx=10)

        # Frame medio - Lista de entradas
        list_frame = ttk.LabelFrame(self, text="Entradas del Historial")
        list_frame.pack(padx=15, pady=10, fill="both", expand=True)

        # Treeview
        columns = ("id", "fecha", "medico", "diagnostico")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        self.tree.heading("id", text="ID")
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("medico", text="Médico")
        self.tree.heading("diagnostico", text="Diagnóstico")
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("fecha", width=150)
        self.tree.column("medico", width=200)
        self.tree.column("diagnostico", width=400)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.bind("<<TreeviewSelect>>", self.mostrar_detalle)

        # Frame inferior - Detalle de entrada seleccionada
        detail_frame = ttk.LabelFrame(self, text="Detalle de la Entrada")
        detail_frame.pack(padx=15, pady=10, fill="both")

        ttk.Label(detail_frame, text="Diagnóstico:").grid(row=0, column=0, padx=10, pady=5, sticky="nw")
        self.diagnostico_text = tk.Text(detail_frame, width=70, height=4, wrap="word", state="disabled")
        self.diagnostico_text.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(detail_frame, text="Observaciones:").grid(row=1, column=0, padx=10, pady=5, sticky="nw")
        self.observaciones_text = tk.Text(detail_frame, width=70, height=4, wrap="word", state="disabled")
        self.observaciones_text.grid(row=1, column=1, padx=10, pady=5)

    def configurar_acceso(self):
        """Configura el acceso según el rol del usuario."""
        if self.id_paciente_fijo is not None:
            paciente = PacienteDAO().buscar_paciente_por_id_paciente(self.id_paciente_fijo)
            if paciente:
                self.pacientes = [paciente]
                self.paciente_combo['values'] = [f"{paciente.apellido}, {paciente.nombre} (DNI: {paciente.dni})"]
                self.paciente_combo.current(0)
                self.paciente_combo.config(state="disabled")
                self.consultar_historial()
            else:
                messagebox.showerror("Error", "Paciente no encontrado.")
                self.destroy()
        elif self.rol == "Paciente":
            # Pacientes solo ven su propio historial
            paciente = PacienteDAO().obtener_paciente_por_usuario(self.usuario)
            if paciente:
                self.pacientes = [paciente]
                self.paciente_combo['values'] = [f"{paciente.apellido}, {paciente.nombre} (DNI: {paciente.dni})"]
                self.paciente_combo.current(0)
                self.paciente_combo.config(state="disabled")
                self.consultar_historial()  # Auto-cargar
        elif self.rol in ["Medico", "Administrador"]:
            # Médicos y admins ven todos los pacientes
            self.pacientes = PacienteDAO().obtener_todos_los_pacientes()
            self.paciente_combo['values'] = [f"{p.apellido}, {p.nombre} (DNI: {p.dni})" for p in self.pacientes]
        else:
            messagebox.showerror("Error", "No tiene permisos para consultar historiales.")
            self.destroy()

    def consultar_historial(self):
        sel_index = self.paciente_combo.current()
        if sel_index == -1:
            messagebox.showwarning("Advertencia", "Debe seleccionar un paciente.")
            return

        paciente = self.pacientes[sel_index]
        historial_dao = HistorialDAO()
        self.historiales, mensaje = historial_dao.obtener_historial_por_paciente(paciente.id_paciente, self.usuario)

        # Limpiar tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not self.historiales:
            if "Permiso denegado" in mensaje:
                messagebox.showerror("Error", mensaje)
            else:
                messagebox.showinfo("Info", "No hay entradas en el historial de este paciente.")
            return

        # Cargar entradas
        for h in self.historiales:
            medico = MedicoDAO().obtener_medico_por_id(h.id_medico)
            medico_nombre = f"Dr./Dra. {medico.apellido}, {medico.nombre}" if medico else "Desconocido"
            diagnostico_preview = h.diagnostico[:60] + "..." if h.diagnostico and len(h.diagnostico) > 60 else h.diagnostico
            
            self.tree.insert("", "end", values=(
                h.id_historial,
                h.fecha,
                medico_nombre,
                diagnostico_preview
            ))

    def mostrar_detalle(self, event):
        sel = self.tree.selection()
        if not sel:
            return

        item = self.tree.item(sel[0])
        id_historial = item['values'][0]
        
        # Buscar el historial completo
        historial = next((h for h in self.historiales if h.id_historial == id_historial), None)
        if not historial:
            return

        # Mostrar detalle
        self.diagnostico_text.config(state="normal")
        self.diagnostico_text.delete("1.0", "end")
        self.diagnostico_text.insert("1.0", historial.diagnostico or "Sin diagnóstico")
        self.diagnostico_text.config(state="disabled")

        self.observaciones_text.config(state="normal")
        self.observaciones_text.delete("1.0", "end")
        self.observaciones_text.insert("1.0", historial.observaciones or "Sin observaciones")
        self.observaciones_text.config(state="disabled")
