import tkinter as tk
from tkinter import ttk, messagebox
from Backend.DAO.EspecialidadDAO import EspecialidadDAO
from Backend.Model.Especialidad import Especialidad
from Backend.Validaciones.validaciones import Validaciones

class GestionEspecialidades(tk.Toplevel):
    def __init__(self, parent, usuario="admin"):
        super().__init__(parent)
        self.title("Gestión de Especialidades (Modificar / Baja)")
        self.geometry("800x500")
        self.configure(bg="#333333")
        self.usuario = usuario

        self.create_widgets()
        self.cargar_especialidades()

    def create_widgets(self):
        main_frame = tk.Frame(self, bg="#333333")
        main_frame.pack(expand=True, fill="both")

        form_frame = tk.LabelFrame(main_frame, text="Datos de la Especialidad Seleccionada", bg="#333333", fg="white", padx=10, pady=10)
        form_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(form_frame, text="Nombre:", bg="#333333", fg="white").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.nombre_entry = ttk.Entry(form_frame, width=40)
        self.nombre_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(form_frame, text="Descripción:", bg="#333333", fg="white").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.descripcion_entry = ttk.Entry(form_frame, width=40)
        self.descripcion_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        button_frame = tk.Frame(main_frame, bg="#333333")
        button_frame.pack(padx=10, pady=5, fill="x")

        self.modificacion_button = ttk.Button(button_frame, text="Guardar Modificación", command=self.modificacion_especialidad)
        self.modificacion_button.pack(side="left", padx=10)

        self.baja_button = ttk.Button(button_frame, text="Eliminar Seleccionada", command=self.baja_especialidad)
        self.baja_button.pack(side="left", padx=10)
        
        tree_frame = tk.Frame(main_frame, bg="#333333")
        tree_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        tk.Label(tree_frame, text="Seleccione una especialidad para modificarla o eliminarla:", bg="#333333", fg="white").pack(anchor="w")

        style = ttk.Style()
        style.configure("Treeview", background="#DDDDDD", foreground="black", fieldbackground="#DDDDDD")
        style.configure("Treeview.Heading", background="#CCCCCC", foreground="black")

        self.tree = ttk.Treeview(tree_frame, columns=("id", "nombre", "descripcion"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("descripcion", text="Descripción")
        
        self.tree.column("id", width=50, anchor="center", stretch=tk.NO)
        self.tree.column("nombre", width=200, stretch=tk.NO)
        self.tree.column("descripcion", width=500)

        self.tree.pack(fill="both", expand=True, side="left")
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_especialidad)

    def cargar_especialidades(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        especialidad_dao = EspecialidadDAO()
        especialidades = especialidad_dao.get_all()
        for e in especialidades:
            self.tree.insert("", "end", values=(e.id_especialidad, e.nombre, e.descripcion))

    def seleccionar_especialidad(self, _):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        item = self.tree.item(selected_item[0])
        nombre = item["values"][1]
        descripcion = item["values"][2]
        
        self.nombre_entry.delete(0, tk.END)
        self.nombre_entry.insert(0, nombre)
        self.descripcion_entry.delete(0, tk.END)
        self.descripcion_entry.insert(0, descripcion)

    def baja_especialidad(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Acción Requerida", "Por favor, seleccione una especialidad de la lista para eliminar.")
            return

        if messagebox.askyesno("Confirmar Eliminación", "¿Está seguro de que desea eliminar la especialidad seleccionada?"):
            item = self.tree.item(selected_item[0])
            id_especialidad = item["values"][0]
            
            especialidad_dao = EspecialidadDAO()
            exito, mensaje = especialidad_dao.eliminar_especialidad(id_especialidad, self.usuario)
            
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                self.cargar_especialidades()
                self.nombre_entry.delete(0, tk.END)
                self.descripcion_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", mensaje)

    def modificacion_especialidad(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Acción Requerida", "Por favor, seleccione una especialidad de la lista para modificar.")
            return

        item = self.tree.item(selected_item[0])
        id_especialidad = item["values"][0]

        nombre_nuevo = self.nombre_entry.get().strip()
        descripcion_nueva = self.descripcion_entry.get().strip()

        es_valido, errores = Validaciones.validar_campos_requeridos({"nombre": nombre_nuevo}, ["nombre"])
        if not es_valido:
            messagebox.showerror("Error de Validación", errores[0])
            return

        especialidad = Especialidad(id_especialidad=id_especialidad, nombre=nombre_nuevo, descripcion=descripcion_nueva)
        especialidad_dao = EspecialidadDAO()
        
        exito, mensaje = especialidad_dao.actualizar_especialidad(especialidad, self.usuario)

        if exito:
            messagebox.showinfo("Éxito", mensaje)
            self.cargar_especialidades()
        else:
            messagebox.showerror("Error", mensaje)
