import tkinter as tk
from .panel_pacientes import PanelPacientes
from .panel_medicos import PanelMedicos
from .panel_especialidades import PanelEspecialidades
from .abm_turnos import ABMTurnos
from .reportes import Reportes
from .registro_historial import RegistroHistorial
from .consulta_historial import ConsultaHistorial
from .abm_consultorios import GestionConsultorios
from .abm_obras_sociales import GestionObrasSociales

class MainMenu(tk.Tk):
    def __init__(self, rol, usuario):
        super().__init__()
        self.title("Sistema de Turnos Médicos - Menú Principal")
        
        window_width = 800
        window_height = 600
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        
        pos_x = center_x - 50
        pos_y = center_y - 50
        
        self.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")

        self.configure(bg="#333333")

        self.rol = rol
        self.usuario = usuario
        
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

        botones = {
            "Gestionar Pacientes": (self.open_panel_pacientes, ["Administrador"]),
            "Gestionar Médicos": (self.open_panel_medicos, ["Administrador"]),
            "Gestionar Especialidades": (self.open_panel_especialidades, ["Administrador"]),
            "Gestionar Consultorios": (self.open_gestion_consultorios, ["Administrador"]),
            "Gestionar Obras Sociales": (self.open_gestion_obras, ["Administrador"]),
            "Gestionar Turnos": (self.open_abm_turnos, ["Administrador", "Medico", "Paciente"]),
            "Registrar Historial Clínico": (self.open_registro_historial, ["Medico"]),
            "Consultar Historial Clínico": (self.open_consulta_historial, ["Administrador", "Medico", "Paciente"]),
            "Ver Reportes": (self.open_reportes, ["Administrador", "Medico"]),
        }

        for texto_boton, (comando, roles_permitidos) in botones.items():
            if self.rol in roles_permitidos:
                border_frame = tk.Frame(button_container, bg="#FFD700", bd=2)
                border_frame.pack(pady=10)
                
                btn = tk.Button(border_frame, text=texto_boton, command=comando, **button_properties)
                btn.pack()
                btn.bind("<Enter>", self.on_enter)
                btn.bind("<Leave>", self.on_leave)


        border_frame_salir = tk.Frame(button_container, bg="#FFD700", bd=2)
        border_frame_salir.pack(pady=20)
        salir_btn = tk.Button(border_frame_salir, text="Salir", command=self.destroy, **button_properties)
        salir_btn.pack()
        salir_btn.bind("<Enter>", self.on_enter)
        salir_btn.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        e.widget['background'] = '#AAAAAA'

    def on_leave(self, e):
        e.widget['background'] = '#CCCCCC'

    def open_panel_pacientes(self):
        panel_pacientes_window = PanelPacientes(self)
        panel_pacientes_window.grab_set()

    def open_panel_medicos(self):
        panel_medicos_window = PanelMedicos(self)
        panel_medicos_window.grab_set()

    def open_panel_especialidades(self):
        panel_especialidades_window = PanelEspecialidades(self)
        panel_especialidades_window.grab_set()

    def open_abm_turnos(self):
        abm_turnos_window = ABMTurnos(self, self.rol, self.usuario)
        abm_turnos_window.grab_set()

    def open_reportes(self):
        reportes_window = Reportes(self)
        reportes_window.grab_set()

    def open_registro_historial(self):
        registro_window = RegistroHistorial(self, self.usuario, self.rol)
        registro_window.grab_set()

    def open_consulta_historial(self):
        consulta_window = ConsultaHistorial(self, self.usuario, self.rol)
        consulta_window.grab_set()

    def open_gestion_consultorios(self):
        win = GestionConsultorios(self, self.usuario)
        win.grab_set()

    def open_gestion_obras(self):
        win = GestionObrasSociales(self, self.usuario)
        win.grab_set()
