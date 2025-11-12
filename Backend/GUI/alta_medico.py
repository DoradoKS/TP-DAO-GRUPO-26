import tkinter as tk
from tkinter import ttk, messagebox
from Backend.DAO.MedicoDAO import MedicoDAO
from Backend.DAO.EspecialidadDAO import EspecialidadDAO
from Backend.Model.Medico import Medico
from Backend.DAO.UsuarioDAO import UsuarioDAO

class AltaMedico(tk.Toplevel):
    def __init__(self, parent, usuario="admin"):
        super().__init__(parent)
        self.title("Alta de Nuevo Médico")
        self.geometry("500x450")
        self.usuario = usuario

        self.especialidades = []
        self.entries = {}

        self.create_widgets()
        self.cargar_especialidades()

    def create_widgets(self):
        form_frame = ttk.Frame(self)
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)

        labels = ["Usuario:", "Contraseña:", "Nombre:", "Apellido:", "DNI:", "Tipo DNI:", "Matrícula:", "Teléfono:", "Email:"]
        for i, label_text in enumerate(labels):
            ttk.Label(form_frame, text=label_text, font=("Arial", 12)).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            show_char = "*" if label_text == "Contraseña:" else None  # oculta contraseña
            entry = ttk.Entry(form_frame, width=40, show=show_char)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries[label_text] = entry


        ttk.Label(form_frame, text="Especialidad:", font=("Arial", 12)).grid(row=len(labels), column=0, padx=10, pady=5, sticky="e")
        self.especialidad_combo = ttk.Combobox(form_frame, width=38)
        self.especialidad_combo.grid(row=len(labels), column=1, padx=10, pady=5)

        guardar_button = ttk.Button(form_frame, text="Guardar", command=self.guardar_medico)
        guardar_button.grid(row=len(labels) + 1, column=0, columnspan=2, pady=20)

    def cargar_especialidades(self):
        self.especialidades = EspecialidadDAO().obtener_todas_las_especialidades()
        self.especialidad_combo["values"] = [e.nombre for e in self.especialidades]

    def guardar_medico(self):
        usuario = self.entries["Usuario:"].get().strip()
        contraseña = self.entries["Contraseña:"].get().strip()
        nombre = self.entries["Nombre:"].get().strip()
        apellido = self.entries["Apellido:"].get().strip()
        tipo_dni = self.entries["Tipo DNI:"].get().strip()
        dni = self.entries["DNI:"].get().strip()
        matricula = self.entries["Matrícula:"].get().strip()
        telefono = self.entries["Teléfono:"].get().strip()
        email = self.entries["Email:"].get().strip()

        selected_especialidad_nombre = self.especialidad_combo.get()
        id_especialidad = next((e.id_especialidad for e in self.especialidades if e.nombre == selected_especialidad_nombre), None)

        if not all([usuario, contraseña, nombre, apellido, dni, tipo_dni, matricula, id_especialidad]):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        # Paso 1: crear usuario
        usuario_dao = UsuarioDAO()
        creado, msg_usuario = usuario_dao.crear_usuario(usuario, contraseña, "Medico")
        if not creado:
            messagebox.showerror("Error", msg_usuario)
            return

        # Paso 2: crear médico vinculado al usuario
        medico = Medico(
            usuario=usuario,
            nombre=nombre,
            apellido=apellido,
            matricula=matricula,
            tipo_dni=tipo_dni,
            dni=dni,
            email=email,
            telefono=telefono,
            id_especialidad=id_especialidad,
            calle="Default",
            numero_calle=123
        )

        id_creado, mensaje = MedicoDAO().crear_medico(medico, self.usuario)
        if id_creado:
            messagebox.showinfo("Éxito", f"{mensaje} (ID: {id_creado})")
            self.destroy()
        else:
            messagebox.showerror("Error", mensaje)
