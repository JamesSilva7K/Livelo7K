import sqlite3
conn = sqlite3.connect(r'd:\Paginas ADS\Livelo\livelo.db')
conn.execute("UPDATE manager SET name='Lucas Cardoso' WHERE id=1 AND name='Gerente Livelo'")
conn.commit()
conn.close()
