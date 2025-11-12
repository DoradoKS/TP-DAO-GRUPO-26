import sys
import os
import pathlib

# --- Configuración de la Ruta del Proyecto ---
ROOT_DIR = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from Backend.GUI.welcome import WelcomeScreen

if __name__ == "__main__":
    print("Iniciando la Interfaz Gráfica...")
    app = WelcomeScreen()
    app.mainloop()
