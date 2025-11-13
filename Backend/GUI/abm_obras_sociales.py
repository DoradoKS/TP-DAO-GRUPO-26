import tkinter as tk
from tkinter import ttk, messagebox
from Backend.DAO.ObraSocialDAO import ObraSocialDAO
from Backend.Model.ObraSocial import ObraSocial
from .alta_obra_social import AltaObraSocial

class GestionObrasSociales(tk.Toplevel):
    def __init__(self, parent, usuario="admin"):
        super().__init__(parent)
        self.title("Gestión de Obras Sociales")
        self.geometry("700x500")
        self.configure(bg="#333333")
        self.usuario = usuario

        self.selected_id = None
        self.entries = {}

        self.create_widgets()
        self.cargar_obras_sociales()

    def create_widgets(self):
        main = tk.Frame(self, bg="#333333"); main.pack(expand=True, fill="both")
        
        form = tk.LabelFrame(main, text="Obra Social Seleccionada", bg="#333333", fg="white", padx=10, pady=10)
        form.pack(padx=10, pady=10, fill="x")
        tk.Label(form, text="Nombre:", bg="#333333", fg="white").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entries["Nombre"] = ttk.Entry(form, width=50)
        self.entries["Nombre"].grid(row=0, column=1, padx=5, pady=5, sticky="w")

        btns = tk.Frame(main, bg="#333333"); btns.pack(padx=10, pady=5, fill="x")
        
        ttk.Button(btns, text="Guardar Modificación", command=self.guardar_modificacion).pack(side="left", padx=5)
        ttk.Button(btns, text="Eliminar", command=self.eliminar).pack(side="left", padx=5)
        ttk.Button(btns, text="Nueva Obra Social", command=self.abrir_alta).pack(side="right", padx=5)

        tf = tk.Frame(main, bg="#333333"); tf.pack(padx=10, pady=10, fill="both", expand=True)
        
        style = ttk.Style()
        style.configure("Treeview", background="#DDDDDD", foreground="black", fieldbackground="#DDDDDD")
        style.configure("Treeview.Heading", background="#CCCCCC", foreground="black")

        self.tree = ttk.Treeview(tf, columns=("id","nombre"), show="headings")
        self.tree.heading("id", text="ID"); self.tree.heading("nombre", text="Nombre")
        self.tree.column("id", width=80, anchor="center")
        self.tree.pack(fill="both", expand=True, side="left")
        sc = ttk.Scrollbar(tf, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sc.set); sc.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def cargar_obras_sociales(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for o in ObraSocialDAO().obtener_obra_social():
            self.tree.insert("", "end", values=(o.id_obra_social, o.nombre))
        self.limpiar_campos()

    def on_select(self, _):
        sel = self.tree.selection();
        if not sel: return
        item = self.tree.item(sel[0])
        self.selected_id = item["values"][0]
        self.entries["Nombre"].delete(0, tk.END)
        self.entries["Nombre"].insert(0, item["values"][1])

    def limpiar_campos(self):
        self.selected_id = None
        self.entries["Nombre"].delete(0, tk.END)
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection()[0])

    def abrir_alta(self):
        AltaObraSocial(self, self.usuario).grab_set()

    def guardar_modificacion(self):
        nombre = self.entries["Nombre"].get().strip()
        if not self.selected_id:
            messagebox.showwarning("Atención", "Seleccione una Obra Social de la lista para modificar.")
            return
        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio.")
            return
            
        dao = ObraSocialDAO()
        ok, msg = dao.actualizar_obra_social(ObraSocial(id_obra_social=self.selected_id, nombre=nombre), self.usuario)
        
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.cargar_obras_sociales()
        else:
            messagebox.showerror("Error", msg)

    def eliminar(self):
        if not self.selected_id:
            messagebox.showwarning("Atención", "Seleccione una Obra Social de la lista.")
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar la Obra Social seleccionada?"):
            return
            
        ok, mensaje = ObraSocialDAO().eliminar_obra_social(self.selected_id, self.usuario)
        if ok:
            messagebox.showinfo("Éxito", mensaje)
            self.cargar_obras_sociales()
        else:
            messagebox.showerror("Error", mensaje)
