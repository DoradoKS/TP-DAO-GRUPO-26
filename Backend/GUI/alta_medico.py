import tkinter as tk
from tkinter import ttk, messagebox
from Backend.DAO.MedicoDAO import MedicoDAO
from Backend.DAO.EspecialidadDAO import EspecialidadDAO
from Backend.DAO.BarrioDAO import BarrioDAO
from Backend.Model.Medico import Medico
from Backend.DAO.UsuarioDAO import UsuarioDAO
from Backend.Validaciones.validaciones import Validaciones

class AltaMedico(tk.Toplevel):
    def __init__(self, parent, usuario="admin"):
        super().__init__(parent)
        self.title("Alta de Nuevo Médico")
        self.geometry("500x600")
        self.usuario = usuario

        self.especialidades = []
        self.barrios = []
        self.entries = {}

        self.create_widgets()
        self.cargar_comboboxes()

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        fields = [
            ("Usuario:", "Entry"), ("Contraseña:", "Entry"), ("Nombre:", "Entry"), 
            ("Apellido:", "Entry"), ("DNI:", "Entry"), ("Tipo DNI:", "Combobox"), 
            ("Matrícula:", "Entry"), ("Teléfono:", "Entry"), ("Email:", "Entry"),
            ("Calle:", "Entry"), ("Número:", "Entry"), ("Barrio:", "Entry"),
            ("Especialidad:", "Combobox")
        ]

        for i, (label_text, widget_type) in enumerate(fields):
            ttk.Label(main_frame, text=label_text, font=("Arial", 12)).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            
            if widget_type == "Entry":
                show_char = "*" if label_text == "Contraseña:" else None
                entry = ttk.Entry(main_frame, width=40, show=show_char)
                entry.grid(row=i, column=1, padx=10, pady=5)
                self.entries[label_text] = entry
            elif widget_type == "Combobox":
                if label_text == "Tipo DNI:":
                    self.tipo_dni_combo = ttk.Combobox(main_frame, width=38, state="readonly", values=["DNI", "Pasaporte", "Libreta de Enrolamiento", "Libreta Cívica"])
                    self.tipo_dni_combo.grid(row=i, column=1, padx=10, pady=5)
                    self.tipo_dni_combo.current(0)
                elif label_text == "Barrio:":
                    entry = ttk.Entry(main_frame, width=40)
                    entry.grid(row=i, column=1, padx=10, pady=5)
                    self.entries[label_text] = entry
                elif label_text == "Especialidad:":
                    self.especialidad_combo = ttk.Combobox(main_frame, width=38, state="readonly")
                    self.especialidad_combo.grid(row=i, column=1, padx=10, pady=5)

        guardar_button = ttk.Button(main_frame, text="Guardar", command=self.guardar_medico)
        guardar_button.grid(row=len(fields), column=0, columnspan=2, pady=20)

    def cargar_comboboxes(self):
        self.especialidades = EspecialidadDAO().obtener_todas_las_especialidades()
        self.especialidad_combo["values"] = [e.nombre for e in self.especialidades]
        if self.especialidades:
            self.especialidad_combo.current(0)

        self.barrios = []  # Ahora barrio se ingresa por teclado

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
        calle = self.entries["Calle:"].get().strip()
        numero_calle = self.entries["Número:"].get().strip()
        barrio_nombre = self.entries["Barrio:"].get().strip()
        
        selected_especialidad_nombre = self.especialidad_combo.get()
        id_especialidad = next((e.id_especialidad for e in self.especialidades if e.nombre == selected_especialidad_nombre), None)
        
        if not barrio_nombre:
            messagebox.showerror("Error", "Debe ingresar el barrio.")
            return
        id_barrio = BarrioDAO().obtener_o_crear_barrio(barrio_nombre)

        if not all([usuario, contraseña, nombre, apellido, dni, tipo_dni, matricula, telefono, email, calle, numero_calle, id_especialidad, id_barrio]):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        try:
            numero_calle_int = int(numero_calle)
        except ValueError:
            messagebox.showerror("Error", "El número de calle debe ser un entero.")
            return

        # Validar matrícula numérica antes de continuar
        try:
            matricula_int = int(matricula)
        except ValueError:
            messagebox.showerror("Error", "La matrícula debe ser un número entero.")
            return

        # Validaciones completas antes de crear el usuario para evitar usuarios huérfanos
        datos_validacion = {
            'usuario': usuario,
            'matricula': matricula_int,
            'nombre': nombre,
            'apellido': apellido,
            'tipo_dni': tipo_dni,
            'dni': dni,
            'email': email,
            'telefono': telefono
        }
        es_valido, errores = Validaciones.validar_medico_completo(datos_validacion)
        if not es_valido:
            messagebox.showerror("Errores de validación", "\n".join(errores))
            return

        usuario_dao = UsuarioDAO()
        creado, msg_usuario = usuario_dao.crear_usuario(usuario, contraseña, "Medico")
        if not creado:
            messagebox.showerror("Error al crear usuario", msg_usuario)
            return

        medico = Medico(
            usuario=usuario, nombre=nombre, apellido=apellido, matricula=matricula_int,
            tipo_dni=tipo_dni, dni=dni, email=email, telefono=telefono,
            id_especialidad=id_especialidad, calle=calle, numero_calle=numero_calle_int,
            id_barrio=id_barrio
        )

        id_creado, mensaje = MedicoDAO().crear_medico(medico, self.usuario)
        if id_creado:
            messagebox.showinfo("Éxito", f"{mensaje} (ID: {id_creado})")
            self.destroy()
        else:
            # Si falló la creación del médico, eliminar el usuario creado para evitar inconsistencias
            try:
                usuario_dao.eliminar_usuario(usuario)
            except Exception:
                pass
            messagebox.showerror("Error al crear médico", mensaje)
