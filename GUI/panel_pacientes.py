import tkinter as tk
from .alta_paciente import AltaPaciente
from .abm_pacientes import GestionPacientes
from .consulta_pacientes import ConsultaPacientesScreen

class PanelPacientes(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Panel de Pacientes")
        self.geometry("600x400")
        self.configure(bg="#333333")
        self.parent = parent

        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self, bg="#333333")
        main_frame.pack(expand=True, fill="both")
        
        button_container = tk.Frame(main_frame, bg="#333333")
        button_container.pack(expand=True, pady=20)

        button_properties = {
            "font": ("Arial", 14), "bg": "#CCCCCC", "fg": "#000000",
            "relief": "flat", "width": 25, "pady": 15
        }

        buttons_to_create = [
            ("Dar de Alta Paciente", self.abrir_alta),
            ("Modificar / Dar de Baja", self.abrir_gestion),
            ("Consultar Pacientes", self.abrir_consulta)
        ]

        for text, command in buttons_to_create:
            border_frame = tk.Frame(button_container, bg="#FFD700", bd=2)
            border_frame.pack(pady=8, padx=60, fill='x')
            btn = tk.Button(border_frame, text=text, command=command, **button_properties)
            btn.pack(fill='x', padx=8, pady=4)
            btn.bind("<Enter>", self.on_enter)
            btn.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        e.widget['background'] = '#AAAAAA'

    def on_leave(self, e):
        e.widget['background'] = '#CCCCCC'

    def abrir_alta(self):
        alta_window = AltaPaciente(self)
        alta_window.grab_set()

    def abrir_gestion(self):
        gestion_window = GestionPacientes(self)
        gestion_window.grab_set()

    def abrir_consulta(self):
        consulta_window = ConsultaPacientesScreen(self)
        consulta_window.grab_set()
