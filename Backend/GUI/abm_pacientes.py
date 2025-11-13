import tkinter as tk
from tkinter import ttk, messagebox
from Backend.DAO.PacienteDAO import PacienteDAO
from Backend.Model.Paciente import Paciente

class GestionPacientes(tk.Toplevel):
    def __init__(self, parent, usuario="admin"):
        super().__init__(parent)
        self.title("Gestión de Pacientes (Modificar / Baja)")
        self.geometry("900x600")
        self.configure(bg="#333333")
        self.usuario = usuario
        self.selected_paciente_id = None
        self.entries = {}

        self.create_widgets()
        self.cargar_pacientes()

    def create_widgets(self):
        main_frame = tk.Frame(self, bg="#333333")
        main_frame.pack(expand=True, fill="both")

        form_frame = tk.LabelFrame(main_frame, text="Datos del Paciente Seleccionado", bg="#333333", fg="white", padx=10, pady=10)
        form_frame.pack(padx=10, pady=10, fill="x")

        fields = [
            ("Nombre:", "Entry"), ("Apellido:", "Entry"), ("DNI:", "Entry"),
            ("Tipo DNI:", "Combobox"), ("Fecha Nacimiento:", "Entry"), 
            ("Teléfono:", "Entry"), ("Email:", "Entry")
        ]

        for i, (label_text, widget_type) in enumerate(fields):
            label = tk.Label(form_frame, text=label_text, bg="#333333", fg="white")
            label.grid(row=i, column=0, padx=5, pady=5, sticky="e")

            if widget_type == "Entry":
                entry = ttk.Entry(form_frame, width=40)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
                self.entries[label_text] = entry
            elif widget_type == "Combobox":
                self.tipo_dni_combo = ttk.Combobox(form_frame, width=38, state="readonly", values=["DNI", "Pasaporte", "Libreta de Enrolamiento", "Libreta Cívica"])
                self.tipo_dni_combo.grid(row=i, column=1, padx=5, pady=5, sticky="w")

        button_frame = tk.Frame(main_frame, bg="#333333")
        button_frame.pack(padx=10, pady=5, fill="x")

        self.modificacion_button = ttk.Button(button_frame, text="Guardar Modificación", command=self.modificacion_paciente)
        self.modificacion_button.pack(side="left", padx=10)

        self.baja_button = ttk.Button(button_frame, text="Eliminar Seleccionado", command=self.baja_paciente)
        self.baja_button.pack(side="left", padx=10)
        
        tree_frame = tk.Frame(main_frame, bg="#333333")
        tree_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        tk.Label(tree_frame, text="Seleccione un paciente para modificar o eliminar:", bg="#333333", fg="white").pack(anchor="w")

        style = ttk.Style()
        style.configure("Treeview", background="#DDDDDD", foreground="black", fieldbackground="#DDDDDD")
        style.configure("Treeview.Heading", background="#CCCCCC", foreground="black")

        self.tree = ttk.Treeview(tree_frame, columns=("id", "nombre", "apellido", "dni"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("apellido", text="Apellido")
        self.tree.heading("dni", text="DNI")
        
        self.tree.column("id", width=50, anchor="center", stretch=tk.NO)
        self.tree.column("nombre", width=200)
        self.tree.column("apellido", width=200)
        self.tree.column("dni", width=100)

        self.tree.pack(fill="both", expand=True, side="left")
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_paciente)

    def cargar_pacientes(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        paciente_dao = PacienteDAO()
        for p in paciente_dao.obtener_todos_los_pacientes():
            self.tree.insert("", "end", values=(p.id_paciente, p.nombre, p.apellido, p.dni))

    def seleccionar_paciente(self, _):
        selected_item = self.tree.selection()
        if not selected_item: return

        item = self.tree.item(selected_item[0])
        self.selected_paciente_id = item["values"][0]
        
        paciente = PacienteDAO().buscar_paciente_por_id_paciente(self.selected_paciente_id)
        if paciente:
            self.entries["Nombre:"].delete(0, tk.END); self.entries["Nombre:"].insert(0, paciente.nombre)
            self.entries["Apellido:"].delete(0, tk.END); self.entries["Apellido:"].insert(0, paciente.apellido)
            self.entries["DNI:"].delete(0, tk.END); self.entries["DNI:"].insert(0, paciente.dni)
            self.tipo_dni_combo.set(paciente.tipo_dni)
            self.entries["Fecha Nacimiento:"].delete(0, tk.END); self.entries["Fecha Nacimiento:"].insert(0, paciente.fecha_nacimiento)
            self.entries["Teléfono:"].delete(0, tk.END); self.entries["Teléfono:"].insert(0, paciente.telefono)
            self.entries["Email:"].delete(0, tk.END); self.entries["Email:"].insert(0, paciente.email)

    def baja_paciente(self):
        if not self.selected_paciente_id:
            messagebox.showwarning("Acción Requerida", "Por favor, seleccione un paciente de la lista.")
            return

        if messagebox.askyesno("Confirmar Eliminación", "¿Está seguro de que desea eliminar al paciente seleccionado?"):
            exito, mensaje = PacienteDAO().eliminar_paciente(self.selected_paciente_id, self.usuario)
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                self.cargar_pacientes()
                for entry in self.entries.values(): entry.delete(0, tk.END)
                self.tipo_dni_combo.set("")
                self.selected_paciente_id = None
            else:
                messagebox.showerror("Error", mensaje)

    def modificacion_paciente(self):
        if not self.selected_paciente_id:
            messagebox.showwarning("Acción Requerida", "Por favor, seleccione un paciente de la lista.")
            return

        paciente_original = PacienteDAO().buscar_paciente_por_id_paciente(self.selected_paciente_id)
        if not paciente_original:
            messagebox.showerror("Error", "No se pudo obtener el paciente.")
            return

        paciente = Paciente(
            id_paciente=self.selected_paciente_id,
            id_barrio=paciente_original.id_barrio,
            usuario=paciente_original.usuario,
            nombre=self.entries["Nombre:"].get(),
            apellido=self.entries["Apellido:"].get(),
            fecha_nacimiento=self.entries["Fecha Nacimiento:"].get(),
            tipo_dni=self.tipo_dni_combo.get(),
            dni=self.entries["DNI:"].get(),
            email=self.entries["Email:"].get(),
            telefono=self.entries["Teléfono:"].get(),
            id_obra_social=paciente_original.id_obra_social,
            calle=paciente_original.calle,
            numero_calle=paciente_original.numero_calle
        )
        
        exito, mensaje = PacienteDAO().actualizar_paciente(paciente, self.usuario)
        if exito:
            messagebox.showinfo("Éxito", mensaje)
            self.cargar_pacientes()
        else:
            messagebox.showerror("Error", mensaje)
