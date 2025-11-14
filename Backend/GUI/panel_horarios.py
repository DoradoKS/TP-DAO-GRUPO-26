import tkinter as tk
from tkinter import ttk, messagebox
from Backend.DAO.FranjaHorariaDAO import FranjaHorariaDAO
from Backend.Model.FranjaHoraria import FranjaHoraria
import re # Importar módulo de expresiones regulares

class PanelHorarios(tk.Toplevel):
    """
    Esta ventana (Toplevel) permite gestionar (ver, agregar, eliminar)
    las franjas horarias de un médico específico.
    """
    
    def __init__(self, parent, id_medico, nombre_medico):
        super().__init__(parent)
        self.title(f"Gestionar Horarios de: {nombre_medico}")
        self.geometry("700x550") # Aumentar el tamaño de la ventana
        self.configure(bg="#333333") # Fondo oscuro para la ventana principal
        
        # Guardamos el ID del médico que estamos editando
        self.id_medico = id_medico
        self.dao = FranjaHorariaDAO()

        # --- Validación de entrada para HH:MM ---
        self.vcmd = (self.register(self._on_validate_time_input), '%P')

        # --- Widgets de Creación ---
        form_frame = tk.Frame(self, bg="#333333", padx=15, pady=15) # Usar tk.Frame y bg
        form_frame.pack(fill='x')

        tk.Label(form_frame, text="Días de la Semana (seleccione uno o varios):", bg="#333333", fg="white").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        # Usamos Listbox para permitir seleccionar varios días a la vez
        self.listbox_dias = tk.Listbox(form_frame, selectmode='multiple', height=7, exportselection=False)
        dias_vals = ["1 - Lunes", "2 - Martes", "3 - Miércoles", "4 - Jueves", "5 - Viernes", "6 - Sábado", "7 - Domingo"]
        for d in dias_vals:
            self.listbox_dias.insert(tk.END, d)
        self.listbox_dias.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(form_frame, text="Hora Inicio (HH:MM):", bg="#333333", fg="white").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_inicio = ttk.Entry(form_frame, width=15, validate="key", validatecommand=self.vcmd) # ttk.Entry para fondo blanco
        self.entry_inicio.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Hora Fin (HH:MM):", bg="#333333", fg="white").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_fin = ttk.Entry(form_frame, width=15, validate="key", validatecommand=self.vcmd) # ttk.Entry para fondo blanco
        self.entry_fin.grid(row=2, column=1, padx=5, pady=5)

        btn_agregar = ttk.Button(form_frame, text="Agregar Franja(s)", command=self.agregar_franja)
        btn_agregar.grid(row=3, column=1, padx=5, pady=10, sticky="e")
        btn_modificar = ttk.Button(form_frame, text="Modificar Franja Seleccionada", command=self.modificar_franja)
        btn_modificar.grid(row=3, column=0, padx=5, pady=10, sticky="w")

        # Botón "Eliminar Día" movido y posicionado con grid
        btn_eliminar_dia = ttk.Button(form_frame, text="Eliminar Día Seleccionado", command=self.eliminar_dia_seleccionado)
        btn_eliminar_dia.grid(row=4, column=0, padx=5, pady=10, sticky="w") # Nueva posición

        # --- Separador ---
        ttk.Separator(self, orient='horizontal').pack(fill='x', padx=10, pady=5)

        # --- TreeView para Mostrar Franjas Existentes ---
        list_frame = tk.Frame(self, bg="#333333", padx=15, pady=15) # Usar tk.Frame y bg
        list_frame.pack(fill='both', expand=True)
        
        tk.Label(list_frame, text="Horarios Laborales Programados:", bg="#333333", fg="white").pack(anchor="w")

        # Estilos para el Treeview (mantenerlos aquí para que no contaminen)
        style = ttk.Style()
        style.configure("Treeview", background="#DDDDDD", foreground="black", fieldbackground="#DDDDDD")
        style.configure("Treeview.Heading", background="#CCCCCC", foreground="black")

        self.tree = ttk.Treeview(list_frame, columns=("id", "dia", "inicio", "fin"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("dia", text="Día")
        self.tree.heading("inicio", text="Hora Inicio")
        self.tree.heading("fin", text="Hora Fin")
        
        # Definir ancho de columnas
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("dia", width=150)
        
        self.tree.pack(fill='both', expand=True, pady=10)

        # Cargar las franjas existentes al abrir la ventana
        self.cargar_franjas_existentes()

    def _on_validate_time_input(self, new_text):
        """
        Valida la entrada de texto en tiempo real para el formato HH:MM.
        Permite solo dígitos y un solo ':' en la posición correcta.
        """
        if not new_text: # Permitir campo vacío
            return True
        
        # Permitir solo dígitos y un solo ':'
        if not re.fullmatch(r'[\d:]*', new_text):
            return False
        
        # Limitar longitud a 5 (HH:MM)
        if len(new_text) > 5:
            return False
        
        # Asegurar que el ':' esté en la posición 2 si ya hay 3 caracteres
        if len(new_text) == 3 and new_text[2] != ':':
            # Si el usuario escribe 3er caracter y no es ':', lo insertamos
            self.after(1, lambda: self._insert_colon_if_needed(self.focus_get()))
            return True # Permitir la entrada para que el after pueda actuar
        
        return True

    def _insert_colon_if_needed(self, widget):
        """Inserta ':' automáticamente si el usuario escribió HH y el 3er caracter no es ':'."""
        current_text = widget.get()
        if len(current_text) == 2 and current_text.isdigit():
            widget.insert(tk.END, ':')
        elif len(current_text) == 3 and current_text[2].isdigit():
            # Si el usuario escribió HHX, donde X es un dígito, corregimos a HH:X
            widget.delete(2, tk.END)
            widget.insert(2, ':')
            widget.insert(3, current_text[2])
        
    def _validar_hora_completa(self, hora_str):
        """
        Valida que la cadena de hora tenga el formato HH:MM y que los valores sean válidos.
        Retorna True si es válida, False en caso contrario.
        """
        match = re.fullmatch(r'(\d{2}):(\d{2})', hora_str)
        if not match:
            return False
        
        horas = int(match.group(1))
        minutos = int(match.group(2))
        
        if not (0 <= horas <= 23 and 0 <= minutos <= 59):
            return False
            
        return True

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

        if not self._validar_hora_completa(inicio):
            messagebox.showerror("Error", "La 'Hora Inicio' no es válida. Use el formato HH:MM (ej. 08:00).", parent=self)
            return
        
        if not self._validar_hora_completa(fin):
            messagebox.showerror("Error", "La 'Hora Fin' no es válida. Use el formato HH:MM (ej. 14:30).", parent=self)
            return
        
        if inicio >= fin:
            messagebox.showerror("Error", "La hora de inicio debe ser anterior a la hora de fin.", parent=self)
            return

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
            resultado, msg = self.dao.insertar(nueva_franja) # Ahora el DAO devuelve (id, msg)
            if resultado:
                inserted_any = True
            else:
                errores.append(f"No se pudo insertar franja para {dia_text}: {msg}")

        if inserted_any:
            messagebox.showinfo("Éxito", "Franja(s) horaria(s) agregada(s) correctamente.", parent=self)
            self.cargar_franjas_existentes()
            self.entry_inicio.delete(0, tk.END)
            self.entry_fin.delete(0, tk.END)
            self.listbox_dias.selection_clear(0, tk.END)
        else:
            messagebox.showerror("Error", "No se pudieron agregar franjas. " + " ".join(errores), parent=self)

    def eliminar_dia_seleccionado(self): # Renombrado de eliminar_franja
        """Toma la franja seleccionada del TreeView y la elimina usando el DAO."""
        
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione una franja horaria de la lista para eliminar.", parent=self)
            return

        if not messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar esta franja horaria?", parent=self):
            return

        # Obtenemos el ID (el primer valor de la fila)
        id_franja_a_borrar = self.tree.item(selected_item[0])['values'][0]
        
        ok, msg = self.dao.eliminar(id_franja_a_borrar) # Ahora el DAO devuelve (ok, msg)
        if ok:
            messagebox.showinfo("Éxito", "Franja horaria eliminada.", parent=self)
            self.cargar_franjas_existentes() # Refrescar la lista
        else:
            messagebox.showerror("Error", f"No se pudo eliminar la franja: {msg}", parent=self)

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

        if not self._validar_hora_completa(inicio):
            messagebox.showerror("Error", "La 'Hora Inicio' no es válida. Use el formato HH:MM (ej. 08:00).", parent=self)
            return
        
        if not self._validar_hora_completa(fin):
            messagebox.showerror("Error", "La 'Hora Fin' no es válida. Use el formato HH:MM (ej. 14:30).", parent=self)
            return

        if inicio >= fin:
            messagebox.showerror("Error", "La hora de inicio debe ser anterior a la hora de fin.", parent=self)
            return

        # Validar que se haya seleccionado exactamente un día
        if len(selec_indices) != 1:
            messagebox.showerror("Error", "Seleccione correctamente el día que quiere modificar (solo un día).", parent=self)
            return

        # Validar que el día seleccionado coincida con el día de la franja en el TreeView
        dia_text_seleccionado = self.listbox_dias.get(selec_indices[0])
        try:
            dia_num_seleccionado = int(dia_text_seleccionado.split(" - ")[0])
        except ValueError:
            messagebox.showerror("Error", "Día inválido seleccionado.", parent=self)
            return
        
        dia_num_franja_tree = int(self.tree.item(selected_item[0])['values'][1].split(" - ")[0]) # Obtener el número del día de la franja en el TreeView

        if dia_num_seleccionado != dia_num_franja_tree:
            messagebox.showerror("Error", "El día seleccionado para modificar no coincide con el día de la franja horaria en la lista.", parent=self)
            return

        ok, msg = self.dao.actualizar(id_franja, dia_num_seleccionado, inicio, fin)
        if ok:
            messagebox.showinfo("Éxito", "Franja actualizada correctamente.", parent=self)
            self.cargar_franjas_existentes()
        else:
            messagebox.showerror("Error", f"No se pudo actualizar la franja: {msg}", parent=self)
