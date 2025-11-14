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

        ttk.Label(form_frame, text="Días de la Semana (seleccione uno o varios):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        # Usamos Listbox para permitir seleccionar varios días a la vez
        self.listbox_dias = tk.Listbox(form_frame, selectmode='multiple', height=7, exportselection=False)
        dias_vals = ["1 - Lunes", "2 - Martes", "3 - Miércoles", "4 - Jueves", "5 - Viernes", "6 - Sábado", "7 - Domingo"]
        for d in dias_vals:
            self.listbox_dias.insert(tk.END, d)
        self.listbox_dias.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Hora Inicio (HH:MM):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_inicio = ttk.Entry(form_frame, width=15)
        self.entry_inicio.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Hora Fin (HH:MM):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_fin = ttk.Entry(form_frame, width=15)
        self.entry_fin.grid(row=2, column=1, padx=5, pady=5)

        btn_agregar = ttk.Button(form_frame, text="Agregar Franja(s)", command=self.agregar_franja)
        btn_agregar.grid(row=3, column=1, padx=5, pady=10, sticky="e")
        btn_modificar = ttk.Button(form_frame, text="Modificar Franja Seleccionada", command=self.modificar_franja)
        btn_modificar.grid(row=3, column=0, padx=5, pady=10, sticky="w")

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
        selec_indices = self.listbox_dias.curselection()
        inicio = self.entry_inicio.get()
        fin = self.entry_fin.get()

        if not (selec_indices and inicio and fin):
            messagebox.showerror("Error", "Todos los campos son obligatorios.", parent=self)
            return

        # (Acá deberías agregar validación de formato HH:MM)

        # Insertar una franja por cada día seleccionado
        inserted_any = False
        errores = []
        for idx in selec_indices:
            dia_text = self.listbox_dias.get(idx)
            try:
                dia_num = int(dia_text.split(" - ")[0])
            except Exception:
                errores.append(f"Día inválido: {dia_text}")
                continue

            nueva_franja = FranjaHoraria(id_medico=self.id_medico, dia_semana=dia_num, hora_inicio=inicio, hora_fin=fin)
            resultado = self.dao.insertar(nueva_franja)
            if resultado:
                inserted_any = True
            else:
                errores.append(f"No se pudo insertar franja para {dia_text}.")

        if inserted_any:
            messagebox.showinfo("Éxito", "Franja(s) horaria(s) agregada(s) correctamente.", parent=self)
            self.cargar_franjas_existentes()
            self.entry_inicio.delete(0, tk.END)
            self.entry_fin.delete(0, tk.END)
            self.listbox_dias.selection_clear(0, tk.END)
        else:
            messagebox.showerror("Error", "No se pudieron agregar franjas. " + " ".join(errores), parent=self)

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

    def modificar_franja(self):
        """Modifica la franja seleccionada en el TreeView usando los valores actuales de los campos."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione una franja horaria de la lista para modificar.", parent=self)
            return

        if len(selected_item) > 1:
            messagebox.showwarning("Advertencia", "Seleccione sólo una franja para modificar.", parent=self)
            return

        id_franja = self.tree.item(selected_item[0])['values'][0]
        inicio = self.entry_inicio.get()
        fin = self.entry_fin.get()
        selec_indices = self.listbox_dias.curselection()

        if not (selec_indices and inicio and fin):
            messagebox.showerror("Error", "Seleccione un día y complete horas antes de modificar.", parent=self)
            return

        # Si el usuario seleccionó más de un día, sólo tomamos el primero para la modificación
        dia_text = self.listbox_dias.get(selec_indices[0])
        try:
            dia_num = int(dia_text.split(" - ")[0])
        except Exception:
            messagebox.showerror("Error", "Día inválido.", parent=self)
            return

        ok = self.dao.actualizar(id_franja, dia_num, inicio, fin)
        if ok:
            messagebox.showinfo("Éxito", "Franja actualizada correctamente.", parent=self)
            self.cargar_franjas_existentes()
        else:
            messagebox.showerror("Error", "No se pudo actualizar la franja. Verifique la consola.", parent=self)