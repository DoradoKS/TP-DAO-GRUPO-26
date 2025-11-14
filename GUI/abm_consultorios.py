import tkinter as tk
from tkinter import ttk, messagebox
from Backend.DAO.ConsultorioDAO import ConsultorioDAO
from Backend.Model.Consultorio import Consultorio
from .alta_consultorio import AltaConsultorio

class GestionConsultorios(tk.Toplevel):
    def __init__(self, parent, usuario="admin"):
        super().__init__(parent)
        self.title("Gestión de Consultorios")
        self.geometry("700x500")
        self.configure(bg="#333333")
        self.usuario = usuario

        self.selected_id = None
        self.entries = {}

        self.create_widgets()
        self.cargar_consultorios()

    def create_widgets(self):
        main = tk.Frame(self, bg="#333333"); main.pack(expand=True, fill="both")
        
        form = tk.LabelFrame(main, text="Consultorio Seleccionado", bg="#333333", fg="white", padx=10, pady=10)
        form.pack(padx=10, pady=10, fill="x")
        tk.Label(form, text="Descripción:", bg="#333333", fg="white").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entries["Descripcion"] = ttk.Entry(form, width=50)
        self.entries["Descripcion"].grid(row=0, column=1, padx=5, pady=5, sticky="w")

        btns = tk.Frame(main, bg="#333333"); btns.pack(padx=10, pady=5, fill="x")
        
        ttk.Button(btns, text="Guardar Modificación", command=self.guardar_modificacion).pack(side="left", padx=5)
        ttk.Button(btns, text="Eliminar", command=self.eliminar).pack(side="left", padx=5)
        ttk.Button(btns, text="Nuevo Consultorio", command=self.abrir_alta).pack(side="right", padx=5)

        tf = tk.Frame(main, bg="#333333"); tf.pack(padx=10, pady=10, fill="both", expand=True)
        
        style = ttk.Style()
        style.configure("Treeview", background="#DDDDDD", foreground="black", fieldbackground="#DDDDDD")
        style.configure("Treeview.Heading", background="#CCCCCC", foreground="black")

        self.tree = ttk.Treeview(tf, columns=("id","descripcion"), show="headings")
        self.tree.heading("id", text="ID"); self.tree.heading("descripcion", text="Descripción")
        self.tree.column("id", width=80, anchor="center")
        self.tree.pack(fill="both", expand=True, side="left")
        sc = ttk.Scrollbar(tf, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sc.set); sc.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def cargar_consultorios(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for c in ConsultorioDAO().obtener_todos():
            self.tree.insert("", "end", values=(c.id_consultorio, c.descripcion))
        self.limpiar_campos()

    def on_select(self, _):
        sel = self.tree.selection();
        if not sel: return
        item = self.tree.item(sel[0])
        self.selected_id = item["values"][0]
        self.entries["Descripcion"].delete(0, tk.END)
        self.entries["Descripcion"].insert(0, item["values"][1])

    def limpiar_campos(self):
        self.selected_id = None
        self.entries["Descripcion"].delete(0, tk.END)
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection()[0])

    def abrir_alta(self):
        AltaConsultorio(self, self.usuario).grab_set()

    def guardar_modificacion(self):
        descripcion = self.entries["Descripcion"].get().strip()
        if not self.selected_id:
            messagebox.showwarning("Atención", "Seleccione un consultorio de la lista para modificar.")
            return
        if not descripcion:
            messagebox.showerror("Error", "La descripción es obligatoria.")
            return
            
        dao = ConsultorioDAO()
        ok, msg = dao.actualizar_consultorio(Consultorio(id_consultorio=self.selected_id, descripcion=descripcion), self.usuario)
        
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.cargar_consultorios()
        else:
            messagebox.showerror("Error", msg)

    def eliminar(self):
        if not self.selected_id:
            messagebox.showwarning("Atención", "Seleccione un consultorio de la lista.")
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar el consultorio seleccionado?"):
            return
            
        ok, mensaje = ConsultorioDAO().eliminar_consultorio(self.selected_id, self.usuario)
        if ok:
            messagebox.showinfo("Éxito", mensaje)
            self.cargar_consultorios()
        else:
            messagebox.showerror("Error", mensaje)
