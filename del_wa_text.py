import sqlite3
db = sqlite3.connect('livelo.db')
db.execute("DELETE FROM sys_config WHERE key='wa_text'")
db.commit()
db.close()
print("wa_text deleted")
