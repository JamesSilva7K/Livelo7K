import os
import sqlite3
import shutil

# Backup current DB
if os.path.exists("livelo.db"):
    shutil.copy2("livelo.db", "livelo.db.bak")
    # Also grab other configs
    old_db = sqlite3.connect("livelo.db")
    old_configs = old_db.execute("SELECT key, value FROM sys_config").fetchall()
    old_db.close()
    os.remove("livelo.db")
else:
    old_configs = []

from app import init_db
init_db()

new_db = sqlite3.connect("livelo.db")

# Insert all old configs back
for k, v in old_configs:
    new_db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES (?, ?)", (k, v))

# Force update the C7 API keys just in case they were missing
new_db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('c7_api_key', 'c7_live_44748a7a2531729b8f17c3e2f63fb037a0c67807d110ad1d3373bec47dc44b31')")
new_db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('c7_api_secret', '45528e14d91b78dd3eacc10e3088dfb9fe351a79011981d9c0675e78d5663f41cfd61cff90a1a6c085788f6befe4b8781d950575640d249a98e149c8728e89b9')")
new_db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('c7_best_acquirer', '2')")

# Create default admin if missing
admin = new_db.execute("SELECT * FROM admin").fetchone()
if not admin:
    from werkzeug.security import generate_password_hash
    new_db.execute("INSERT INTO admin (username, password) VALUES ('admin', ?)", (generate_password_hash("admin"),))

new_db.commit()
new_db.close()
print("Database rebuilt successfully with correct API keys!")
