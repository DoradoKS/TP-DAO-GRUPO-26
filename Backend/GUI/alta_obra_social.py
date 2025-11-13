import tkinter as tk
from tkinter import ttk, messagebox
from Backend.DAO.ObraSocialDAO import ObraSocialDAO
from Backend.Model.ObraSocial import ObraSocial

class AltaObraSocial(tk.Toplevel):
    def __init__(self, parent, usuario="admin"):
        super().__init__(parent)
        self.title("Alta de Nueva Obra Social")
        self.geometry("400x150")
        self.configure(bg="#333333")
        self.usuario = usuario
        self.parent = parent

        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self, bg="#333333")
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        tk.Label(main_frame, text="Nombre:", font=("Arial", 12), bg="#333333", fg="white").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.nombre_entry = ttk.Entry(main_frame, width=30)
        self.nombre_entry.grid(row=0, column=1, padx=10, pady=10)

        guardar_button = ttk.Button(main_frame, text="Registrar", command=self.guardar_obra_social)
        guardar_button.grid(row=1, column=0, columnspan=2, pady=20)

    def guardar_obra_social(self):
        nombre = self.nombre_entry.get().strip()
        if not nombre:
            messagebox.showerror("Error de Validación", "El nombre no puede estar vacío.")
            return

        obra_social = ObraSocial(nombre=nombre)
        dao = ObraSocialDAO()
        
        # Asumo que el método en el DAO se llama `crear_obra_social`
        # y que devuelve (id, mensaje) o (None, mensaje_error)
        id_creado, mensaje = dao.cargar_obra_social(obra_social, self.usuario)

        if id_creado:
            messagebox.showinfo("Éxito", "Obra Social creada exitosamente.")
            # Actualizar la lista en la ventana padre
            if hasattr(self.parent, 'cargar_obras_sociales'):
                self.parent.cargar_obras_sociales()
            self.destroy()
        else:
            messagebox.showerror("Error", mensaje)
