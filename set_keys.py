import sqlite3
db = sqlite3.connect('livelo.db')
c = db.cursor()

def set_config(key, value):
    c.execute("SELECT key FROM sys_config WHERE key=?", (key,))
    row = c.fetchone()
    if row:
        c.execute("UPDATE sys_config SET value=? WHERE key=?", (value, key))
    else:
        c.execute("INSERT INTO sys_config (key, value) VALUES (?, ?)", (key, value))

set_config('c7_api_key', 'c7_live_cdbd8be1a34c09a4488233ea72e798a16ba4e54962e50b39cf1b77b1df48b5c7')
set_config('c7_api_secret', '9c602a1b01239a89541024b17a605942104bb944ebb46366b8fec04fb1550678bd26a7df640a63e5d08c0d83bb7e87db635fa4c5486d45714fa7c88a49cb4886')

db.commit()
db.close()
print("Credenciais gravadas no SQLite com sucesso!")
