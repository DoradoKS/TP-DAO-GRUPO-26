import tkinter as tk
from tkinter import ttk
from Backend.DAO.PacienteDAO import PacienteDAO

class ConsultaPacientesScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Consulta de Pacientes")
        self.geometry("1200x600")
        self.configure(bg="#333333")

        self.paciente_dao = PacienteDAO()

        self.create_widgets()
        self.cargar_pacientes()

    def create_widgets(self):
        main_frame = tk.Frame(self, bg="#333333")
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        search_frame = tk.Frame(main_frame, bg="#333333")
        search_frame.pack(fill="x", pady=(0, 10), anchor="w")

        filter_fields_frame = tk.Frame(search_frame, bg="#333333")
        filter_fields_frame.pack(side="left")

        tk.Label(filter_fields_frame, text="Buscar por apellido:", bg="#333333", fg="white").grid(row=0, column=0, sticky="e", pady=2, padx=5)
        self.apellido_entry = ttk.Entry(filter_fields_frame, width=30)
        self.apellido_entry.grid(row=0, column=1, sticky="w", pady=2)

        tk.Label(filter_fields_frame, text="Buscar por DNI:", bg="#333333", fg="white").grid(row=1, column=0, sticky="e", pady=2, padx=5)
        self.dni_entry = ttk.Entry(filter_fields_frame, width=30)
        self.dni_entry.grid(row=1, column=1, sticky="w", pady=2)

        button_frame = tk.Frame(search_frame, bg="#333333")
        button_frame.pack(side="left", padx=20, anchor="center")

        search_button = ttk.Button(button_frame, text="Buscar", command=self.buscar_pacientes, width=20)
        search_button.pack()
        
        tree_container = tk.Frame(main_frame, bg="#333333")
        tree_container.pack(expand=True, fill="both")

        style = ttk.Style()
        style.configure("Treeview", background="#DDDDDD", foreground="black", fieldbackground="#DDDDDD")
        style.configure("Treeview.Heading", background="#CCCCCC", foreground="black")

        columns = ("ID", "Usuario", "Nombre", "Apellido", "Tipo DNI", "DNI", "Fec. Nac.", "Obra Social", "Barrio", "Calle", "N°", "Email", "Teléfono")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80)

        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("N°", width=50, anchor="center")
        self.tree.column("Nombre", width=120)
        self.tree.column("Apellido", width=120)
        self.tree.column("Email", width=150)

        self.tree.pack(side="left", expand=True, fill="both")
        
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def cargar_pacientes(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        pacientes = self.paciente_dao.obtener_pacientes_con_detalles()
        for paciente in pacientes:
            self.tree.insert("", "end", values=paciente)

    def buscar_pacientes(self):
        apellido = self.apellido_entry.get()
        dni = self.dni_entry.get()

        for i in self.tree.get_children():
            self.tree.delete(i)

        pacientes = self.paciente_dao.buscar_pacientes(apellido, dni)
        for paciente in pacientes:
            self.tree.insert("", "end", values=paciente)
