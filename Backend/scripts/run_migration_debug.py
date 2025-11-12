import sqlite3
from pathlib import Path
DB_PATH = Path(__file__).parent.parent / 'BDD' / 'clinica.db'
print('DB:', DB_PATH)
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
print('Before PRAGMA table_info:')
c.execute('PRAGMA table_info(Usuario);')
cols = c.fetchall()
print(cols)
cols_names = [r[1] for r in cols]
print('col names:', cols_names)
if 'contrasenia' in cols_names:
    print('already has contrasenia')
elif 'contrasea' in cols_names:
    print('will migrate contrasea -> contrasenia')
    try:
        c.execute('PRAGMA foreign_keys = OFF;')
        c.execute('BEGIN;')
        c.execute('''CREATE TABLE IF NOT EXISTS Usuario_new (
                        usuario TEXT PRIMARY KEY,
                        contrasenia TEXT NOT NULL,
                        rol TEXT NOT NULL
                    );''')
        c.execute("INSERT INTO Usuario_new (usuario, contrasenia, rol) SELECT usuario, contrasea, rol FROM Usuario;")
        c.execute("DROP TABLE Usuario;")
        c.execute("ALTER TABLE Usuario_new RENAME TO Usuario;")
        c.execute('COMMIT;')
        print('migration commit')
    except Exception as e:
        c.execute('ROLLBACK;')
        print('migration error', e)
    finally:
        c.execute('PRAGMA foreign_keys = ON;')
else:
    print('neither column present')

c.execute('PRAGMA table_info(Usuario);')
print('After:', c.fetchall())
conn.close()

