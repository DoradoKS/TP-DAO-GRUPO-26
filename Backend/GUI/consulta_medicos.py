import tkinter as tk
from tkinter import ttk
from Backend.DAO.MedicoDAO import MedicoDAO

class ConsultaMedicosScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Consulta de Médicos")
        self.geometry("1200x600")
        self.configure(bg="#333333")

        self.medico_dao = MedicoDAO()

        self.create_widgets()
        self.cargar_medicos()

    def create_widgets(self):
        style = ttk.Style(self)
        style.configure("TLabel", background="#333333", foreground="white")
        style.configure("TFrame", background="#333333")
        style.configure("TButton", background="#CCCCCC", foreground="black")
        style.configure("Treeview", background="#DDDDDD", foreground="black", fieldbackground="#DDDDDD")
        style.configure("Treeview.Heading", background="#CCCCCC", foreground="black")

        main_frame = tk.Frame(self, bg="#333333")
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        search_frame = tk.Frame(main_frame, bg="#333333")
        search_frame.pack(fill="x", pady=(0, 10), anchor="w")

        filter_fields_frame = tk.Frame(search_frame, bg="#333333")
        filter_fields_frame.pack(side="left")

        tk.Label(filter_fields_frame, text="Buscar por especialidad:", bg="#333333", fg="white").grid(row=0, column=0, sticky="e", pady=2, padx=5)
        self.especialidad_entry = tk.Entry(filter_fields_frame, width=30)
        self.especialidad_entry.grid(row=0, column=1, sticky="w", pady=2)

        tk.Label(filter_fields_frame, text="Buscar por apellido:", bg="#333333", fg="white").grid(row=1, column=0, sticky="e", pady=2, padx=5)
        self.apellido_entry = tk.Entry(filter_fields_frame, width=30)
        self.apellido_entry.grid(row=1, column=1, sticky="w", pady=2)

        tk.Label(filter_fields_frame, text="Buscar por DNI:", bg="#333333", fg="white").grid(row=2, column=0, sticky="e", pady=2, padx=5)
        self.dni_entry = tk.Entry(filter_fields_frame, width=30)
        self.dni_entry.grid(row=2, column=1, sticky="w", pady=2)

        button_frame = tk.Frame(search_frame, bg="#333333")
        button_frame.pack(side="left", padx=20, anchor="center")

        search_button = ttk.Button(button_frame, text="Buscar", command=self.buscar_medicos, width=20)
        search_button.pack()
        
        tree_container = tk.Frame(main_frame)
        tree_container.pack(expand=True, fill="both")

        columns = ("ID", "Usuario", "Matrícula", "Nombre", "Apellido", "Tipo DNI", "DNI", "Calle", "N°", "Email", "Teléfono", "Especialidad")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("N°", width=50, anchor="center")
        self.tree.column("Nombre", width=120)
        self.tree.column("Apellido", width=120)
        self.tree.column("Email", width=150)
        self.tree.column("Especialidad", width=120)

        self.tree.pack(side="left", expand=True, fill="both")
        
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def cargar_medicos(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        medicos = self.medico_dao.obtener_medicos_con_especialidad()
        for medico in medicos:
            self.tree.insert("", "end", values=medico)

    def buscar_medicos(self):
        especialidad = self.especialidad_entry.get()
        apellido = self.apellido_entry.get()
        dni = self.dni_entry.get()

        for i in self.tree.get_children():
            self.tree.delete(i)

        medicos = self.medico_dao.buscar_medicos(especialidad, apellido, dni)
        for medico in medicos:
            self.tree.insert("", "end", values=medico)
