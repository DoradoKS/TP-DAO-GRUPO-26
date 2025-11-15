import tkinter as tk
from tkinter import ttk, messagebox, filedialog
# Imports absolutos desde Backend
from Backend.DAO.TurnoDAO import TurnoDAO
from Backend.DAO.PacienteDAO import PacienteDAO
from Backend.DAO.MedicoDAO import MedicoDAO

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    _HAS_MATPLOTLIB = True
except Exception:
    # matplotlib no está instalado; las funciones de graficado mostrarán un mensaje de error al usuario
    plt = None
    FigureCanvasTkAgg = None
    _HAS_MATPLOTLIB = False

class Reportes(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Reportes y Estadísticas")
        self.geometry("800x600")

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Report selection
        report_frame = ttk.LabelFrame(main_frame, text="Seleccionar Reporte")
        report_frame.pack(padx=10, pady=10, fill="x")

        self.report_type = tk.StringVar()
        ttk.Radiobutton(report_frame, text="Turnos por Médico", variable=self.report_type, value="medico").pack(anchor="w")
        ttk.Radiobutton(report_frame, text="Turnos por Paciente", variable=self.report_type, value="paciente").pack(anchor="w")
        ttk.Radiobutton(report_frame, text="Turnos por Día", variable=self.report_type, value="dia").pack(anchor="w")
        ttk.Radiobutton(report_frame, text="Asistencias vs Inasistencias por Mes", variable=self.report_type, value="asistencia_mes").pack(anchor="w")

        actions_frame = ttk.Frame(report_frame)
        actions_frame.pack(pady=5, fill='x')

        generate_button = ttk.Button(actions_frame, text="Generar Reporte", command=self.generar_reporte)
        generate_button.pack(side='left')

        # Botón inline para exportar PDF junto al botón de generar (inicialmente deshabilitado)
        # Hacemos el botón inline más ancho para que quepa la etiqueta
        self.export_button_inline = ttk.Button(actions_frame, text='Exportar a PDF', command=self._export_fig_to_pdf, state='disabled', width=18)
        self.export_button_inline.pack(side='left', padx=8)

        # Chart display
        self.chart_frame = ttk.Frame(main_frame)
        self.chart_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Export controls (fuera del chart_frame para no ser destruidos al regenerar el gráfico)
        export_frame = ttk.Frame(main_frame)
        export_frame.pack(padx=10, pady=(0,10), fill="x")
        self.export_button = ttk.Button(export_frame, text='Exportar a PDF', command=self._export_fig_to_pdf, state='disabled', width=18)
        self.export_button.pack(side='left')

    def generar_reporte(self):
        report_type = self.report_type.get()
        if not report_type:
            messagebox.showwarning("Advertencia", "Seleccione un tipo de reporte.")
            return

        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        if not _HAS_MATPLOTLIB:
            messagebox.showerror("Dependencia faltante", "matplotlib no está instalado. Instale matplotlib para ver reportes.")
            return

        if report_type == "medico":
            self.reporte_turnos_por_medico()
        elif report_type == "paciente":
            self.reporte_turnos_por_paciente()
        elif report_type == "dia":
            self.reporte_turnos_por_dia()
        elif report_type == "asistencia_mes":
            self.reporte_asistencias_vs_inasistencias_por_mes()

    def reporte_turnos_por_medico(self):
        turno_dao = TurnoDAO()
        medico_dao = MedicoDAO()
        
        medicos = medico_dao.obtener_todos_los_medicos()
        medico_nombres = [f"{m.nombre} {m.apellido}" for m in medicos]
        turnos_counts = [turno_dao.contar_turnos_por_medico(m.id_medico) for m in medicos]

        self.crear_grafico_barras(medico_nombres, turnos_counts, "Turnos por Médico", "Médicos", "Cantidad de Turnos")

    def reporte_turnos_por_paciente(self):
        turno_dao = TurnoDAO()
        paciente_dao = PacienteDAO()

        pacientes = paciente_dao.obtener_todos_los_pacientes()
        paciente_nombres = [f"{p.nombre} {p.apellido}" for p in pacientes]
        turnos_counts = [turno_dao.contar_turnos_por_paciente(p.id_paciente) for p in pacientes]

        self.crear_grafico_barras(paciente_nombres, turnos_counts, "Turnos por Paciente", "Pacientes", "Cantidad de Turnos")

    def reporte_turnos_por_dia(self):
        turno_dao = TurnoDAO()
        turnos = turno_dao.obtener_todos_los_turnos()
        
        turnos_por_dia = {}
        for turno in turnos:
            fecha = turno.fecha_hora.split(" ")[0]
            turnos_por_dia[fecha] = turnos_por_dia.get(fecha, 0) + 1
            
        dias = list(turnos_por_dia.keys())
        turnos_counts = list(turnos_por_dia.values())

        self.crear_grafico_barras(dias, turnos_counts, "Turnos por Día", "Fecha", "Cantidad de Turnos")

    def crear_grafico_barras(self, x_data, y_data, title, xlabel, ylabel):
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(x_data, y_data)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        # Botón interno visible encima del gráfico (fallback prominente)
        try:
            if hasattr(self, '_inner_export_button') and self._inner_export_button:
                self._inner_export_button.destroy()
        except Exception:
            pass
        try:
            inner_frame = ttk.Frame(self.chart_frame)
            inner_frame.pack(fill='x')
            # botón en tk para garantizar contraste en temas oscuros
            self._inner_export_button = tk.Button(inner_frame, text='Exportar a PDF', command=self._export_fig_to_pdf, bg='#ffcc00')
            self._inner_export_button.pack(side='left', padx=6, pady=6)
        except Exception:
            pass

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        # Guardamos figura para permitir exportar a PDF y habilitamos los botones
        self.current_fig = fig
        try:
            if hasattr(self, 'export_button'):
                self.export_button.config(state='normal')
        except Exception:
            pass
        try:
            if hasattr(self, 'export_button_inline'):
                self.export_button_inline.config(state='normal')
        except Exception:
            pass

    def reporte_asistencias_vs_inasistencias_por_mes(self):
        turno_dao = TurnoDAO()
        datos = turno_dao.obtener_resumen_asistencia_por_mes()
        if not datos:
            messagebox.showinfo("Info", "No hay datos de asistencia/inasistencia registrados.")
            return

        meses = [d[0] for d in datos]
        asist = [d[1] for d in datos]
        inasist = [d[2] for d in datos]

        fig, ax = plt.subplots(figsize=(10, 5))
        x = range(len(meses))
        ax.bar([i - 0.2 for i in x], asist, width=0.4, label='Asistencias')
        ax.bar([i + 0.2 for i in x], inasist, width=0.4, label='Inasistencias')
        ax.set_title("Asistencias vs Inasistencias por Mes")
        ax.set_xlabel("Mes")
        ax.set_ylabel("Cantidad")
        ax.set_xticks(x)
        ax.set_xticklabels(meses, rotation=45, ha="right")
        ax.legend()
        plt.tight_layout()

        # Botón interno visible encima del gráfico (fallback prominente)
        try:
            if hasattr(self, '_inner_export_button') and self._inner_export_button:
                self._inner_export_button.destroy()
        except Exception:
            pass
        try:
            inner_frame = ttk.Frame(self.chart_frame)
            inner_frame.pack(fill='x')
            self._inner_export_button = tk.Button(inner_frame, text='Exportar a PDF', command=self._export_fig_to_pdf, bg='#ffcc00')
            self._inner_export_button.pack(side='left', padx=6, pady=6)
        except Exception:
            pass

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        # Guardamos figura para permitir exportar a PDF y habilitamos los botones
        self.current_fig = fig
        try:
            if hasattr(self, 'export_button'):
                self.export_button.config(state='normal')
        except Exception:
            pass
        try:
            if hasattr(self, 'export_button_inline'):
                self.export_button_inline.config(state='normal')
        except Exception:
            pass

    def _export_fig_to_pdf(self):
        """Exporta la figura actual a PDF mediante un diálogo de guardado."""
        if not hasattr(self, 'current_fig') or self.current_fig is None:
            messagebox.showwarning('Advertencia', 'No hay gráfico para exportar.')
            return
        path = filedialog.asksaveasfilename(defaultextension='.pdf', filetypes=[('PDF files', '*.pdf')], title='Guardar gráfico como PDF')
        if not path:
            return
        try:
            self.current_fig.savefig(path, format='pdf')
            messagebox.showinfo('Exportado', f'Gráfico exportado a {path}')
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo exportar el PDF: {e}')
