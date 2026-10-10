import sqlite3

db = sqlite3.connect('livelo.db')

# Insert C7 API credentials
db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('c7_api_key', 'c7_live_72f859fc4305ea84808d8ce66c1abacdeec35dd2db948525d8fff7690490d7fe')")
db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('c7_api_secret', 'd45b57c3af06581f6a211363a47be0d311520b3b73f11a581d660086f3332b5d8ed849b329a47a587dec09aaa3290c2a2901380aa42b6910ce89f46f3015f7b9')")

# Insert Token Interno (maybe for bot or other integration)
db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('bot_secret', '9bd3434165fd220dfcd17259ba07ce6b')")

db.commit()
print("Credentials successfully updated in database.")
