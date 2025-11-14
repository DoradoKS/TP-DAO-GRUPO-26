import tkinter as tk
from tkinter import ttk, messagebox
from Backend.DAO.TurnoDAO import TurnoDAO
from Backend.DAO.MedicoDAO import MedicoDAO
from Backend.DAO.PacienteDAO import PacienteDAO
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
        style.configure("Header.TLabel", background="#333333", foreground="white")
        
        # Estilo para los botones de reporte
        style.configure("Report.TButton", 
                        background="#555555", 
                        foreground="white", 
                        font=("Arial", 10, "bold"),
                        padding=10)
        style.map("Report.TButton", 
                  background=[('active', '#777777')],
                  foreground=[('active', 'white')])
        # -----------------------------

        # --- DAOs ---
        self.turno_dao = TurnoDAO()
        self.medico_dao = MedicoDAO()
        self.paciente_dao = PacienteDAO()
        
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
        btn_reporte1 = ttk.Button(filter_frame, text="Turnos por Médico", command=self.generar_reporte_1, style="Report.TButton", width=25)
        btn_reporte1.grid(row=0, column=3, padx=10, pady=5, sticky="ew")
        
        btn_reporte2 = ttk.Button(filter_frame, text="Turnos por Especialidad", command=self.generar_reporte_2, style="Report.TButton", width=25)
        btn_reporte2.grid(row=1, column=3, padx=10, pady=5, sticky="ew")
        
        btn_reporte3 = ttk.Button(filter_frame, text="Pacientes Atendidos", command=self.generar_reporte_3, style="Report.TButton", width=25)
        btn_reporte3.grid(row=2, column=3, padx=10, pady=5, sticky="ew")

        btn_reporte4 = ttk.Button(filter_frame, text="Gráfico Asistencias", command=self.generar_reporte_4, style="Report.TButton", width=25)
        btn_reporte4.grid(row=3, column=3, padx=10, pady=5, sticky="ew")

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

    def generar_reporte_1(self):
        self.label_titulo_reporte.config(text="Reporte: Turnos por Médico")
        # Ocultar el gráfico (si está visible)
        self.chart_frame.pack_forget()
        # Mostrar la tabla (TreeView)
        self.tree.pack(fill="both", expand=True, side="left")
        
        # 1. Obtener datos de los filtros
        medico_nombre = self.combo_medicos.get()
        
        # --- OBTENEMOS DATOS DEL CALENDARIO ---
        try:
            fecha_obj_inicio = self.entry_fecha_inicio.get_date()
            fecha_obj_fin = self.entry_fecha_fin.get_date()
            
            # Formateamos a string para el DAO
            fecha_inicio = fecha_obj_inicio.strftime('%Y-%m-%d')
            fecha_fin = fecha_obj_fin.strftime('%Y-%m-%d')
        except Exception as e:
            messagebox.showerror("Error de fecha", "Fechas inválidas seleccionadas.", parent=self)
            return
        # ----------------------------------------

        # 2. Validar entradas
        if not medico_nombre:
            messagebox.showwarning("Faltan datos", "Debe seleccionar un médico.", parent=self)
            return

        if fecha_obj_fin < fecha_obj_inicio:
            messagebox.showwarning("Rango inválido", "La 'Fecha Fin' no puede ser anterior a la 'Fecha Inicio'.", parent=self)
            return
            
        id_medico = None
        for m in self.medicos:
            if f"{m.nombre} {m.apellido}" == medico_nombre:
                id_medico = m.id_medico
                break
        
        if id_medico is None:
             messagebox.showerror("Error", "Médico no válido.", parent=self)
             return

        # 3. Limpiar tabla (TreeView)
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.tree.configure(columns=("id", "paciente", "fecha", "hora", "estado"), show="headings")
        self.tree.heading("id", text="ID Turno")
        self.tree.heading("paciente", text="Paciente")
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("hora", text="Hora")
        self.tree.heading("estado", text="Estado")
        self.tree.column("id", width=60, anchor="center")
        
        # 4. Llamar al Backend (DAO)
        try:
            turnos_encontrados = self.turno_dao.reporte_turnos_por_medico_y_periodo(id_medico, fecha_inicio, fecha_fin)
            if not turnos_encontrados:
                messagebox.showinfo("Sin resultados", "No se encontraron turnos para ese médico en ese período.", parent=self)
                return

            # 5. Poblar la tabla
            for t in turnos_encontrados:
                pac = self.paciente_dao.buscar_paciente_por_id_paciente(t.id_paciente)
                paciente_nombre = f"{pac.nombre} {pac.apellido}" if pac else "N/A"
                
                # --- AQUÍ LA CORRECCIÓN ---
                if t.fecha_hora:
                    # Si la fecha_hora existe, la partimos
                    fecha, hora = t.fecha_hora.split(" ")
                    hora = hora[:5] # (Solo HH:MM)
                else:
                    # Si es None, ponemos valores por defecto
                    fecha = "Fecha N/A"
                    hora = "Hora N/A"
                # -------------------------
                
                estado = 'Pendiente' if t.asistio is None else ('Asistió' if t.asistio == 1 else 'Inasistencia')
                
                self.tree.insert("", "end", values=(
                    t.id_turno,
                    paciente_nombre,
                    fecha,
                    hora,
                    estado
                ))
        except Exception as e:
            print(f"Error generando reporte 1: {e}")
            messagebox.showerror("Error de Backend", "No se pudo generar el reporte. Revise la consola.", parent=self)

    
    def generar_reporte_2(self):
        self.label_titulo_reporte.config(text="Reporte: Turnos por Especialidad")

        # Ocultar el gráfico (si está visible)
        self.chart_frame.pack_forget()
        # Mostrar la tabla (TreeView)
        self.tree.pack(fill="both", expand=True, side="left")
        
        # 1. Limpiar y Reconfigurar tabla (TreeView)
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # --- RECONFIGURAR COLUMNAS PARA REPORTE 2 ---
        self.tree.configure(columns=("especialidad", "cantidad"), show="headings")
        self.tree.heading("especialidad", text="Especialidad")
        self.tree.heading("cantidad", text="Cantidad de Turnos")
        self.tree.column("especialidad", width=200) # Damos más ancho
        self.tree.column("cantidad", width=150, anchor="center")
        # ---------------------------------------------
        
        # 2. Llamar al Backend (DAO)
        try:
            # Este método del DAO ya lo creamos
            datos_reporte = self.turno_dao.reporte_cantidad_turnos_por_especialidad()
            
            if not datos_reporte:
                messagebox.showinfo("Sin resultados", "No se encontraron turnos para generar el reporte.", parent=self)
                return

            # 3. Poblar la tabla
            for (especialidad_nombre, cantidad) in datos_reporte:
                self.tree.insert("", "end", values=(
                    especialidad_nombre,
                    cantidad
                ))
        
        except Exception as e:
            print(f"Error generando reporte 2: {e}")
            messagebox.showerror("Error de Backend", "No se pudo generar el reporte. Revise la consola.", parent=self)


    def generar_reporte_3(self):
        self.label_titulo_reporte.config(text="Reporte: Pacientes Atendidos")
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
            datos = self.turno_dao.reporte_asistencia_global()
            
            if not datos or (datos[0] is None and datos[1] is None):
                messagebox.showinfo("Sin resultados", "No hay datos de asistencia para graficar.", parent=self)
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

        except Exception as e:
            print(f"Error generando reporte 4 (gráfico): {e}")
            messagebox.showerror("Error de Backend", "No se pudo generar el gráfico. Revise la consola.", parent=self)