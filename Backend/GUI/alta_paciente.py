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
        self.tipos_dni = []
        self.entries = {}
        self.create_widgets()
        self.cargar_comboboxes()

    def create_widgets(self):
        form_frame = ttk.LabelFrame(self, text="Datos del Paciente")
        form_frame.pack(padx=20, pady=15, fill="both", expand=True)

        # Campos texto
        filas = [
            ("Usuario:", True), ("Contraseña:", True), ("Nombre:", True), ("Apellido:", True),
            ("Fecha Nacimiento (YYYY-MM-DD):", True), ("DNI:", True), ("Email:", True), ("Teléfono:", True),
            ("Calle:", True), ("Número:", True)
        ]
        row = 0
        for label_text, requerido in filas:
            ttk.Label(form_frame, text=label_text).grid(row=row, column=0, padx=8, pady=5, sticky="e")
            entry = ttk.Entry(form_frame, width=35, show="*" if label_text == "Contraseña:" else None)
            entry.grid(row=row, column=1, padx=8, pady=5, sticky="w")
            self.entries[label_text] = entry
            row += 1

        # Combobox Tipo DNI
        ttk.Label(form_frame, text="Tipo DNI:").grid(row=row, column=0, padx=8, pady=5, sticky="e")
        self.tipo_dni_combo = ttk.Combobox(form_frame, width=33, state="readonly")
        self.tipo_dni_combo.grid(row=row, column=1, padx=8, pady=5, sticky="w")
        row += 1
        # Combobox Obra Social
        ttk.Label(form_frame, text="Obra Social:").grid(row=row, column=0, padx=8, pady=5, sticky="e")
        self.obra_social_combo = ttk.Combobox(form_frame, width=33, state="readonly")
        self.obra_social_combo.grid(row=row, column=1, padx=8, pady=5, sticky="w")
        row += 1
        # Combobox Barrio
        ttk.Label(form_frame, text="Barrio:").grid(row=row, column=0, padx=8, pady=5, sticky="e")
        self.barrio_combo = ttk.Combobox(form_frame, width=33, state="readonly")
        self.barrio_combo.grid(row=row, column=1, padx=8, pady=5, sticky="w")
        row += 1

        guardar_button = ttk.Button(self, text="Registrar Paciente", command=self.guardar_paciente)
        guardar_button.pack(pady=10)

    def cargar_comboboxes(self):
        # Tipos DNI: intentar leer tabla TipoDni; si falla usar lista por defecto
        import sqlite3
        from Backend.BDD.Conexion import get_conexion
        conn = None
        tipos = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT tipo_dni, tipo FROM TipoDni ORDER BY tipo_dni")
            for tid, nombre in cursor.fetchall():
                tipos.append((tid, nombre))
        except sqlite3.Error:
            tipos = [(1, 'DNI'), (2, 'Pasaporte'), (3, 'Carnet Extranjero')]
        finally:
            if conn: conn.close()
        self.tipos_dni = tipos
        self.tipo_dni_combo['values'] = [t[1] for t in tipos]
        if tipos:
            self.tipo_dni_combo.current(0)

        # Obra Social
        self.obras_sociales = ObraSocialDAO().obtener_obra_social()
        self.obra_social_combo['values'] = [o.nombre for o in self.obras_sociales]
        if self.obras_sociales:
            self.obra_social_combo.current(0)

        # Barrios
        self.barrios = BarrioDAO().obtener_todos_los_barrios()
        self.barrio_combo['values'] = [b.nombre for b in self.barrios]
        if self.barrios:
            self.barrio_combo.current(0)

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

        if not all([usuario, contrasena, nombre, apellido, fecha_nac, dni, email, telefono, calle, numero_calle]):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        # Validar fecha
        try:
            datetime.strptime(fecha_nac, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Fecha de nacimiento inválida. Formato esperado YYYY-MM-DD.")
            return

        # Obtener ids seleccionados
        tipo_dni_nombre = self.tipo_dni_combo.get()
        tipo_dni_id = next((t[0] for t in self.tipos_dni if t[1] == tipo_dni_nombre), None)
        obra_social_nombre = self.obra_social_combo.get()
        id_obra_social = next((o.id_obra_social for o in self.obras_sociales if o.nombre == obra_social_nombre), None)
        barrio_nombre = self.barrio_combo.get()
        id_barrio = next((b.id_barrio for b in self.barrios if b.nombre == barrio_nombre), None)

        if not all([tipo_dni_id, id_obra_social, id_barrio]):
            messagebox.showerror("Error", "Debe seleccionar Tipo DNI, Obra Social y Barrio.")
            return

        # Crear usuario primero
        usuario_dao = UsuarioDAO()
        ok_usuario, msg_usuario = usuario_dao.crear_usuario(usuario, contrasena, "Paciente")
        if not ok_usuario:
            messagebox.showerror("Error", msg_usuario)
            return

        # Crear paciente
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
            tipo_dni=tipo_dni_id,
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
