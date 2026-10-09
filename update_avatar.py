import sqlite3
conn = sqlite3.connect(r'd:\Paginas ADS\Livelo\livelo.db')
conn.execute("UPDATE manager SET photo_url='/static/images/Avatar_Gerente.png' WHERE id=1")
conn.commit()
conn.close()
