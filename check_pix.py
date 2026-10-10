import sqlite3
db = sqlite3.connect('livelo.db')
db.row_factory = sqlite3.Row
try:
    print(dict(db.execute("SELECT * FROM sys_config WHERE key='pix_key'").fetchone() or {}))
except Exception as e:
    print(e)
