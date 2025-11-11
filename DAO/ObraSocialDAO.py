import sqlite3
# En DAO/ObraSocialDAO.py

from Backend.BDD.Conexion import get_conexion
from Backend.Model.ObraSocial import ObraSocial # Importa el modelo que acabamos de crear

class ObraSocialDAO:
    """
    DAO para la entidad ObraSocial.
    Por ahora, solo implementamos la lectura de datos.
    """

    def obtener_todas(self):
        """
        Retorna una lista de todas las obras sociales como objetos.
        """
        conn = None
        obras_sociales = []
        try:
            conn = get_conexion()
            cursor = conn.cursor()

            sql = "SELECT * FROM ObraSocial ORDER BY nombre"
            cursor.execute(sql)
            filas = cursor.fetchall()

            for fila in filas:
                os = ObraSocial(
                    id_obra_social=fila[0], 
                    nombre=fila[1]
                )
                obras_sociales.append(os)
            
            return obras_sociales

        except sqlite3.Error as e:
            print(f"Error al obtener todas las Obras Sociales: {e}")
            return []
        finally:
            if conn:
                conn.close()

    # --- Opcional: ABM Completo ---
    # Si quisieras un ABM completo, aquí agregarías:
    # def crear_obra_social(self, nombre):
    # def actualizar_obra_social(self, obra_social):
    # def eliminar_obra_social(self, id_obra_social):
    #
    # Pero por ahora, no es necesario para la funcionalidad principal.