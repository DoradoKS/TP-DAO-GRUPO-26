import tkinter as tk
from tkinter import ttk, messagebox
from Backend.DAO.MedicoDAO import MedicoDAO
from Backend.DAO.EspecialidadDAO import EspecialidadDAO
from Backend.DAO.BarrioDAO import BarrioDAO
from Backend.Model.Medico import Medico

class GestionMedicos(tk.Toplevel):
    def __init__(self, parent, usuario="admin"):
        super().__init__(parent)
        self.title("Gestión de Médicos (Modificar / Baja)")
        self.geometry("900x600")
        self.configure(bg="#333333")
        self.usuario = usuario

        self.entries = {}
        self.especialidades = []
        self.barrios = []
        self.selected_medico_id = None

        self.create_widgets()
        self.cargar_especialidades()
        self.cargar_barrios()
        self.cargar_medicos()

    def create_widgets(self):
        main_frame = tk.Frame(self, bg="#333333")
        main_frame.pack(expand=True, fill="both")

        form_frame = tk.LabelFrame(main_frame, text="Datos del Médico Seleccionado", bg="#333333", fg="white", padx=10, pady=10)
        form_frame.pack(padx=10, pady=10, fill="x")

        fields = [
            ("Nombre:", "Entry"), ("Apellido:", "Entry"), ("DNI:", "Entry"),
            ("Tipo DNI:", "Combobox"), ("Matrícula:", "Entry"), ("Teléfono:", "Entry"),
            ("Email:", "Entry"), ("Calle:", "Entry"), ("Número:", "Entry"),
            ("Barrio:", "Entry"), ("Especialidad:", "Combobox")
        ]
        
        for i, (label_text, widget_type) in enumerate(fields):
            label = tk.Label(form_frame, text=label_text, bg="#333333", fg="white")
            label.grid(row=i, column=0, padx=5, pady=5, sticky="e")

            if widget_type == "Entry":
                entry = ttk.Entry(form_frame, width=40)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
                self.entries[label_text] = entry
            elif label_text == "Tipo DNI:":
                self.tipo_dni_combo = ttk.Combobox(form_frame, width=38, state="readonly", values=["DNI", "Pasaporte", "Libreta de Enrolamiento", "Libreta Cívica"])
                self.tipo_dni_combo.grid(row=i, column=1, padx=5, pady=5, sticky="w")
            elif label_text == "Barrio:":
                entry = ttk.Entry(form_frame, width=40)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
                self.entries[label_text] = entry
            elif label_text == "Especialidad:":
                self.especialidad_combo = ttk.Combobox(form_frame, width=38, state="readonly")
                self.especialidad_combo.grid(row=i, column=1, padx=5, pady=5, sticky="w")

        button_frame = tk.Frame(main_frame, bg="#333333")
        button_frame.pack(padx=10, pady=5, fill="x")

        self.modificacion_button = ttk.Button(button_frame, text="Guardar Modificación", command=self.modificacion_medico)
        self.modificacion_button.pack(side="left", padx=10)

        self.baja_button = ttk.Button(button_frame, text="Eliminar Seleccionado", command=self.baja_medico)
        self.baja_button.pack(side="left", padx=10)
        
        tree_frame = tk.Frame(main_frame, bg="#333333")
        tree_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        tk.Label(tree_frame, text="Seleccione un médico para modificar o eliminar:", bg="#333333", fg="white").pack(anchor="w")

        style = ttk.Style()
        style.configure("Treeview", background="#DDDDDD", foreground="black", fieldbackground="#DDDDDD")
        style.configure("Treeview.Heading", background="#CCCCCC", foreground="black")

        self.tree = ttk.Treeview(tree_frame, columns=("id", "nombre", "apellido", "dni", "matricula", "especialidad"), show="headings")
        self.tree.heading("id", text="ID"); self.tree.heading("nombre", text="Nombre"); self.tree.heading("apellido", text="Apellido")
        self.tree.heading("dni", text="DNI"); self.tree.heading("matricula", text="Matrícula"); self.tree.heading("especialidad", text="Especialidad")
        
        self.tree.column("id", width=50, anchor="center", stretch=tk.NO)
        self.tree.column("nombre", width=150); self.tree.column("apellido", width=150)
        self.tree.column("dni", width=100); self.tree.column("matricula", width=100); self.tree.column("especialidad", width=150)

        self.tree.pack(fill="both", expand=True, side="left")
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_medico)

    def cargar_medicos(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for m in MedicoDAO().obtener_medicos_con_especialidad():
            self.tree.insert("", "end", values=m)

    def cargar_especialidades(self):
        self.especialidades = EspecialidadDAO().obtener_todas_las_especialidades()
        self.especialidad_combo["values"] = [e.nombre for e in self.especialidades]

    def cargar_barrios(self):
        # Ya no usamos combobox para barrio; solo precargamos lista para mostrar nombre
        self.barrios = BarrioDAO().obtener_todos_los_barrios()

    def seleccionar_medico(self, _):
        selected_item = self.tree.selection()
        if not selected_item: return

        item = self.tree.item(selected_item[0])
        self.selected_medico_id = item["values"][0]
        
        medico = MedicoDAO().obtener_medico_por_id(self.selected_medico_id)
        if medico:
            self.entries["Nombre:"].delete(0, tk.END); self.entries["Nombre:"].insert(0, medico.nombre)
            self.entries["Apellido:"].delete(0, tk.END); self.entries["Apellido:"].insert(0, medico.apellido)
            self.entries["DNI:"].delete(0, tk.END); self.entries["DNI:"].insert(0, medico.dni)
            self.tipo_dni_combo.set(medico.tipo_dni)
            self.entries["Matrícula:"].delete(0, tk.END); self.entries["Matrícula:"].insert(0, medico.matricula)
            self.entries["Teléfono:"].delete(0, tk.END); self.entries["Teléfono:"].insert(0, medico.telefono)
            self.entries["Email:"].delete(0, tk.END); self.entries["Email:"].insert(0, medico.email)
            self.entries["Calle:"].delete(0, tk.END); self.entries["Calle:"].insert(0, medico.calle or "")
            self.entries["Número:"].delete(0, tk.END); self.entries["Número:"].insert(0, str(medico.numero_calle or ""))
            
            barrio_nombre = next((b.nombre for b in self.barrios if b.id_barrio == medico.id_barrio), "")
            self.entries["Barrio:"].delete(0, tk.END)
            self.entries["Barrio:"].insert(0, barrio_nombre)
            
            especialidad_nombre = next((e.nombre for e in self.especialidades if e.id_especialidad == medico.id_especialidad), "")
            self.especialidad_combo.set(especialidad_nombre)

    def baja_medico(self):
        if not self.selected_medico_id:
            messagebox.showwarning("Acción Requerida", "Por favor, seleccione un médico de la lista.")
            return

        if messagebox.askyesno("Confirmar Eliminación", "¿Está seguro de que desea eliminar al médico seleccionado?"):
            exito, mensaje = MedicoDAO().eliminar_medico(self.selected_medico_id, self.usuario)
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                self.cargar_medicos()
                for entry in self.entries.values(): entry.delete(0, tk.END)
                self.especialidad_combo.set("")
                self.entries["Barrio:"].delete(0, tk.END)
                self.tipo_dni_combo.set("")
                self.selected_medico_id = None
            else:
                messagebox.showerror("Error", mensaje)

    def modificacion_medico(self):
        if not self.selected_medico_id:
            messagebox.showwarning("Acción Requerida", "Por favor, seleccione un médico de la lista.")
            return

        medico_original = MedicoDAO().obtener_medico_por_id(self.selected_medico_id)
        if not medico_original:
            messagebox.showerror("Error", "No se pudo obtener el médico.")
            return
        
        id_especialidad = next((e.id_especialidad for e in self.especialidades if e.nombre == self.especialidad_combo.get()), None)
        
        barrio_nombre = self.entries["Barrio:"].get().strip()
        if not barrio_nombre:
            messagebox.showerror("Error", "El barrio es obligatorio.")
            return
        id_barrio = BarrioDAO().obtener_o_crear_barrio(barrio_nombre)
        
        numero_calle_str = self.entries["Número:"].get().strip()
        try:
            numero_calle = int(numero_calle_str) if numero_calle_str else None
        except ValueError:
            messagebox.showerror("Error", "El número de calle debe ser un entero.")
            return

        medico = Medico(
            id_medico=self.selected_medico_id,
            usuario=medico_original.usuario,
            nombre=self.entries["Nombre:"].get(),
            apellido=self.entries["Apellido:"].get(),
            matricula=self.entries["Matrícula:"].get(),
            tipo_dni=self.tipo_dni_combo.get(),
            dni=self.entries["DNI:"].get(),
            email=self.entries["Email:"].get(),
            telefono=self.entries["Teléfono:"].get(),
            id_especialidad=id_especialidad,
            calle=self.entries["Calle:"].get().strip(),
            numero_calle=numero_calle,
            id_barrio=id_barrio
        )
        
        exito, mensaje = MedicoDAO().actualizar_medico(medico, self.usuario)
        if exito:
            messagebox.showinfo("Éxito", mensaje)
            self.cargar_medicos()
        else:
            messagebox.showerror("Error", mensaje)
