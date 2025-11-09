# --- test.py ---
# Archivo en la carpeta RAÍZ del proyecto

import datetime
from DAO.PacienteDAO import PacienteDAO
from Model.Paciente import Paciente
from DAO.MedicoDAO import MedicoDAO  # <-- NUEVA IMPORTACIÓN
from Model.Medico import Medico      # <-- NUEVA IMPORTACIÓN
from DAO.ObraSocialDAO import ObraSocialDAO

# --- PRUEBAS PACIENTE DAO (Las dejamos) ---
print("=============================================")
print("====== 🏥 INICIANDO PRUEBAS PACIENTE 🏥 ======")
print("=============================================")
dao_paciente = PacienteDAO()

print("\n--- 1. PROBANDO OBTENER TODOS LOS PACIENTES ---")
lista_pacientes = dao_paciente.obtener_todos_los_pacientes()
if lista_pacientes:
    for p in lista_pacientes:
        print(p)
else:
    print("No se encontraron pacientes.")

print("\n--- 2. PROBANDO OBTENER PACIENTE POR DNI ---")
paciente_encontrado = dao_paciente.obtener_paciente_por_dni('35123456')
if paciente_encontrado:
    print(f"Paciente encontrado: {paciente_encontrado}")
else:
    print("Paciente con DNI 35123456 no encontrado.")

print("\n--- 3. PROBANDO CREAR UN NUEVO PACIENTE ---")
# (Usamos el usuario 'testpaciente' que ya creamos)
nuevo_paciente = Paciente(
    id_paciente=None, id_barrio=1, usuario='testpaciente',
    nombre='Laura', apellido='Mendez',
    fecha_nacimiento=datetime.date(1995, 10, 22),
    tipo_dni=1, dni='40111222', email='lauram@mail.com',
    telefono='351987654', id_obra_social=3,
    calle='Calle Falsa', numero_calle=123
)
# Primero verificamos si ya existe (por si el test falló y no se borró)
paciente_existente = dao_paciente.obtener_paciente_por_dni('40111222')
if not paciente_existente:
    nuevo_id_paciente = dao_paciente.crear_paciente(nuevo_paciente)
    if nuevo_id_paciente:
        print(f"¡Paciente nuevo creado con ID: {nuevo_id_paciente}!")
        nuevo_paciente.id_paciente = nuevo_id_paciente
    else:
        print("ERROR al crear el paciente.")
else:
    print("El paciente de prueba ('40111222') ya existe, se omite creación.")
    nuevo_id_paciente = paciente_existente.id_paciente
    nuevo_paciente = paciente_existente


print("\n--- 4. PROBANDO ACTUALIZAR EL PACIENTE CREADO ---")
if nuevo_id_paciente:
    nuevo_paciente.telefono = '55554444' # Nuevo tel para la prueba
    nuevo_paciente.calle = 'Calle Actualizada'
    
    if dao_paciente.actualizar_paciente(nuevo_paciente):
        print(f"Paciente con ID {nuevo_id_paciente} actualizado.")
    else:
        print(f"ERROR al actualizar paciente con ID {nuevo_id_paciente}.")
else:
    print("No se puede probar la actualización, la creación falló.")


print("\n--- 5. PROBANDO ELIMINAR EL PACIENTE CREADO ---")
if nuevo_id_paciente:
    if dao_paciente.eliminar_paciente(nuevo_id_paciente):
        print(f"Paciente con ID {nuevo_id_paciente} eliminado.")
    else:
        print(f"ERROR al eliminar paciente con ID {nuevo_id_paciente}.")
else:
    print("No se puede probar la eliminación, la creación falló.")


# --- ================================== ---
# ---     NUEVAS PRUEBAS MEDICO DAO      ---
# --- ================================== ---

print("\n\n=============================================")
print("====== 👨‍⚕️ INICIANDO PRUEBAS MEDICO 👨‍⚕️ ======")
print("=============================================")

dao_medico = MedicoDAO()

print("\n--- 1. PROBANDO OBTENER TODOS LOS MEDICOS ---")
lista_medicos = dao_medico.obtener_todos_los_medicos()
if lista_medicos:
    for m in lista_medicos:
        print(m)
else:
    print("No se encontraron médicos.")

print("\n--- 2. PROBANDO OBTENER MEDICO POR MATRICULA ---")
# Probamos buscar uno que SÍ existe (según los datos de prueba)
mat_a_buscar = 12345 # Dra. Ana Gomez
medico_encontrado = dao_medico.obtener_medico_por_matricula(mat_a_buscar)
if medico_encontrado:
    print(f"Médico encontrado: {medico_encontrado}")
else:
    print(f"Médico con Matrícula {mat_a_buscar} no encontrado.")

# Probamos buscar uno que NO existe
mat_falsa = 999
medico_falso = dao_medico.obtener_medico_por_matricula(mat_falsa)
if medico_falso:
    print(f"ERROR: Se encontró un médico que no existe: {medico_falso}")
else:
    print(f"CORRECTO: Médico con Matrícula {mat_falsa} no encontrado.")


print("\n--- 3. PROBANDO CREAR UN NUEVO MEDICO ---")
# Creamos un objeto Medico nuevo
# Usamos el usuario 'drmartinez' que acabamos de agregar
# Asegúrate de que id_especialidad = 3 (Traumatología) exista
nuevo_medico = Medico(
    id_medico=None,
    usuario='drmartinez',       # (FK 1 - ¡DEBE EXISTIR!)
    matricula=98765,            # Matrícula Única
    nombre='Roberto',
    apellido='Martinez',
    tipo_dni=1,                 # (FK 2 - 'DNI')
    dni='30555666',             # DNI Único
    calle='Av. Colon',
    numero_calle=1020,
    email='rmartinez@mail.com',
    telefono='351122334',
    id_especialidad=3           # (FK 3 - 'Traumatología')
)

# Verificamos si ya existe (por si el test falló y no se borró)
medico_existente = dao_medico.obtener_medico_por_matricula(98765)
if not medico_existente:
    nuevo_id_medico = dao_medico.crear_medico(nuevo_medico)
    if nuevo_id_medico:
        print(f"¡Médico nuevo creado con ID: {nuevo_id_medico}!")
        nuevo_medico.id_medico = nuevo_id_medico
    else:
        print("ERROR al crear el médico.")
else:
    print("El médico de prueba (Mat. 98765) ya existe, se omite creación.")
    nuevo_id_medico = medico_existente.id_medico
    nuevo_medico = medico_existente


print("\n--- 4. PROBANDO ACTUALIZAR EL MEDICO CREADO ---")
if nuevo_id_medico:
    nuevo_medico.telefono = '00000000' # Cambiamos el teléfono
    nuevo_medico.email = 'nuevo_email@mail.com' # Cambiamos el email
    
    if dao_medico.actualizar_medico(nuevo_medico):
        print(f"Médico con ID {nuevo_id_medico} actualizado correctamente.")
        # Verificamos
        medico_actualizado = dao_medico.obtener_medico_por_matricula(98765)
        print(f"Datos actualizados: {medico_actualizado.telefono} y {medico_actualizado.email}")
    else:
        print(f"ERROR al actualizar médico con ID {nuevo_id_medico}.")
else:
    print("No se puede probar la actualización, la creación falló.")


print("\n--- 5. PROBANDO ELIMINAR EL MEDICO CREADO ---")
if nuevo_id_medico:
    if dao_medico.eliminar_medico(nuevo_id_medico):
        print(f"Médico con ID {nuevo_id_medico} eliminado correctamente.")
        # Verificamos que ya no exista
        medico_eliminado = dao_medico.obtener_medico_por_matricula(98765)
        if not medico_eliminado:
            print("CORRECTO: El médico ya no se encuentra en la DB.")
        else:
            print("ERROR: El médico no se eliminó correctamente.")
    else:
        print(f"ERROR al eliminar médico con ID {nuevo_id_medico}.")
else:
    print("No se puede probar la eliminación, la creación falló.")

print("\n\n=============================================")
print("====== 📋 INICIANDO PRUEBAS CATALOGOS 📋 =====")
print("=============================================")

print("\n--- 1. PROBANDO OBTENER TODAS LAS OBRAS SOCIALES ---")
dao_obras = ObraSocialDAO()
lista_os = dao_obras.obtener_todas()
if lista_os:
    for os in lista_os:
        print(os)
else:
    print("No se encontraron Obras Sociales.")