import tkinter as tk
from tkinter import ttk

from Backend.DAO.EspecialidadDAO import EspecialidadDAO


class ConsultaEspecialidades(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Consulta de Especialidades")
        self.geometry("800x600")
        self.configure(bg="#333333")

        self.especialidad_dao = EspecialidadDAO()

        self.create_widgets()
        self.cargar_especialidades()

    def create_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self, bg="#333333")
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Frame de búsqueda
        search_frame = tk.Frame(main_frame, bg="#333333")
        search_frame.pack(fill="x", pady=(0, 10), anchor="w")

        # Frame para los campos de filtro
        filter_fields_frame = tk.Frame(search_frame, bg="#333333")
        filter_fields_frame.pack(side="left")

        tk.Label(filter_fields_frame, text="Buscar por ID:", bg="#333333", fg="#FFFFFF").grid(row=0, column=0, sticky="e", pady=2, padx=5)
        self.id_entry = tk.Entry(filter_fields_frame)
        self.id_entry.grid(row=0, column=1, sticky="w", pady=2)

        tk.Label(filter_fields_frame, text="Buscar por Nombre:", bg="#333333", fg="#FFFFFF").grid(row=1, column=0, sticky="e", pady=2, padx=5)
        self.nombre_entry = tk.Entry(filter_fields_frame)
        self.nombre_entry.grid(row=1, column=1, sticky="w", pady=2)

        # Frame para el botón de búsqueda
        button_frame = tk.Frame(search_frame, bg="#333333")
        button_frame.pack(side="left", padx=20, anchor="center")

        search_button = tk.Button(button_frame, text="Buscar...", command=self.buscar_especialidades, width=20)
        search_button.pack()
        
        # Treeview para mostrar especialidades
        tree_container = tk.Frame(main_frame)
        tree_container.pack(expand=True, fill="both")

        self.tree = ttk.Treeview(tree_container, columns=("ID", "Nombre", "Descripción"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Descripción", text="Descripción")

        self.tree.column("ID", width=50, anchor="center", stretch=tk.NO)
        self.tree.column("Nombre", width=200, stretch=tk.NO)
        self.tree.column("Descripción", width=500)

        self.tree.pack(side="left", expand=True, fill="both")
        
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")


    def cargar_especialidades(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        especialidades = self.especialidad_dao.get_all()
        for esp in especialidades:
            self.tree.insert("", "end", values=(esp.id_especialidad, esp.nombre, esp.descripcion))

    def buscar_especialidades(self):
        id_busqueda = self.id_entry.get()
        nombre_busqueda = self.nombre_entry.get()

        for i in self.tree.get_children():
            self.tree.delete(i)

        especialidades = self.especialidad_dao.search(id_busqueda, nombre_busqueda)
        for esp in especialidades:
            self.tree.insert("", "end", values=(esp.id_especialidad, esp.nombre, esp.descripcion))
