import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'BDD' / 'clinica.db'
print('Usando DB:', DB_PATH)
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
print('\nPRAGMA table_info(Usuario):')
try:
    c.execute("PRAGMA table_info(Usuario);")
    cols = c.fetchall()
    if not cols:
        print('La tabla Usuario no existe o está vacía.')
    for col in cols:
        # Col schema: (cid, name, type, notnull, dflt_value, pk)
        print(col)

    print('\nPRAGMA foreign_key_list(Usuario):')
    try:
        c.execute("PRAGMA foreign_key_list(Usuario);")
        fks = c.fetchall()
        for fk in fks:
            print(fk)
    except Exception as e:
        print('No se pudo obtener foreign_key_list:', e)
except Exception as e:
    print('Error al consultar la base de datos:', e)
finally:
    conn.close()

