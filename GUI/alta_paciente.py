import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry
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
        self.configure(bg="#333333")
        self.usuario = usuario
        self.obras_sociales = []
        self.barrios = []
        self.entries = {}
        self.create_widgets()
        self.cargar_comboboxes()

    def create_widgets(self):
        main_frame = tk.Frame(self, bg="#333333")
        main_frame.pack(padx=20, pady=15, fill="both", expand=True)

        fields = [
            ("Usuario:", "Entry"), ("Contraseña:", "Entry", {"show": "*"}),
            ("Nombre:", "Entry"), ("Apellido:", "Entry"),
            ("Fecha Nacimiento:", "DateEntry"),
            ("DNI:", "Entry"), ("Email:", "Entry"), ("Teléfono:", "Entry"),
            ("Calle:", "Entry"), ("Número:", "Entry"),
            ("Tipo DNI:", "Combobox"), ("Obra Social:", "Combobox"), ("Barrio:", "Combobox")
        ]

        for i, field_info in enumerate(fields):
            label_text = field_info[0]
            widget_type = field_info[1]
            options = field_info[2] if len(field_info) > 2 else {}

            label = tk.Label(main_frame, text=label_text, bg="#333333", fg="white")
            label.grid(row=i, column=0, padx=8, pady=5, sticky="e")

            if widget_type == "Entry":
                entry = ttk.Entry(main_frame, width=35, **options)
                entry.grid(row=i, column=1, padx=8, pady=5, sticky="w")
                self.entries[label_text] = entry
            
            elif widget_type == "DateEntry":
                # Usar patrón ISO consistente y obtener la fecha con get_date()
                self.fecha_nac_entry = DateEntry(main_frame, width=33, date_pattern='yyyy-mm-dd', state="readonly")
                self.fecha_nac_entry.grid(row=i, column=1, padx=8, pady=5, sticky="w")

            elif widget_type == "Combobox":
                if label_text == "Tipo DNI:":
                    self.tipo_dni_combo = ttk.Combobox(main_frame, width=33, state="readonly", values=["DNI", "Pasaporte", "Libreta de Enrolamiento", "Libreta Cívica"])
                    self.tipo_dni_combo.grid(row=i, column=1, padx=8, pady=5, sticky="w")
                elif label_text == "Obra Social:":
                    self.obra_social_combo = ttk.Combobox(main_frame, width=33, state="readonly")
                    self.obra_social_combo.grid(row=i, column=1, padx=8, pady=5, sticky="w")
                elif label_text == "Barrio:":
                    self.barrio_combo = ttk.Combobox(main_frame, width=33, state="readonly")
                    self.barrio_combo.grid(row=i, column=1, padx=8, pady=5, sticky="w")

        guardar_button = ttk.Button(self, text="Registrar Paciente", command=self.guardar_paciente)
        guardar_button.pack(pady=10)

    def cargar_comboboxes(self):
        if self.tipo_dni_combo['values']: self.tipo_dni_combo.current(0)
        self.obras_sociales = ObraSocialDAO().obtener_obra_social()
        self.obra_social_combo['values'] = [o.nombre for o in self.obras_sociales]
        if self.obras_sociales: self.obra_social_combo.current(0)
        self.barrios = BarrioDAO().obtener_todos_los_barrios()
        self.barrio_combo['values'] = [b.nombre for b in self.barrios]
        if self.barrios: self.barrio_combo.current(0)

    def guardar_paciente(self):
        usuario = self.entries["Usuario:"].get().strip()
        contrasena = self.entries["Contraseña:"].get().strip()
        nombre = self.entries["Nombre:"].get().strip()
        apellido = self.entries["Apellido:"].get().strip()
        # Obtener objeto date y formatear a ISO YYYY-MM-DD
        try:
            fecha_nac_date = self.fecha_nac_entry.get_date()
            fecha_nac = fecha_nac_date.strftime("%Y-%m-%d")
        except Exception:
            messagebox.showerror("Error", "Fecha de nacimiento inválida.")
            return

        dni = self.entries["DNI:"].get().strip()
        email = self.entries["Email:"].get().strip()
        telefono = self.entries["Teléfono:"].get().strip()
        calle = self.entries["Calle:"].get().strip()
        numero_calle = self.entries["Número:"].get().strip()

        if not all([usuario, contrasena, nombre, apellido, fecha_nac, dni, email, telefono, calle, numero_calle]):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        # fecha_nac ya validada/formateada como YYYY-MM-DD usando get_date()

        tipo_dni_nombre = self.tipo_dni_combo.get()
        obra_social_nombre = self.obra_social_combo.get()
        id_obra_social = next((o.id_obra_social for o in self.obras_sociales if o.nombre == obra_social_nombre), None)
        barrio_nombre = self.barrio_combo.get()
        id_barrio = next((b.id_barrio for b in self.barrios if b.nombre == barrio_nombre), None)

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
            id_barrio=id_barrio, usuario=usuario, nombre=nombre, apellido=apellido,
            fecha_nacimiento=fecha_nac, tipo_dni=tipo_dni_nombre, dni=dni, email=email,
            telefono=telefono, id_obra_social=id_obra_social, calle=calle, numero_calle=numero_calle_int
        )

        paciente_dao = PacienteDAO()
        id_creado, mensaje = paciente_dao.crear_paciente(paciente, self.usuario)
        if id_creado:
            messagebox.showinfo("Éxito", f"{mensaje} (ID: {id_creado})")
            # Enviar email de bienvenida (no bloquear en caso de error)
            try:
                import Backend.notifications as notifications
                try:
                    notifications.send_welcome_email(email, usuario, contrasena, nombre + ' ' + apellido)
                except Exception as e:
                    print(f"Advertencia: no se pudo enviar email de bienvenida: {e}")
            except Exception:
                pass
            self.destroy()
        else:
            messagebox.showerror("Error", mensaje)
