import sqlite3

db = sqlite3.connect('livelo.db')
db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('telegram_token', '8930849062:AAFc6ehB5UU93c2w6N1DWIlOOwZOEFFllYU')")
db.commit()
print("Telegram token successfully updated in database.")
