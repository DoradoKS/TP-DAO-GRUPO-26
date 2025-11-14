import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from Backend.BDD.Conexion import get_conexion
from Backend.DAO.MedicoDAO import MedicoDAO
from Backend.DAO.EspecialidadDAO import EspecialidadDAO
from Backend.Model.Medico import Medico
from Backend.DAO.UsuarioDAO import UsuarioDAO
from Backend.GUI.panel_horarios import PanelHorarios # Importar PanelHorarios

class AltaMedico(tk.Toplevel):
    def __init__(self, parent, usuario="admin"):
        super().__init__(parent)
        self.title("Alta de Nuevo Médico")
        self.geometry("500x500")
        self.configure(bg="#333333")
        self.usuario = usuario
        self.parent = parent # Guardar referencia al parent para grab_set

        self.especialidades = []
        self.tipos_dni = []
        self.entries = {}

        self.create_widgets()
        self.cargar_comboboxes()

    def create_widgets(self):
        main_frame = tk.Frame(self, bg="#333333")
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        fields = [
            ("Usuario:", "Entry"), ("Contraseña:", "Entry"), ("Nombre:", "Entry"), 
            ("Apellido:", "Entry"), ("DNI:", "Entry"), ("Tipo DNI:", "Combobox"), 
            ("Matrícula:", "Entry"), ("Teléfono:", "Entry"), ("Email:", "Entry"),
            ("Especialidad:", "Combobox")
        ]

        for i, (label_text, widget_type) in enumerate(fields):
            label = tk.Label(main_frame, text=label_text, font=("Arial", 12), bg="#333333", fg="white")
            label.grid(row=i, column=0, padx=10, pady=5, sticky="e")
            
            if widget_type == "Entry":
                show_char = "*" if label_text == "Contraseña:" else None
                entry = ttk.Entry(main_frame, width=40, show=show_char)
                entry.grid(row=i, column=1, padx=10, pady=5)
                self.entries[label_text] = entry
            elif widget_type == "Combobox":
                if label_text == "Tipo DNI:":
                    self.tipo_dni_combo = ttk.Combobox(main_frame, width=38, state="readonly", values=["DNI", "Pasaporte", "Libreta de Enrolamiento", "Libreta Cívica"])
                    self.tipo_dni_combo.grid(row=i, column=1, padx=10, pady=5)
                elif label_text == "Especialidad:":
                    self.especialidad_combo = ttk.Combobox(main_frame, width=38, state="readonly")
                    self.especialidad_combo.grid(row=i, column=1, padx=10, pady=5)

        guardar_button = ttk.Button(main_frame, text="Guardar", command=self.guardar_medico)
        guardar_button.grid(row=len(fields), column=0, columnspan=2, pady=20)

    def cargar_comboboxes(self):
        # Cargar Especialidades
        self.especialidades = EspecialidadDAO().obtener_todas_las_especialidades()
        self.especialidad_combo["values"] = [e.nombre for e in self.especialidades]
        if self.especialidades:
            self.especialidad_combo.current(0)
        
        # Cargar Tipos de DNI
        self.tipo_dni_combo.current(0)


    def guardar_medico(self):
        usuario = self.entries["Usuario:"].get().strip()
        contraseña = self.entries["Contraseña:"].get().strip()
        nombre = self.entries["Nombre:"].get().strip()
        apellido = self.entries["Apellido:"].get().strip()
        dni = self.entries["DNI:"].get().strip()
        tipo_dni = self.tipo_dni_combo.get()
        matricula = self.entries["Matrícula:"].get().strip()
        telefono = self.entries["Teléfono:"].get().strip()
        email = self.entries["Email:"].get().strip()
        
        selected_especialidad_nombre = self.especialidad_combo.get()
        id_especialidad = next((e.id_especialidad for e in self.especialidades if e.nombre == selected_especialidad_nombre), None)

        if not all([usuario, contraseña, nombre, apellido, dni, tipo_dni, matricula, telefono, email, id_especialidad]):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        usuario_dao = UsuarioDAO()
        creado, msg_usuario = usuario_dao.crear_usuario(usuario, contraseña, "Medico")
        if not creado:
            messagebox.showerror("Error al crear usuario", msg_usuario)
            return

        medico = Medico(
            usuario=usuario, nombre=nombre, apellido=apellido, matricula=matricula,
            tipo_dni=tipo_dni, dni=dni, email=email, telefono=telefono,
            id_especialidad=id_especialidad, calle="Default", numero_calle=123
        )

        id_creado, mensaje = MedicoDAO().crear_medico(medico, self.usuario)
        if id_creado:
            messagebox.showinfo("Éxito", f"{mensaje} (ID: {id_creado})")
            
            # Preguntar al usuario si desea configurar horarios
            if messagebox.askyesno("Configurar Horarios", 
                                   f"Médico {nombre} {apellido} creado exitosamente.\n¿Desea configurar sus horarios laborales ahora?", 
                                   parent=self):
                # Abrir PanelHorarios para el médico recién creado
                panel_horarios = PanelHorarios(self.parent, id_creado, f"{nombre} {apellido}")
                panel_horarios.grab_set()
            
            self.destroy() # Cerrar la ventana de alta
        else:
            messagebox.showerror("Error al crear médico", mensaje)
