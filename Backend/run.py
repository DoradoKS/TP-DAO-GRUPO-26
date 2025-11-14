import sys
import pathlib

# --- Configuración de la Ruta del Proyecto ---
ROOT_DIR = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from GUI.welcome import WelcomeScreen
from Backend.notifications import start_scheduler

if __name__ == "__main__":
    print("Iniciando la Interfaz Gráfica...")
    # Iniciamos el scheduler de notificaciones en background (cada 1 minuto para pruebas)
    try:
        start_scheduler(1)
    except Exception as e:
        print(f"No se pudo iniciar el scheduler de notificaciones: {e}")
    app = WelcomeScreen()
    app.mainloop()
