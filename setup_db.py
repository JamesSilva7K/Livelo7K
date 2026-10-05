import sqlite3
import os

db_path = r"d:\Paginas ADS\Livelo\database.db"

def init_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Table for Global Configs
    c.execute('''
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    # Table for Admins (Supreme and Normal)
    c.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT UNIQUE,
            name TEXT,
            avatar_url TEXT,
            role TEXT DEFAULT 'admin', -- 'admin' or 'supreme'
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table for Leads
    c.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cpf TEXT,
            name TEXT,
            income TEXT,
            limit_approved TEXT,
            card_name TEXT,
            card_number TEXT,
            address TEXT,
            shipping_method TEXT,
            shipping_price TEXT,
            whatsapp TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table for Payments
    c.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            amount REAL,
            status TEXT DEFAULT 'PENDING', -- PENDING, APPROVED, REJECTED
            c7_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(lead_id) REFERENCES leads(id)
        )
    ''')
    
    # Insert default config
    defaults = {
        'manager_name': 'Juliana Benedito',
        'manager_avatar': '/static/images/manager.jpg',
        'manager_badge': 'Melhor gerente 2023-2024',
        'manager_whatsapp': '',
        'log_channel_id': '',
        'system_logo': '/static/images/logo.png'
    }
    for k, v in defaults.items():
        c.execute('INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)', (k, v))
        
    conn.commit()
    conn.close()
    print("Database Initialized successfully.")

if __name__ == "__main__":
    init_db()
