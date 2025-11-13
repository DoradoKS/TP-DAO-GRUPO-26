import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from Backend.DAO.PacienteDAO import PacienteDAO
from Backend.DAO.UsuarioDAO import UsuarioDAO
from Backend.DAO.ObraSocialDAO import ObraSocialDAO
from Backend.DAO.BarrioDAO import BarrioDAO
from Backend.Model.Paciente import Paciente

class AltaPaciente(tk.Toplevel):
    def __init__(self, parent, usuario="admin"):
        super().__init__(parent)
        self.title("Alta de Nuevo Paciente")
        self.geometry("650x640")
        self.usuario = usuario
        self.obras_sociales = []
        self.barrios = []
        self.entries = {}
        self.create_widgets()
        self.cargar_comboboxes()

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(padx=20, pady=15, fill="both", expand=True)

        filas = [
            ("Usuario:", True), ("Contraseña:", True), ("Nombre:", True), ("Apellido:", True),
            ("Fecha Nacimiento (YYYY-MM-DD):", True), ("DNI:", True), ("Email:", True), ("Teléfono:", True),
            ("Calle:", True), ("Número:", True)
        ]
        row = 0
        for label_text, requerido in filas:
            ttk.Label(main_frame, text=label_text).grid(row=row, column=0, padx=8, pady=5, sticky="e")
            entry = ttk.Entry(main_frame, width=35, show="*" if label_text == "Contraseña:" else None)
            entry.grid(row=row, column=1, padx=8, pady=5, sticky="w")
            self.entries[label_text] = entry
            row += 1

        ttk.Label(main_frame, text="Tipo DNI:").grid(row=row, column=0, padx=8, pady=5, sticky="e")
        self.tipo_dni_combo = ttk.Combobox(main_frame, width=33, state="readonly", values=["DNI", "Pasaporte", "Libreta de Enrolamiento", "Libreta Cívica"])
        self.tipo_dni_combo.grid(row=row, column=1, padx=8, pady=5, sticky="w")
        row += 1

        ttk.Label(main_frame, text="Obra Social:").grid(row=row, column=0, padx=8, pady=5, sticky="e")
        self.obra_social_combo = ttk.Combobox(main_frame, width=33, state="readonly")
        self.obra_social_combo.grid(row=row, column=1, padx=8, pady=5, sticky="w")
        row += 1

        ttk.Label(main_frame, text="Barrio:").grid(row=row, column=0, padx=8, pady=5, sticky="e")
        self.barrio_entry = ttk.Entry(main_frame, width=35)
        self.barrio_entry.grid(row=row, column=1, padx=8, pady=5, sticky="w")
        row += 1

        guardar_button = ttk.Button(self, text="Registrar Paciente", command=self.guardar_paciente)
        guardar_button.pack(pady=10)

    def cargar_comboboxes(self):
        if self.tipo_dni_combo['values']:
            self.tipo_dni_combo.current(0)

        self.obras_sociales = ObraSocialDAO().obtener_obra_social()
        self.obra_social_combo['values'] = [o.nombre for o in self.obras_sociales]
        if self.obras_sociales:
            self.obra_social_combo.current(0)

        # Para barrio ahora se ingresa por teclado; no cargamos combobox
        self.barrios = []

    def guardar_paciente(self):
        usuario = self.entries["Usuario:"].get().strip()
        contrasena = self.entries["Contraseña:"].get().strip()
        nombre = self.entries["Nombre:"].get().strip()
        apellido = self.entries["Apellido:"].get().strip()
        fecha_nac = self.entries["Fecha Nacimiento (YYYY-MM-DD):"].get().strip()
        dni = self.entries["DNI:"].get().strip()
        email = self.entries["Email:"].get().strip()
        telefono = self.entries["Teléfono:"].get().strip()
        calle = self.entries["Calle:"].get().strip()
        numero_calle = self.entries["Número:"].get().strip()
        barrio_nombre = self.barrio_entry.get().strip()

        if not all([usuario, contrasena, nombre, apellido, fecha_nac, dni, email, telefono, calle, numero_calle]):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        try:
            datetime.strptime(fecha_nac, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Fecha de nacimiento inválida. Formato esperado YYYY-MM-DD.")
            return

        tipo_dni_nombre = self.tipo_dni_combo.get()
        obra_social_nombre = self.obra_social_combo.get()
        id_obra_social = next((o.id_obra_social for o in self.obras_sociales if o.nombre == obra_social_nombre), None)
        if not barrio_nombre:
            messagebox.showerror("Error", "Debe ingresar el barrio.")
            return
        barrio_dao = BarrioDAO()
        id_barrio = barrio_dao.obtener_o_crear_barrio(barrio_nombre)

        if not all([tipo_dni_nombre, id_obra_social, id_barrio]):
            messagebox.showerror("Error", "Debe seleccionar Tipo DNI, Obra Social y Barrio.")
            return

        usuario_dao = UsuarioDAO()
        ok_usuario, msg_usuario = usuario_dao.crear_usuario(usuario, contrasena, "Paciente")
        if not ok_usuario:
            messagebox.showerror("Error", msg_usuario)
            return

        try:
            numero_calle_int = int(numero_calle)
        except ValueError:
            messagebox.showerror("Error", "El número de calle debe ser un entero.")
            return

        paciente = Paciente(
            id_barrio=id_barrio,
            usuario=usuario,
            nombre=nombre,
            apellido=apellido,
            fecha_nacimiento=fecha_nac,
            tipo_dni=tipo_dni_nombre,
            dni=dni,
            email=email,
            telefono=telefono,
            id_obra_social=id_obra_social,
            calle=calle,
            numero_calle=numero_calle_int
        )

        paciente_dao = PacienteDAO()
        id_creado, mensaje = paciente_dao.crear_paciente(paciente, self.usuario)
        if id_creado:
            messagebox.showinfo("Éxito", f"{mensaje} (ID: {id_creado})")
            self.destroy()
        else:
            messagebox.showerror("Error", mensaje)
