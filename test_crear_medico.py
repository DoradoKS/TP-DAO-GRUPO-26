"""
Script de prueba rápida para verificar creación de médico con usuario.
Ejecutar desde la raíz del proyecto.
"""
import sys
import pathlib

ROOT_DIR = pathlib.Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from Backend.DAO.UsuarioDAO import UsuarioDAO
from Backend.DAO.MedicoDAO import MedicoDAO
from Backend.DAO.EspecialidadDAO import EspecialidadDAO
from Backend.Model.Medico import Medico

def test_crear_medico():
    print("=== Test: Crear Médico ===")
    
    # 1. Obtener una especialidad existente (o crear si no existe)
    esp_dao = EspecialidadDAO()
    especialidades = esp_dao.obtener_todas_las_especialidades()
    
    if not especialidades:
        print("No hay especialidades en la BD. Crea al menos una antes de probar.")
        return
    
    id_especialidad = especialidades[0].id_especialidad
    print(f"✓ Usando especialidad: {especialidades[0].nombre} (ID: {id_especialidad})")
    
    # 2. Crear usuario de prueba
    usuario_test = "test.medico"
    contraseña_test = "pass123"
    
    usuario_dao = UsuarioDAO()
    creado, msg = usuario_dao.crear_usuario(usuario_test, contraseña_test, "Medico")
    
    if creado:
        print(f"✓ Usuario creado: {usuario_test}")
    else:
        print(f"⚠ Usuario ya existe o error: {msg}")
    
    # 3. Crear médico
    medico_test = Medico(
        usuario=usuario_test,
        nombre="Dr. Test",
        apellido="Prueba",
        matricula="MP9999",
        tipo_dni="DNI",
        dni="99999999",
        email="test@test.com",
        telefono="123456789",
        id_especialidad=id_especialidad,
        calle="Calle Test",
        numero_calle=100
    )
    
    medico_dao = MedicoDAO()
    id_creado, mensaje = medico_dao.crear_medico(medico_test, "admin")
    
    if id_creado:
        print(f"✓ Médico creado exitosamente (ID: {id_creado})")
        print(f"  Mensaje: {mensaje}")
    else:
        print(f"✗ Error al crear médico: {mensaje}")
    
    print("\n=== Fin del Test ===")

if __name__ == "__main__":
    test_crear_medico()
