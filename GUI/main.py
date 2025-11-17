import tkinter as tk
from tkinter import messagebox
from .panel_pacientes import PanelPacientes
from .panel_medicos import PanelMedicos
from .panel_especialidades import PanelEspecialidades
from .abm_turnos import ABMTurnos
from .consulta_historial import ConsultaHistorial
from .abm_consultorios import GestionConsultorios
from .abm_obras_sociales import GestionObrasSociales
from .panel_reportes import PanelReportes
from .panel_recetas import PanelRecetas # Importar PanelRecetas

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
        
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_columnconfigure(2, weight=1)
        
        # Fila para el rol del usuario
        # Usamos un solo Label para que el texto esté junto y se vea correctamente
        rol_text = f"Su rol en el sistema es: {self.rol.upper()}"
        tk.Label(main_frame, text=rol_text, font=("Arial", 12, "bold"), bg="#333333", fg="white").grid(row=0, column=0, columnspan=3, pady=(0, 5), sticky="w")
        
        # Filas espaciadoras para empujar el contenido
        main_frame.grid_rowconfigure(1, weight=1) # Espacio superior
        main_frame.grid_rowconfigure(5, weight=2) # Espacio grande sobre el botón Salir
        main_frame.grid_rowconfigure(7, weight=1) # Espacio inferior

        button_properties = {
            "font": ("Arial", 14),
            "bg": "#CCCCCC",
            "fg": "#000000",
            "relief": "flat",
            "width": 25,
            "pady": 15
        }

        # --- Fila 1 (administración) ---
        btn_pacientes = self.create_button(main_frame, "Gestionar Pacientes", self.open_panel_pacientes, button_properties)
        btn_medicos = self.create_button(main_frame, "Gestionar Médicos", self.open_panel_medicos, button_properties)
        btn_especialidades = self.create_button(main_frame, "Gestionar Especialidades", self.open_panel_especialidades, button_properties)

        # --- Fila 2 (otros) ---
        btn_consultorios = self.create_button(main_frame, "Gestionar Consultorios", self.open_gestion_consultorios, button_properties)
        btn_turnos = self.create_button(main_frame, "Gestionar Turnos", self.open_abm_turnos, button_properties)
        btn_obras_sociales = self.create_button(main_frame, "Gestionar Obras Sociales", self.open_gestion_obras, button_properties)

        # Mostrar botones según rol
        if self.rol == "Administrador":
            # Admin: vea todo
            btn_pacientes.grid(row=2, column=0, padx=10, pady=20)
            btn_medicos.grid(row=2, column=1, padx=10, pady=20)
            btn_especialidades.grid(row=2, column=2, padx=10, pady=20)

            btn_consultorios.grid(row=3, column=0, padx=10, pady=20)
            btn_turnos.grid(row=3, column=1, padx=10, pady=20)
            btn_obras_sociales.grid(row=3, column=2, padx=10, pady=20)
        elif self.rol == "Medico":
            # Médicos: crear un frame centrado y colocar allí un botón específico
            center_frame = tk.Frame(main_frame, bg="#333333")
            center_frame.grid(row=2, column=0, columnspan=3)
            centered_btn = self.create_button(center_frame, "Gestionar Turnos", self.open_abm_turnos, button_properties)
            centered_btn.pack(pady=10, padx=200)
        else:
            # Paciente u otros: centrar Turnos también
            center_frame = tk.Frame(main_frame, bg="#333333")
            center_frame.grid(row=2, column=0, columnspan=3)
            centered_btn = self.create_button(center_frame, "Gestionar Turnos", self.open_abm_turnos, button_properties)
            centered_btn.pack(pady=10, padx=200)

        # --- Fila 3 (ahora en la fila 4 de la grilla) ---
        frame_fila_3 = tk.Frame(main_frame, bg="#333333")
        frame_fila_3.grid(row=4, column=0, columnspan=3, pady=20)

        btn_historial = self.create_button(frame_fila_3, "Consultar Historial Clínico", self.open_consulta_historial, button_properties)
        btn_historial.pack(side="left", padx=10)
        # Reportes solo para administradores
        if self.rol == "Administrador":
            btn_reportes = self.create_button(frame_fila_3, "Ver Reportes", self.open_reportes, button_properties)
            btn_reportes.pack(side="left", padx=10)

        # Para pacientes, agregar acceso rápido a 'Mis Recetas'
        if self.rol == "Paciente":
            btn_recetas = self.create_button(frame_fila_3, "Mis Recetas", lambda: PanelRecetas(self, self.usuario).grab_set(), button_properties)
            btn_recetas.pack(side="left", padx=10)
        
        # --- Fila 6 (Cerrar sesión / Salir, separado por la fila 5) ---
        btn_cerrar_sesion = self.create_button(main_frame, "Cerrar sesión", self.cerrar_sesion, button_properties)
        btn_cerrar_sesion.grid(row=6, column=0, padx=10, pady=10)

        btn_salir = self.create_button(main_frame, "Salir", self.destroy, button_properties)
        btn_salir.grid(row=6, column=1, padx=10, pady=10)

        # Espacio opcional a la derecha para balance visual
        placeholder = tk.Frame(main_frame, bg="#333333")
        placeholder.grid(row=6, column=2)

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
        if self.rol != "Administrador":
            messagebox.showerror("Permiso denegado", "Solo administradores pueden gestionar pacientes.")
            return
        PanelPacientes(self).grab_set()

    def open_panel_medicos(self):
        if self.rol != "Administrador":
            messagebox.showerror("Permiso denegado", "Solo administradores pueden gestionar médicos.")
            return
        PanelMedicos(self).grab_set()

    def open_panel_especialidades(self):
        if self.rol != "Administrador":
            messagebox.showerror("Permiso denegado", "Solo administradores pueden gestionar especialidades.")
            return
        PanelEspecialidades(self).grab_set()

    def open_abm_turnos(self):
        ABMTurnos(self, self.rol, self.usuario).grab_set()

    def open_reportes(self):
        if self.rol != "Administrador":
            messagebox.showerror("Permiso denegado", "Solo administradores pueden ver reportes.")
            return
        PanelReportes(self).grab_set()

    def open_consulta_historial(self):
        ConsultaHistorial(self, self.usuario, self.rol).grab_set()

    def open_gestion_consultorios(self):
        if self.rol != "Administrador":
            messagebox.showerror("Permiso denegado", "Solo administradores pueden gestionar consultorios.")
            return
        GestionConsultorios(self, self.usuario).grab_set()

    def open_gestion_obras(self):
        if self.rol != "Administrador":
            messagebox.showerror("Permiso denegado", "Solo administradores pueden gestionar obras sociales.")
            return
        GestionObrasSociales(self, self.usuario).grab_set()

    def cerrar_sesion(self):
        """Cierra la sesión actual y vuelve a la ventana de login sin salir del programa."""
        if not messagebox.askyesno("Cerrar sesión", "¿Desea cerrar la sesión y volver a la pantalla de login?"):
            return
        try:
            # Destruir la ventana actual del menú
            self.destroy()
            # Importar LoginWindow localmente para evitar import circular
            from GUI.login import LoginWindow
            # Abrir la ventana de login (nueva instancia)
            LoginWindow().mainloop()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cerrar la sesión: {e}")
