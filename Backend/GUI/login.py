import tkinter as tk
from tkinter import ttk, messagebox
from Backend.DAO.UsuarioDAO import UsuarioDAO
from Backend.GUI.main import MainMenu

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login")
        
        window_width = 400
        window_height = 250
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        
        pos_x = center_x - 50
        pos_y = center_y - 50
        
        self.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")

        self.create_widgets()
        # self.usuario_entry.focus_set() # Eliminamos la llamada directa
        self.after(100, self.usuario_entry.focus_set) # Retrasamos el focus_set
        self.focus_force() # Forzar el foco a esta ventana

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        ttk.Label(main_frame, text="Usuario:", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=10, sticky="e")
        self.usuario_entry = ttk.Entry(main_frame, font=("Arial", 12))
        self.usuario_entry.grid(row=0, column=1, padx=5, pady=10, sticky="w")

        ttk.Label(main_frame, text="Contraseña:", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=10, sticky="e")
        self.password_entry = ttk.Entry(main_frame, show="*", font=("Arial", 12))
        self.password_entry.grid(row=1, column=1, padx=5, pady=10, sticky="w")

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        login_button = ttk.Button(button_frame, text="Login", command=self.login)
        login_button.pack()

        self.bind('<Return>', self.login_event)
        self.usuario_entry.bind('<Return>', self.login_event)
        self.password_entry.bind('<Return>', self.login_event)

    def login_event(self, event=None):
        self.login()

    def login(self):
        usuario = self.usuario_entry.get()
        password = self.password_entry.get()

        if not usuario or not password:
            messagebox.showerror("Error", "Usuario y contraseña son requeridos.")
            return

        usuario_dao = UsuarioDAO()
        rol = usuario_dao.autenticar_usuario(usuario, password)
        
        if rol:
            self.destroy()
            app = MainMenu(rol, usuario)
            app.mainloop()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
