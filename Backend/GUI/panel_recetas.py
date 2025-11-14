import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from Backend.DAO.RecetaDAO import RecetaDAO
from Backend.DAO.PacienteDAO import PacienteDAO
from Backend.DAO.MedicoDAO import MedicoDAO

class PanelRecetas(tk.Toplevel):
    """Panel para que un paciente vea sus recetas y filtre por vigentes/vencidas."""
    def __init__(self, parent, usuario):
        super().__init__(parent)
        self.title("Mis Recetas")
        self.geometry("800x400")
        self.usuario = usuario

        self.create_widgets()
        self.cargar_recetas()

    def create_widgets(self):
        top_frame = ttk.Frame(self, padding=10)
        top_frame.pack(fill='x')

        ttk.Label(top_frame, text="Filtrar:").pack(side='left')
        self.filtro_var = tk.StringVar(value='todas')
        opciones = [('Todas', 'todas'), ('Vigentes', 'vigentes'), ('Vencidas', 'vencidas')]
        for txt, val in opciones:
            ttk.Radiobutton(top_frame, text=txt, variable=self.filtro_var, value=val, command=self.cargar_recetas).pack(side='left', padx=6)

        # Treeview
        cols = ('id', 'fecha', 'medico', 'detalles', 'estado')
        self.tree = ttk.Treeview(self, columns=cols, show='headings')
        for c, t in zip(cols, ('ID', 'Fecha Emisión', 'Médico', 'Detalles', 'Estado')):
            self.tree.heading(c, text=t)
            self.tree.column(c, width=120 if c!='detalles' else 300)
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)

    def cargar_recetas(self):
        # Obtener paciente por usuario
        paciente = PacienteDAO().obtener_paciente_por_usuario(self.usuario)
        if not paciente:
            messagebox.showerror('Error', 'No se pudo determinar el paciente')
            self.destroy()
            return

        recetas = RecetaDAO().obtener_recetas_por_paciente(paciente.id_paciente)

        # Limpiar
        for i in self.tree.get_children():
            self.tree.delete(i)

        hoy = date.today()
        filtro = self.filtro_var.get()

        for r in recetas:
            # r may have attributes 'fecha'/'descripcion' or 'fecha_emision'/'detalles'
            raw_fecha = getattr(r, 'fecha_emision', None) or getattr(r, 'fecha', None)
            try:
                # Fecha puede tener formato datetime o string
                if isinstance(raw_fecha, str):
                    fecha_dt = datetime.strptime(raw_fecha.split('.')[0], '%Y-%m-%d %H:%M:%S') if ' ' in raw_fecha else datetime.strptime(raw_fecha, '%Y-%m-%d')
                else:
                    fecha_dt = raw_fecha
            except Exception:
                # Intentar parseo simple YYYY-MM-DD
                try:
                    fecha_dt = datetime.strptime(str(raw_fecha), '%Y-%m-%d')
                except Exception:
                    fecha_dt = None

            vencimiento = None
            if fecha_dt:
                # Vigencia 1 mes desde fecha_emision
                year = fecha_dt.year
                month = fecha_dt.month + 1
                if month == 13:
                    month = 1
                    year += 1
                day = fecha_dt.day
                # ajustar si el mes siguiente no tiene ese día
                import calendar
                last_day = calendar.monthrange(year, month)[1]
                if day > last_day:
                    day = last_day
                vencimiento = date(year, month, day)

            estado = 'Vencida' if (vencimiento and vencimiento < hoy) else 'Vigente'

            # Aplicar filtro
            if filtro == 'vigentes' and estado != 'Vigente':
                continue
            if filtro == 'vencidas' and estado != 'Vencida':
                continue

            # Obtener nombre médico
            medico_nombre = 'N/A'
            try:
                med = MedicoDAO().obtener_medico_por_id(r.id_medico)
                if med:
                    medico_nombre = f"{med.nombre} {med.apellido}"
            except Exception:
                pass

            fecha_str = fecha_dt.strftime('%Y-%m-%d') if fecha_dt else str(raw_fecha)
            self.tree.insert('', 'end', values=(r.id_receta, fecha_str, medico_nombre, getattr(r, 'detalles', getattr(r, 'descripcion', '')), estado))
