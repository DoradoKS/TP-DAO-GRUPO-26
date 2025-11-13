import sqlite3
import pathlib

# --- 1. CONFIGURACIÓN ---
# Asumimos que el script está en la raíz
DB_PATH = pathlib.Path(__file__).parent / "Backend" / "BDD" / "clinica.db"

# --- 2. DATOS DE PRUEBA ---
# Lista de tuplas: (id_medico, dia_semana, hora_inicio, hora_fin)
franjas_a_cargar = [
    (2, 2, "10:00", "13:00"),  # Médico ID 2, Martes (Día 2), 10:00-13:00
    (3, 3, "14:00", "18:00")   # Médico ID 3, Miércoles (Día 3), 14:00-18:00
]

# --- 3. CONEXIÓN Y EJECUCIÓN ---
conn = None
try:
    print(f"Intentando conectar a: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Activar claves foráneas (¡importante!)
    cursor.execute("PRAGMA foreign_keys = ON;")

    sql = """
    INSERT INTO FranjaHoraria (id_medico, dia_semana, hora_inicio, hora_fin)
    VALUES (?, ?, ?, ?)
    """
    
    print("Insertando franjas de prueba...")
    # Usamos executemany para insertar múltiples filas
    cursor.executemany(sql, franjas_a_cargar)
    conn.commit()
    
    print(f"\n¡ÉXITO! Se agregaron {len(franjas_a_cargar)} franjas horarias.")
    print("  - Médico ID 2 (Martes 10-13)")
    print("  - Médico ID 3 (Miércoles 14-18)")

except sqlite3.IntegrityError:
    print(f"\n--- ERROR DE INTEGRIDAD ---")
    print(f"Asegurate de que los Médicos con ID 2 y 3 existan en la tabla 'Medico'.")
    print("Por favor, creá esos médicos desde la interfaz primero y volvé a correr este script.")
except sqlite3.Error as e:
    print(f"Error de SQL: {e}")
finally:
    if conn:
        conn.close()