import tkinter as tk
from tkinter import ttk, messagebox
from Backend.DAO.EspecialidadDAO import EspecialidadDAO
from Backend.Model.Especialidad import Especialidad
from Backend.Validaciones.validaciones import Validaciones

class AltaEspecialidad(tk.Toplevel):
    def __init__(self, parent, usuario="admin"):
        super().__init__(parent)
        self.title("Alta de Nueva Especialidad")
        self.geometry("500x250")
        self.usuario = usuario

        self.create_widgets()

    def create_widgets(self):
        form_frame = ttk.Frame(self)
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)

        ttk.Label(form_frame, text="Nombre:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.nombre_entry = ttk.Entry(form_frame, width=40)
        self.nombre_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(form_frame, text="Descripción:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.descripcion_entry = ttk.Entry(form_frame, width=40)
        self.descripcion_entry.grid(row=1, column=1, padx=10, pady=10)

        guardar_button = ttk.Button(form_frame, text="Guardar", command=self.guardar_especialidad)
        guardar_button.grid(row=2, column=0, columnspan=2, pady=20)

    def guardar_especialidad(self):
        nombre = self.nombre_entry.get().strip()
        descripcion = self.descripcion_entry.get().strip()

        # Validación de campo vacío
        es_valido, errores = Validaciones.validar_campos_requeridos({"nombre": nombre}, ["nombre"])
        if not es_valido:
            messagebox.showerror("Error de Validación", errores[0])
            return

        especialidad = Especialidad(nombre=nombre, descripcion=descripcion)
        especialidad_dao = EspecialidadDAO()
        
        id_creado, mensaje = especialidad_dao.crear_especialidad(especialidad, self.usuario)

        if id_creado:
            messagebox.showinfo("Éxito", mensaje)
            self.destroy()  # Cerrar la ventana de alta
        else:
            messagebox.showerror("Error", mensaje)
