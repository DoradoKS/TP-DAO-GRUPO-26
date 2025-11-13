import tkinter as tk
from tkinter import messagebox
from .panel_pacientes import PanelPacientes
from .panel_medicos import PanelMedicos
from .panel_especialidades import PanelEspecialidades
from .abm_turnos import ABMTurnos
from .reportes import Reportes
from .consulta_historial import ConsultaHistorial
from .abm_consultorios import GestionConsultorios
from .abm_obras_sociales import GestionObrasSociales

class MainMenu(tk.Tk):
    def __init__(self, rol, usuario):
        super().__init__()
        self.title("Sistema de Turnos Médicos - Menú Principal")
        
        self.geometry("900x600")
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        center_x = int(screen_width / 2 - 900 / 2)
        center_y = int(screen_height / 2 - 600 / 2)
        
        self.geometry(f"900x600+{center_x}+{center_y}")

        self.configure(bg="#333333")

        self.rol = rol
        self.usuario = usuario
        
        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self, bg="#333333")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Configurar la grilla para que las columnas se centren
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_columnconfigure(2, weight=1)
        
        # Filas espaciadoras para empujar el contenido
        main_frame.grid_rowconfigure(0, weight=1) # Espacio superior
        main_frame.grid_rowconfigure(4, weight=2) # Espacio grande sobre el botón Salir
        main_frame.grid_rowconfigure(6, weight=1) # Espacio inferior

        button_properties = {
            "font": ("Arial", 14),
            "bg": "#CCCCCC",
            "fg": "#000000",
            "relief": "flat",
            "width": 25,
            "pady": 15
        }

        # --- Fila 1 (ahora en la fila 1 de la grilla) ---
        btn_pacientes = self.create_button(main_frame, "Gestionar Pacientes", self.open_panel_pacientes, button_properties)
        btn_pacientes.grid(row=1, column=0, padx=10, pady=20)

        btn_medicos = self.create_button(main_frame, "Gestionar Médicos", self.open_panel_medicos, button_properties)
        btn_medicos.grid(row=1, column=1, padx=10, pady=20)

        btn_especialidades = self.create_button(main_frame, "Gestionar Especialidades", self.open_panel_especialidades, button_properties)
        btn_especialidades.grid(row=1, column=2, padx=10, pady=20)

        # --- Fila 2 (ahora en la fila 2 de la grilla) ---
        btn_consultorios = self.create_button(main_frame, "Gestionar Consultorios", self.open_gestion_consultorios, button_properties)
        btn_consultorios.grid(row=2, column=0, padx=10, pady=20)

        btn_turnos = self.create_button(main_frame, "Gestionar Turnos", self.open_abm_turnos, button_properties)
        btn_turnos.grid(row=2, column=1, padx=10, pady=20)

        btn_obras_sociales = self.create_button(main_frame, "Gestionar Obras Sociales", self.open_gestion_obras, button_properties)
        btn_obras_sociales.grid(row=2, column=2, padx=10, pady=20)

        # --- Fila 3 (ahora en la fila 3 de la grilla) ---
        frame_fila_3 = tk.Frame(main_frame, bg="#333333")
        frame_fila_3.grid(row=3, column=0, columnspan=3, pady=20)

        btn_historial = self.create_button(frame_fila_3, "Consultar Historial Clínico", self.open_consulta_historial, button_properties)
        btn_historial.pack(side="left", padx=10)

        btn_reportes = self.create_button(frame_fila_3, "Ver Reportes", self.open_reportes, button_properties)
        btn_reportes.pack(side="left", padx=10)
        
        # --- Fila 5 (Salir, separado por la fila 4) ---
        btn_salir = self.create_button(main_frame, "Salir", self.destroy, button_properties)
        btn_salir.grid(row=5, column=1, padx=10, pady=10)

    def create_button(self, parent, text, command, properties):
        border_frame = tk.Frame(parent, bg="#FFD700", bd=2)
        btn = tk.Button(border_frame, text=text, command=command, **properties)
        btn.pack()
        btn.bind("<Enter>", self.on_enter)
        btn.bind("<Leave>", self.on_leave)
        return border_frame

    def on_enter(self, e):
        e.widget['background'] = '#AAAAAA'

    def on_leave(self, e):
        e.widget['background'] = '#CCCCCC'

    def open_panel_pacientes(self):
        PanelPacientes(self).grab_set()

    def open_panel_medicos(self):
        PanelMedicos(self).grab_set()

    def open_panel_especialidades(self):
        PanelEspecialidades(self).grab_set()

    def open_abm_turnos(self):
        ABMTurnos(self, self.rol, self.usuario).grab_set()

    def open_reportes(self):
        Reportes(self).grab_set()

    def open_consulta_historial(self):
        ConsultaHistorial(self, self.usuario, self.rol).grab_set()

    def open_gestion_consultorios(self):
        GestionConsultorios(self, self.usuario).grab_set()

    def open_gestion_obras(self):
        GestionObrasSociales(self, self.usuario).grab_set()
