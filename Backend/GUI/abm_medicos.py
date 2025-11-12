import tkinter as tk
from tkinter import ttk, messagebox
from Backend.DAO.MedicoDAO import MedicoDAO
from Backend.DAO.EspecialidadDAO import EspecialidadDAO
from Backend.Model.Medico import Medico

class GestionMedicos(tk.Toplevel):
    def __init__(self, parent, usuario="admin"):
        super().__init__(parent)
        self.title("Gestión de Médicos (Modificar / Baja)")
        self.geometry("900x600")
        self.usuario = usuario

        self.entries = {}
        self.especialidades = []

        self.create_widgets()
        self.cargar_especialidades()
        self.cargar_medicos()

    def create_widgets(self):
        form_frame = ttk.LabelFrame(self, text="Datos del Médico Seleccionado")
        form_frame.pack(padx=10, pady=10, fill="x")

        labels = ["Nombre:", "Apellido:", "DNI:", "Tipo DNI:", "Matrícula:", "Teléfono:", "Email:"]
        for i, label_text in enumerate(labels):
            ttk.Label(form_frame, text=label_text).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            entry = ttk.Entry(form_frame, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
            self.entries[label_text] = entry
        
        ttk.Label(form_frame, text="Especialidad:").grid(row=len(labels), column=0, padx=5, pady=5, sticky="e")
        self.especialidad_combo = ttk.Combobox(form_frame, width=38)
        self.especialidad_combo.grid(row=len(labels), column=1, padx=5, pady=5, sticky="w")

        button_frame = ttk.Frame(self)
        button_frame.pack(padx=10, pady=5, fill="x")

        self.modificacion_button = ttk.Button(button_frame, text="Guardar Modificación", command=self.modificacion_medico)
        self.modificacion_button.pack(side="left", padx=10)

        self.baja_button = ttk.Button(button_frame, text="Eliminar Seleccionado", command=self.baja_medico)
        self.baja_button.pack(side="left", padx=10)
        
        tree_frame = ttk.Frame(self)
        tree_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        ttk.Label(tree_frame, text="Seleccione un médico para modificar o eliminar:").pack(anchor="w")

        self.tree = ttk.Treeview(tree_frame, columns=("id", "nombre", "apellido", "dni", "matricula"), show="headings")
        self.tree.heading("id", text="ID"); self.tree.heading("nombre", text="Nombre"); self.tree.heading("apellido", text="Apellido")
        self.tree.heading("dni", text="DNI"); self.tree.heading("matricula", text="Matrícula")
        
        self.tree.column("id", width=50, anchor="center", stretch=tk.NO)
        self.tree.column("nombre", width=150); self.tree.column("apellido", width=150)
        self.tree.column("dni", width=100); self.tree.column("matricula", width=100)

        self.tree.pack(fill="both", expand=True, side="left")
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_medico)

    def cargar_medicos(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for m in MedicoDAO().obtener_todos_los_medicos():
            self.tree.insert("", "end", values=(m.id_medico, m.nombre, m.apellido, m.dni, m.matricula))

    def cargar_especialidades(self):
        self.especialidades = EspecialidadDAO().obtener_todas_las_especialidades()
        self.especialidad_combo["values"] = [e.nombre for e in self.especialidades]

    def seleccionar_medico(self, _):
        selected_item = self.tree.selection()
        if not selected_item: return

        item = self.tree.item(selected_item[0])
        id_medico = item["values"][0]
        
        medico = MedicoDAO().obtener_medico_por_id(id_medico)
        if medico:
            self.entries["Nombre:"].delete(0, tk.END); self.entries["Nombre:"].insert(0, medico.nombre)
            self.entries["Apellido:"].delete(0, tk.END); self.entries["Apellido:"].insert(0, medico.apellido)
            self.entries["DNI:"].delete(0, tk.END); self.entries["DNI:"].insert(0, medico.dni)
            self.entries["Tipo DNI:"].delete(0, tk.END); self.entries["Tipo DNI:"].insert(0, medico.tipo_dni)
            self.entries["Matrícula:"].delete(0, tk.END); self.entries["Matrícula:"].insert(0, medico.matricula)
            self.entries["Teléfono:"].delete(0, tk.END); self.entries["Teléfono:"].insert(0, medico.telefono)
            self.entries["Email:"].delete(0, tk.END); self.entries["Email:"].insert(0, medico.email)
            
            especialidad_nombre = next((e.nombre for e in self.especialidades if e.id_especialidad == medico.id_especialidad), "")
            self.especialidad_combo.set(especialidad_nombre)

    def baja_medico(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Acción Requerida", "Por favor, seleccione un médico de la lista.")
            return

        if messagebox.askyesno("Confirmar Eliminación", "¿Está seguro de que desea eliminar al médico seleccionado?"):
            item = self.tree.item(selected_item[0])
            id_medico = item["values"][0]
            
            exito, mensaje = MedicoDAO().eliminar_medico(id_medico, self.usuario)
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                self.cargar_medicos()
                for entry in self.entries.values(): entry.delete(0, tk.END)
                self.especialidad_combo.set("")
            else:
                messagebox.showerror("Error", mensaje)

    def modificacion_medico(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Acción Requerida", "Por favor, seleccione un médico de la lista.")
            return

        item = self.tree.item(selected_item[0])
        id_medico = item["values"][0]
        
        # Obtener el médico original para preservar el usuario
        medico_original = MedicoDAO().obtener_medico_por_id(id_medico)
        if not medico_original:
            messagebox.showerror("Error", "No se pudo obtener el médico.")
            return
        
        id_especialidad = next((e.id_especialidad for e in self.especialidades if e.nombre == self.especialidad_combo.get()), None)

        medico = Medico(
            id_medico=id_medico,
            usuario=medico_original.usuario,  # Mantener el usuario original (FK a tabla Usuario)
            nombre=self.entries["Nombre:"].get(),
            apellido=self.entries["Apellido:"].get(),
            matricula=self.entries["Matrícula:"].get(),
            tipo_dni=self.entries["Tipo DNI:"].get(),
            dni=self.entries["DNI:"].get(),
            email=self.entries["Email:"].get(),
            telefono=self.entries["Teléfono:"].get(),
            id_especialidad=id_especialidad,
            calle=medico_original.calle if medico_original.calle else "Default",
            numero_calle=medico_original.numero_calle if medico_original.numero_calle else 123
        )
        
        exito, mensaje = MedicoDAO().actualizar_medico(medico, self.usuario)
        if exito:
            messagebox.showinfo("Éxito", mensaje)
            self.cargar_medicos()
        else:
            messagebox.showerror("Error", mensaje)
