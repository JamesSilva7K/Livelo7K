import sqlite3
c = sqlite3.connect('livelo.db')
c.execute("INSERT OR IGNORE INTO sys_config (key, value) VALUES ('cpf_api_token', 'd0442b7d42e2a762f64a02f5e4abc1187ad6585cb3e9c11740c4024961aa1026')")
c.execute("INSERT OR IGNORE INTO sys_config (key, value) VALUES ('cpf_api_calls', '0')")
c.commit()
