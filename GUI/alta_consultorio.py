import tkinter as tk
from tkinter import ttk, messagebox
from Backend.DAO.ConsultorioDAO import ConsultorioDAO
from Backend.Model.Consultorio import Consultorio

class AltaConsultorio(tk.Toplevel):
    def __init__(self, parent, usuario="admin"):
        super().__init__(parent)
        self.title("Alta de Nuevo Consultorio")
        self.geometry("400x150")
        self.configure(bg="#333333")
        self.usuario = usuario
        self.parent = parent

        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self, bg="#333333")
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        tk.Label(main_frame, text="Descripción:", font=("Arial", 12), bg="#333333", fg="white").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.descripcion_entry = ttk.Entry(main_frame, width=30)
        self.descripcion_entry.grid(row=0, column=1, padx=10, pady=10)

        guardar_button = ttk.Button(main_frame, text="Registrar", command=self.guardar_consultorio)
        guardar_button.grid(row=1, column=0, columnspan=2, pady=20)

    def guardar_consultorio(self):
        descripcion = self.descripcion_entry.get().strip()
        if not descripcion:
            messagebox.showerror("Error de Validación", "La descripción no puede estar vacía.")
            return

        consultorio = Consultorio(descripcion=descripcion)
        dao = ConsultorioDAO()
        
        id_creado, mensaje = dao.crear_consultorio(consultorio, self.usuario)

        if id_creado:
            messagebox.showinfo("Éxito", "Consultorio creado exitosamente.")
            if hasattr(self.parent, 'cargar_consultorios'):
                self.parent.cargar_consultorios()
            self.destroy()
        else:
            messagebox.showerror("Error", mensaje)
