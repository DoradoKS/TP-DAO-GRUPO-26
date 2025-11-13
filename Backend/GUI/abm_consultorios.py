import tkinter as tk
from tkinter import ttk, messagebox
from Backend.DAO.ConsultorioDAO import ConsultorioDAO
from Backend.Model.Consultorio import Consultorio

class GestionConsultorios(tk.Toplevel):
    def __init__(self, parent, usuario="admin"):
        super().__init__(parent)
        self.title("Gestión de Consultorios")
        self.geometry("700x500")
        self.configure(bg="#333333")
        self.usuario = usuario

        self.entries = {}
        self.selected_id = None

        self.create_widgets()
        self.cargar_consultorios()

    def create_widgets(self):
        main_frame = tk.Frame(self, bg="#333333")
        main_frame.pack(expand=True, fill="both")

        form_frame = tk.LabelFrame(main_frame, text="Consultorio", bg="#333333", fg="white", padx=10, pady=10)
        form_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(form_frame, text="Descripción:", bg="#333333", fg="white").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entries["Descripcion"] = ttk.Entry(form_frame, width=50)
        self.entries["Descripcion"].grid(row=0, column=1, padx=5, pady=5, sticky="w")

        btns = tk.Frame(main_frame, bg="#333333")
        btns.pack(padx=10, pady=5, fill="x")
        ttk.Button(btns, text="Nuevo", command=self.nuevo).pack(side="left", padx=5)
        ttk.Button(btns, text="Guardar", command=self.guardar).pack(side="left", padx=5)
        ttk.Button(btns, text="Eliminar", command=self.eliminar).pack(side="left", padx=5)

        tree_frame = tk.Frame(main_frame, bg="#333333")
        tree_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.tree = ttk.Treeview(tree_frame, columns=("id","descripcion"), show="headings")
        self.tree.heading("id", text="ID"); self.tree.heading("descripcion", text="Descripción")
        self.tree.column("id", width=80, anchor="center")
        self.tree.pack(fill="both", expand=True, side="left")
        scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def cargar_consultorios(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for c in ConsultorioDAO().obtener_todos():
            self.tree.insert("", "end", values=(c.id_consultorio, c.descripcion))

    def on_select(self, _):
        sel = self.tree.selection()
        if not sel: return
        item = self.tree.item(sel[0])
        self.selected_id = item["values"][0]
        self.entries["Descripcion"].delete(0, tk.END)
        self.entries["Descripcion"].insert(0, item["values"][1])

    def nuevo(self):
        self.selected_id = None
        self.entries["Descripcion"].delete(0, tk.END)

    def guardar(self):
        desc = self.entries["Descripcion"].get().strip()
        if not desc:
            messagebox.showerror("Error", "La descripción es obligatoria.")
            return
        dao = ConsultorioDAO()
        if self.selected_id:
            ok, msg = dao.actualizar_consultorio(Consultorio(id_consultorio=self.selected_id, descripcion=desc), self.usuario)
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.cargar_consultorios()
            else:
                messagebox.showerror("Error", msg)
        else:
            _id, msg = dao.crear_consultorio(Consultorio(descripcion=desc), self.usuario)
            if _id:
                messagebox.showinfo("Éxito", msg)
                self.cargar_consultorios()
            else:
                messagebox.showerror("Error", msg)

    def eliminar(self):
        if not self.selected_id:
            messagebox.showwarning("Atención", "Seleccione un consultorio.")
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar consultorio seleccionado?"):
            return
        ok, msg = ConsultorioDAO().eliminar_consultorio(self.selected_id, self.usuario)
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.cargar_consultorios()
            self.nuevo()
        else:
            messagebox.showerror("Error", msg)
