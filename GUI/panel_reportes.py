import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from Backend.DAO.TurnoDAO import TurnoDAO
from Backend.DAO.MedicoDAO import MedicoDAO
from Backend.DAO.PacienteDAO import PacienteDAO

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except Exception:
    Figure = None
    FigureCanvasTkAgg = None
    HAS_MATPLOTLIB = False

# Importamos el calendario
from tkcalendar import DateEntry
from datetime import date

class PanelReportes(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Panel de Reportes")
        self.geometry("900x600")
        self.configure(bg="#333333")

        # --- DEFINICIÓN DE ESTILOS ---
        style = ttk.Style(self)
        
        # Estilo para el fondo principal
        style.configure("Main.TFrame", background="#333333")
        
        # Estilo para el LabelFrame
        style.configure("TLabelframe", background="#333333", bordercolor="#555555")
        style.configure("TLabelframe.Label", background="#333333", foreground="white", font=("Arial", 11, "bold"))
        
        # Estilo para las etiquetas
        style.configure("TLabel", background="#333333", foreground="white")
        # Estilo corregido para el título del reporte: fondo oscuro, texto blanco
        style.configure("Header.TLabel", background="#333333", foreground="white") 
        
        # Estilo para los botones de reporte
        style.configure("Report.TButton", 
                        background="#555555", 
                        foreground="black", # Cambiado a negro
                        font=("Arial", 10, "bold"),
                        padding=10)
        style.map("Report.TButton", 
                  background=[('active', '#777777')],
                  foreground=[('active', 'black')]) # Cambiado a negro
        # -----------------------------

        # --- DAOs ---
        self.turno_dao = TurnoDAO()
        self.medico_dao = MedicoDAO()
        self.paciente_dao = PacienteDAO()
        # Figura actual para exportar
        self.current_fig = None
        
        # --- Datos para combos ---
        self.medicos = []
        self.create_widgets()
        self.cargar_combo_medicos()

    def create_widgets(self):
        main_frame = ttk.Frame(self, style="Main.TFrame")
        main_frame.pack(expand=True, fill="both")

        # --- Frame de Filtros y Acciones ---
        filter_frame = ttk.LabelFrame(main_frame, text="Filtros y Reportes", style="TLabelframe")
        filter_frame.pack(padx=20, pady=20, fill="x")

        # Asegurar columnas para botones y sus export buttons
        filter_frame.grid_columnconfigure(3, weight=1)
        filter_frame.grid_columnconfigure(4, weight=0)

        # --- Columna 0 y 1: FILTROS ---
        ttk.Label(filter_frame, text="Médico:", style="TLabel").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.combo_medicos = ttk.Combobox(filter_frame, width=30, state="readonly")
        self.combo_medicos.grid(row=0, column=1, padx=5, pady=10, sticky="w")

        ttk.Label(filter_frame, text="Fecha Inicio:", style="TLabel").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.entry_fecha_inicio = DateEntry(filter_frame, width=15, date_pattern='y-mm-dd',
                                            background='darkblue', foreground='white', borderwidth=2)
        self.entry_fecha_inicio.grid(row=1, column=1, padx=5, pady=10, sticky="w")

        ttk.Label(filter_frame, text="Fecha Fin:", style="TLabel").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.entry_fecha_fin = DateEntry(filter_frame, width=15, date_pattern='y-mm-dd',
                                         background='darkblue', foreground='white', borderwidth=2)
        self.entry_fecha_fin.grid(row=2, column=1, padx=5, pady=10, sticky="w")
        
        # --- Columna 2: Separador Vertical ---
        ttk.Separator(filter_frame, orient='vertical').grid(row=0, column=2, rowspan=4, sticky='ns', padx=20, pady=5)

        # --- Columna 3: BOTONES DE ACCIÓN ---
        # Nota: opción 'Turnos por Médico' eliminada según pedido
        
        btn_reporte2 = ttk.Button(filter_frame, text="Turnos por Especialidad", command=self.generar_reporte_2, style="Report.TButton", width=25)
        btn_reporte2.grid(row=1, column=3, padx=10, pady=5, sticky="ew")
        # Export button for reporte 2 (disabled until chart exists)
        self.btn_export_reporte2 = ttk.Button(filter_frame, text="Exportar PDF", command=self.export_current_chart, style="Report.TButton", width=12, state="disabled")
        self.btn_export_reporte2.grid(row=1, column=4, padx=(5,10), pady=5, sticky="w")
        btn_reporte3 = ttk.Button(filter_frame, text="Pacientes Atendidos", command=self.generar_reporte_3, style="Report.TButton", width=25)
        btn_reporte3.grid(row=2, column=3, padx=10, pady=5, sticky="ew")
        btn_reporte4 = ttk.Button(filter_frame, text="Gráfico Asistencias", command=self.generar_reporte_4, style="Report.TButton", width=25)
        btn_reporte4.grid(row=3, column=3, padx=10, pady=5, sticky="ew")
        # Export button for reporte 4 (disabled until chart exists)
        self.btn_export_reporte4 = ttk.Button(filter_frame, text="Exportar PDF", command=self.export_current_chart, style="Report.TButton", width=12, state="disabled")
        self.btn_export_reporte4.grid(row=3, column=4, padx=(5,10), pady=5, sticky="w")

        # Nota: botón global eliminado para mostrar botones de export junto a cada reporte

        # --- Título de Resultados (NUEVO) ---
        self.label_titulo_reporte = ttk.Label(main_frame, text="Resultados del Reporte", style="Header.TLabel", font=("Arial", 14, "bold"))
        self.label_titulo_reporte.pack(padx=20, pady=(10, 0), anchor="w")

        # --- Frame de Resultados (Tabla) ---
        self.tree_frame = ttk.Frame(main_frame)
        self.tree_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        self.tree = ttk.Treeview(self.tree_frame, columns=("1", "2", "3", "4", "5"), show="headings")
        self.tree.pack(fill="both", expand=True, side="left")
        
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # --- Frame del Gráfico (Lienzo) ---
        self.chart_frame = ttk.Frame(main_frame, style="Main.TFrame")
        # (No lo mostramos con .pack() aún)

    def cargar_combo_medicos(self):
        """Carga el ComboBox con todos los médicos."""
        try:
            # Asumo que tenés un método que devuelve todos los médicos
            self.medicos = self.medico_dao.obtener_medicos() 
            self.combo_medicos["values"] = [f"{m.nombre} {m.apellido}" for m in self.medicos]
        except Exception as e:
            print(f"Error cargando médicos: {e}")
            messagebox.showerror("Error", "No se pudo cargar la lista de médicos.")

    
    def generar_reporte_2(self):
        self.label_titulo_reporte.config(text="Reporte: Turnos por Especialidad")
        # Ocultar la tabla y preparar el frame del gráfico
        self.tree.pack_forget()
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Obtener y validar fechas del calendario
        try:
            fecha_obj_inicio = self.entry_fecha_inicio.get_date()
            fecha_obj_fin = self.entry_fecha_fin.get_date()
            fecha_inicio = fecha_obj_inicio.strftime('%Y-%m-%d')
            fecha_fin = fecha_obj_fin.strftime('%Y-%m-%d')
        except Exception:
            messagebox.showerror("Error de fecha", "Fechas inválidas seleccionadas.", parent=self)
            return

        if fecha_obj_fin < fecha_obj_inicio:
            messagebox.showwarning("Rango inválido", "La 'Fecha Fin' no puede ser anterior a la 'Fecha Inicio'.", parent=self)
            return

        # Llamar al Backend (DAO) con el rango de fechas
        try:
            datos_reporte = self.turno_dao.reporte_cantidad_turnos_por_especialidad_periodo(fecha_inicio, fecha_fin)
            if not datos_reporte:
                messagebox.showinfo("Sin resultados", "No se encontraron turnos para generar el reporte en ese período.", parent=self)
                return

            # Preparar datos para gráfico
            nombres = [d[0] for d in datos_reporte]
            cantidades = [d[1] for d in datos_reporte]

            if not HAS_MATPLOTLIB:
                messagebox.showwarning("Matplotlib no instalado", "Instale matplotlib para ver el gráfico.", parent=self)
                return

            fig = Figure(figsize=(8, 5), dpi=100)
            ax = fig.add_subplot(111)
            ax.bar(nombres, cantidades, color='#4C78A8')
            ax.set_title(f'Turnos por Especialidad\n{fecha_inicio} a {fecha_fin}')
            ax.set_xlabel('Especialidad')
            ax.set_ylabel('Cantidad de Turnos')
            ax.set_xticks(range(len(nombres)))
            ax.set_xticklabels(nombres, rotation=45, ha='right')
            fig.tight_layout()

            # Mostrar en canvas
            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

            # Guardar figura actual y habilitar exportación (específico para reporte 2)
            self.current_fig = fig
            try:
                self.btn_export_reporte2.configure(state="normal")
            except Exception:
                pass

        except Exception as e:
            print(f"Error generando reporte 2 (gráfico): {e}")
            messagebox.showerror("Error de Backend", "No se pudo generar el reporte. Revise la consola.", parent=self)


    def generar_reporte_3(self):
        self.label_titulo_reporte.config(text="Reporte: Pacientes Atendidos")
        # Deshabilitar export buttons
        try:
            self.btn_export_reporte2.configure(state="disabled")
        except Exception:
            pass
        try:
            self.btn_export_reporte4.configure(state="disabled")
        except Exception:
            pass
        # Ocultar el gráfico (si está visible)
        self.chart_frame.pack_forget()
        # Mostrar la tabla (TreeView)
        self.tree.pack(fill="both", expand=True, side="left")
        
        # 1. Obtener datos de los filtros (solo fechas)
        try:
            fecha_obj_inicio = self.entry_fecha_inicio.get_date()
            fecha_obj_fin = self.entry_fecha_fin.get_date()
            fecha_inicio = fecha_obj_inicio.strftime('%Y-%m-%d')
            fecha_fin = fecha_obj_fin.strftime('%Y-%m-%d')
        except Exception as e:
            messagebox.showerror("Error de fecha", "Fechas inválidas seleccionadas.", parent=self)
            return

        # 2. Validar rango
        if fecha_obj_fin < fecha_obj_inicio:
            messagebox.showwarning("Rango inválido", "La 'Fecha Fin' no puede ser anterior a la 'Fecha Inicio'.", parent=self)
            return

        # 3. Limpiar y Reconfigurar tabla (TreeView)
        for item in self.tree.get_children():
            self.tree.delete(item)

        # --- RECONFIGURAR COLUMNAS PARA REPORTE 3 ---
        self.tree.configure(columns=("id_pac", "nombre", "apellido", "dni", "email"), show="headings")
        self.tree.heading("id_pac", text="ID Paciente")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("apellido", text="Apellido")
        self.tree.heading("dni", text="DNI")
        self.tree.heading("email", text="Email")
        self.tree.column("id_pac", width=80, anchor="center")
        self.tree.column("nombre", width=150)
        self.tree.column("apellido", width=150)
        self.tree.column("dni", width=100)
        self.tree.column("email", width=200)
        # ---------------------------------------------

        # 4. Llamar al Backend (DAO)
        try:
            # Este método del PacienteDAO ya lo creamos
            pacientes_encontrados = self.paciente_dao.reporte_pacientes_atendidos_por_fecha(fecha_inicio, fecha_fin)
            
            if not pacientes_encontrados:
                messagebox.showinfo("Sin resultados", "No se encontraron pacientes atendidos en ese período.", parent=self)
                return

            # 5. Poblar la tabla
            for pac in pacientes_encontrados:
                self.tree.insert("", "end", values=(
                    pac.id_paciente,
                    pac.nombre,
                    pac.apellido,
                    pac.dni,
                    pac.email
                ))
        
        except Exception as e:
            print(f"Error generando reporte 3: {e}")
            messagebox.showerror("Error de Backend", "No se pudo generar el reporte. Revise la consola.", parent=self)


    def generar_reporte_4(self):
        
        if not HAS_MATPLOTLIB:
            messagebox.showwarning("Matplotlib no instalado",
                       "La librería 'matplotlib' no está instalada.\nInstale con:\n\n  pip install matplotlib\n\npara ver el gráfico.",
                       parent=self)
            return
        self.label_titulo_reporte.config(text="Reporte: Gráfico de Asistencias")
        # Ocultar la tabla (TreeView)
        self.tree.pack_forget() 
        # Limpiar el frame del gráfico (por si ya había uno)
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        # Mostrar el frame del gráfico
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 2. Llamar al Backend (DAO)
        try:
            # Este método del TurnoDAO ya lo creamos
            # Devuelve una tupla (asistencias, inasistencias, pendientes)
            # Obtener fechas del calendario y validar
            try:
                fecha_obj_inicio = self.entry_fecha_inicio.get_date()
                fecha_obj_fin = self.entry_fecha_fin.get_date()
                fecha_inicio = fecha_obj_inicio.strftime('%Y-%m-%d')
                fecha_fin = fecha_obj_fin.strftime('%Y-%m-%d')
            except Exception:
                messagebox.showerror("Error de fecha", "Fechas inválidas seleccionadas.", parent=self)
                return

            if fecha_obj_fin < fecha_obj_inicio:
                messagebox.showwarning("Rango inválido", "La 'Fecha Fin' no puede ser anterior a la 'Fecha Inicio'.", parent=self)
                return

            datos = self.turno_dao.reporte_asistencia_por_periodo(fecha_inicio, fecha_fin)

            if not datos or (datos[0] is None and datos[1] is None and datos[2] is None):
                messagebox.showinfo("Sin resultados", "No hay datos de asistencia para graficar en ese período.", parent=self)
                return

            asistencias = datos[0] if datos[0] is not None else 0
            inasistencias = datos[1] if datos[1] is not None else 0
            pendientes = datos[2] if datos[2] is not None else 0

            # 3. Preparar los datos para Matplotlib
            labels = ['Asistencias', 'Inasistencias', 'Pendientes']
            valores = [asistencias, inasistencias, pendientes]
            colores = ['#4CAF50', '#F44336', '#FFC107'] # Verde, Rojo, Ámbar

            # 4. Crear la Figura (El Gráfico)
            # Creamos una figura de matplotlib (tamaño 8x5 pulgadas)
            fig = Figure(figsize=(8, 5), dpi=100)
            # Le agregamos un "subplot" (un set de ejes)
            ax = fig.add_subplot(111) 
            
            # Creamos el gráfico de barras
            ax.bar(labels, valores, color=colores)
            
            # Seteamos títulos y etiquetas
            ax.set_title('Resumen de Asistencia de Pacientes')
            ax.set_ylabel('Cantidad de Turnos')
            ax.set_ylim(0, max(valores) * 1.2) # Damos un 20% de espacio arriba

            # 5. "Dibujar" el gráfico en el "Lienzo" de Tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

            # Guardar figura actual y habilitar exportación (específico para reporte 4)
            self.current_fig = fig
            try:
                self.btn_export_reporte4.configure(state="normal")
            except Exception:
                pass

        except Exception as e:
            print(f"Error generando reporte 4 (gráfico): {e}")
            messagebox.showerror("Error de Backend", "No se pudo generar el gráfico. Revise la consola.", parent=self)

    def export_current_chart(self):
        """Abre un diálogo para exportar la figura actual a PDF."""
        if not HAS_MATPLOTLIB or self.current_fig is None:
            messagebox.showerror("Error", "No hay un gráfico para exportar o matplotlib no está disponible.", parent=self)
            return
        path = filedialog.asksaveasfilename(defaultextension='.pdf', filetypes=[('PDF files', '*.pdf')], title='Guardar gráfico como PDF', parent=self)
        if not path:
            return
        try:
            self.current_fig.savefig(path, format='pdf')
            messagebox.showinfo("Exportado", f"Gráfico exportado correctamente a:\n{path}", parent=self)
        except Exception as e:
            messagebox.showerror("Error al exportar", f"No se pudo exportar el gráfico: {e}", parent=self)