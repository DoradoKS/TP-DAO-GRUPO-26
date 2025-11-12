import tkinter as tk
from tkinter import ttk
from Backend.BDD.Conexion import inicializar_bdd
from Backend.DAO.UsuarioDAO import UsuarioDAO
from Backend.Model.Usuario import Usuario
from Backend.GUI.login import LoginWindow

class WelcomeScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        
        window_width = 450
        window_height = 450
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        
        pos_x = center_x - 50
        pos_y = center_y - 50
        
        self.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")

        self.progress = None
        self.log_frame = None

        self.create_widgets()
        self.after(500, self.run_setup_tasks)

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(main_frame, width=100, height=100, bg=self.cget('bg'), highlightthickness=0)
        canvas.pack(pady=20)
        self.draw_red_cross(canvas)
        
        ttk.Label(main_frame, text="Iniciando Sistema...", font=("Arial", 16)).pack(pady=10)
        
        self.progress = ttk.Progressbar(main_frame, orient="horizontal", length=350, mode="determinate")
        self.progress.pack(pady=10)

        self.log_frame = tk.Frame(main_frame)
        self.log_frame.pack(pady=10, fill="x", padx=20)

    def draw_red_cross(self, canvas):
        canvas.create_rectangle(35, 10, 65, 90, fill="red", outline="")
        canvas.create_rectangle(10, 35, 90, 65, fill="red", outline="")

    def add_log_message(self, text, color="black"):
        log_label = tk.Label(self.log_frame, text=text, fg=color, font=("Arial", 10))
        log_label.pack(anchor="w")
        self.update_idletasks()
        return log_label

    def run_setup_tasks(self):
        tasks = [
            ("Inicializando base de datos...", self.setup_database),
            ("Verificando usuario administrador...", self.create_admin_user)
        ]
        self.after(200, lambda: self.execute_task(tasks, 0))

    def execute_task(self, tasks, task_index):
        if task_index >= len(tasks):
            self.progress['value'] = 100
            self.add_log_message("✓ ¡Todo listo!", "green")
            self.after(1200, self.open_login)
            return

        initial_message, task_function = tasks[task_index]
        log_label = self.add_log_message(initial_message)
        
        self.progress['value'] = ((task_index + 1) / len(tasks)) * 90
        
        success, message = task_function()
        
        if success:
            log_label.config(text=f"✓ {message}", fg="green")
        else:
            log_label.config(text=f"✗ Error: {message}", fg="red")
            return

        self.after(500, lambda: self.execute_task(tasks, task_index + 1))

    def setup_database(self):
        try:
            inicializar_bdd()
            return True, "Base de datos inicializada."
        except Exception as e:
            return False, str(e)

    def create_admin_user(self):
        try:
            usuario_dao = UsuarioDAO()
            if not usuario_dao.obtener_usuario("admin"):
                admin = Usuario(usuario="admin", contrasenia="admin", rol="Administrador")
                usuario_dao.crear_usuario(admin)
                return True, "Usuario 'admin' creado."
            else:
                return True, "Usuario 'admin' ya existe."
        except Exception as e:
            return False, str(e)

    def open_login(self):
        self.destroy()
        LoginWindow().mainloop()
