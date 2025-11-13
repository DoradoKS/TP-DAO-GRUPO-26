import tkinter as tk
from .abm_especialidades import GestionEspecialidades
from .alta_especialidad import AltaEspecialidad
from .consulta_especialidades import ConsultaEspecialidades

class PanelEspecialidades(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Panel de Especialidades")
        self.geometry("600x400")
        self.configure(bg="#333333")

        self.parent = parent

        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self, bg="#333333")
        main_frame.pack(expand=True, fill="both")
        
        button_container = tk.Frame(main_frame, bg="#333333")
        button_container.pack(expand=True)

        button_properties = {
            "font": ("Arial", 14),
            "bg": "#CCCCCC",
            "fg": "#000000",
            "relief": "flat",
            "width": 25,
            "pady": 15
        }

        buttons_to_create = [
            ("Dar de Alta Especialidad", self.abrir_alta),
            ("Modificar / Dar de Baja", self.abrir_gestion),
            ("Consultar Especialidades", self.abrir_consulta)
        ]

        for text, command in buttons_to_create:
            border_frame = tk.Frame(button_container, bg="#FFD700", bd=2)
            border_frame.pack(pady=10)
            btn = tk.Button(border_frame, text=text, command=command, **button_properties)
            btn.pack()
            btn.bind("<Enter>", self.on_enter)
            btn.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        e.widget['background'] = '#AAAAAA'

    def on_leave(self, e):
        e.widget['background'] = '#CCCCCC'

    def abrir_alta(self):
        alta_window = AltaEspecialidad(self)
        alta_window.grab_set()

    def abrir_gestion(self):
        gestion_window = GestionEspecialidades(self)
        gestion_window.grab_set()

    def abrir_consulta(self):
        consulta_window = ConsultaEspecialidades(self)
        consulta_window.grab_set()
