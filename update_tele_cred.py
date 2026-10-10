import sqlite3

db = sqlite3.connect('livelo.db')
db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('telegram_token', '8730410378:AAExcQJupyktePYfiWcBX4C7FTf_LuuvBhM')")
db.commit()
print("Telegram token successfully updated in database.")
