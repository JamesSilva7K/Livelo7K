import sqlite3

db = sqlite3.connect('livelo.db')
db.execute("UPDATE sys_config SET value='c7_live_44748a7a2531729b8f17c3e2f63fb037a0c67807d110ad1d3373bec47dc44b31' WHERE key='c7_api_key'")
db.execute("UPDATE sys_config SET value='45528e14d91b78dd3eacc10e3088dfb9fe351a79011981d9c0675e78d5663f41cfd61cff90a1a6c085788f6befe4b8781d950575640d249a98e149c8728e89b9' WHERE key='c7_api_secret'")
db.execute("DELETE FROM sys_config WHERE key='c7_api_status'")
db.commit()
db.close()
print("Done!")
