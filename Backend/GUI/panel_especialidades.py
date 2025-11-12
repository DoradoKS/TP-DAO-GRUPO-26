import tkinter as tk
from .abm_especialidades import GestionEspecialidades # Corregido
from .alta_especialidad import AltaEspecialidad

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

        border_alta = tk.Frame(button_container, bg="#FFD700", bd=2)
        border_alta.pack(pady=10)
        btn_alta = tk.Button(border_alta, text="Dar de Alta Especialidad", command=self.abrir_alta, **button_properties)
        btn_alta.pack()

        border_gestion = tk.Frame(button_container, bg="#FFD700", bd=2)
        border_gestion.pack(pady=10)
        btn_gestion = tk.Button(border_gestion, text="Modificar / Dar de Baja", command=self.abrir_gestion, **button_properties)
        btn_gestion.pack()

    def abrir_alta(self):
        alta_window = AltaEspecialidad(self)
        alta_window.grab_set()

    def abrir_gestion(self):
        # Corregido para usar la nueva clase
        gestion_window = GestionEspecialidades(self)
        gestion_window.grab_set()
