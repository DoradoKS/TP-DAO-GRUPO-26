import tkinter as tk
from tkinter import ttk, messagebox
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

        generate_button = ttk.Button(report_frame, text="Generar Reporte", command=self.generar_reporte)
        generate_button.pack(pady=5)

        # Chart display
        self.chart_frame = ttk.Frame(main_frame)
        self.chart_frame.pack(padx=10, pady=10, fill="both", expand=True)

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

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
