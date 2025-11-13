import tkinter as tk
from tkinter import ttk, messagebox
from Backend.DAO.FranjaHorariaDAO import FranjaHorariaDAO
from Backend.Model.FranjaHoraria import FranjaHoraria

class PanelHorarios(tk.Toplevel):
    """
    Esta ventana (Toplevel) permite gestionar (ver, agregar, eliminar)
    las franjas horarias de un médico específico.
    """
    
    def __init__(self, parent, id_medico, nombre_medico):
        super().__init__(parent)
        self.title(f"Gestionar Horarios de: {nombre_medico}")
        self.geometry("600x450")
        
        # Guardamos el ID del médico que estamos editando
        self.id_medico = id_medico
        self.dao = FranjaHorariaDAO()

        # --- Widgets de Creación ---
        form_frame = ttk.Frame(self, padding=15)
        form_frame.pack(fill='x')

        ttk.Label(form_frame, text="Día de la Semana:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        # Usamos un Combobox para los días
        self.combo_dia = ttk.Combobox(form_frame, state="readonly", width=12)
        self.combo_dia['values'] = [
            ("1 - Lunes"),
            ("2 - Martes"),
            ("3 - Miércoles"),
            ("4 - Jueves"),
            ("5 - Viernes"),
            ("6 - Sábado"),
            ("7 - Domingo")
        ]
        self.combo_dia.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Hora Inicio (HH:MM):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_inicio = ttk.Entry(form_frame, width=15)
        self.entry_inicio.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Hora Fin (HH:MM):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_fin = ttk.Entry(form_frame, width=15)
        self.entry_fin.grid(row=2, column=1, padx=5, pady=5)

        btn_agregar = ttk.Button(form_frame, text="Agregar Franja", command=self.agregar_franja)
        btn_agregar.grid(row=3, column=1, padx=5, pady=10, sticky="e")

        # --- Separador ---
        ttk.Separator(self, orient='horizontal').pack(fill='x', padx=10, pady=5)

        # --- TreeView para Mostrar Franjas Existentes ---
        list_frame = ttk.Frame(self, padding=15)
        list_frame.pack(fill='both', expand=True)
        
        ttk.Label(list_frame, text="Horarios Laborales Programados:").pack(anchor="w")

        self.tree = ttk.Treeview(list_frame, columns=("id", "dia", "inicio", "fin"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("dia", text="Día")
        self.tree.heading("inicio", text="Hora Inicio")
        self.tree.heading("fin", text="Hora Fin")
        
        # Definir ancho de columnas
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("dia", width=150)
        
        self.tree.pack(fill='both', expand=True, pady=10)

        btn_eliminar = ttk.Button(self, text="Eliminar Franja Seleccionada", command=self.eliminar_franja)
        btn_eliminar.pack(pady=10)

        # Cargar las franjas existentes al abrir la ventana
        self.cargar_franjas_existentes()

    def cargar_franjas_existentes(self):
        """Limpia el TreeView y carga las franjas horarias del médico desde la BDD."""
        # Borrar datos viejos
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Mapeo de número de día a nombre (para que sea legible)
        dias_semana = {
            1: "1 - Lunes", 2: "2 - Martes", 3: "3 - Miércoles", 
            4: "4 - Jueves", 5: "5 - Viernes", 6: "6 - Sábado", 7: "7 - Domingo"
        }

        # Pedir los datos al DAO
        franjas = self.dao.obtener_por_medico(self.id_medico)
        
        # Insertar datos en el TreeView
        for franja in franjas:
            dia_texto = dias_semana.get(franja.dia_semana, "Día Inválido")
            self.tree.insert("", "end", values=(
                franja.id_franja,
                dia_texto,
                franja.hora_inicio,
                franja.hora_fin
            ))

    def agregar_franja(self):
        """Toma los datos de los Entrys y llama al DAO para insertar una nueva franja."""
        
        # 1. Obtener y validar datos
        dia_seleccionado = self.combo_dia.get()
        inicio = self.entry_inicio.get()
        fin = self.entry_fin.get()

        if not (dia_seleccionado and inicio and fin):
            messagebox.showerror("Error", "Todos los campos son obligatorios.", parent=self)
            return

        # (Acá deberías agregar validación de formato HH:MM)

        # Extraer el número del día (ej. "1 - Lunes" -> 1)
        try:
            dia_num = int(dia_seleccionado.split(" - ")[0])
        except Exception:
            messagebox.showerror("Error", "Seleccione un día válido.", parent=self)
            return

        # 2. Crear el objeto Modelo
        nueva_franja = FranjaHoraria(
            id_medico=self.id_medico,
            dia_semana=dia_num,
            hora_inicio=inicio,
            hora_fin=fin
        )

        # 3. Llamar al DAO
        resultado = self.dao.insertar(nueva_franja)
        
        if resultado:
            messagebox.showinfo("Éxito", "Franja horaria agregada correctamente.", parent=self)
            self.cargar_franjas_existentes() # Refrescar la lista
            # Limpiar campos
            self.entry_inicio.delete(0, tk.END)
            self.entry_fin.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "No se pudo agregar la franja horaria. Verifique la consola.", parent=self)

    def eliminar_franja(self):
        """Toma la franja seleccionada del TreeView y la elimina usando el DAO."""
        
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione una franja horaria de la lista para eliminar.", parent=self)
            return

        if not messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar esta franja horaria?", parent=self):
            return

        # Obtenemos el ID (el primer valor de la fila)
        id_franja_a_borrar = self.tree.item(selected_item[0])['values'][0]
        
        if self.dao.eliminar(id_franja_a_borrar):
            messagebox.showinfo("Éxito", "Franja horaria eliminada.", parent=self)
            self.cargar_franjas_existentes() # Refrescar la lista
        else:
            messagebox.showerror("Error", "No se pudo eliminar la franja.", parent=self)