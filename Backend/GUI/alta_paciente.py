import tkinter as tk
from tkinter import ttk, messagebox
from Backend.DAO.PacienteDAO import PacienteDAO
from Backend.Model.Paciente import Paciente

class AltaPaciente(tk.Toplevel):
    def __init__(self, parent, usuario="admin"):
        super().__init__(parent)
        self.title("Alta de Nuevo Paciente")
        self.geometry("500x400")
        self.usuario = usuario

        self.create_widgets()

    def create_widgets(self):
        form_frame = ttk.Frame(self)
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)

        labels = ["Nombre:", "Apellido:", "DNI:", "Tipo DNI:", "Fecha Nacimiento (YYYY-MM-DD):", "Teléfono:", "Email:"]
        self.entries = {}

        for i, label_text in enumerate(labels):
            ttk.Label(form_frame, text=label_text, font=("Arial", 12)).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = ttk.Entry(form_frame, width=40)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries[label_text] = entry

        guardar_button = ttk.Button(form_frame, text="Guardar", command=self.guardar_paciente)
        guardar_button.grid(row=len(labels), column=0, columnspan=2, pady=20)

    def guardar_paciente(self):
        nombre = self.entries["Nombre:"].get().strip()
        apellido = self.entries["Apellido:"].get().strip()
        
        paciente = Paciente(
            id_barrio=1, # Valor por defecto
            usuario=f"{nombre.lower()}.{apellido.lower()}",
            nombre=nombre,
            apellido=apellido,
            fecha_nacimiento=self.entries["Fecha Nacimiento (YYYY-MM-DD):"].get().strip(),
            tipo_dni=self.entries["Tipo DNI:"].get().strip(),
            dni=self.entries["DNI:"].get().strip(),
            email=self.entries["Email:"].get().strip(),
            telefono=self.entries["Teléfono:"].get().strip(),
            id_obra_social=1, # Valor por defecto
            calle="Default",
            numero_calle=123
        )
        
        paciente_dao = PacienteDAO()
        id_creado, mensaje = paciente_dao.crear_paciente(paciente, self.usuario)

        if id_creado:
            messagebox.showinfo("Éxito", mensaje)
            self.destroy()
        else:
            messagebox.showerror("Error", mensaje)
