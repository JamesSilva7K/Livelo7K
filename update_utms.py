import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "livelo.db"

def alter_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    columns = ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "src", "sck"]
    
    for col in columns:
        try:
            cursor.execute(f"ALTER TABLE leads ADD COLUMN {col} TEXT")
            print(f"Added column {col}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"Column {col} already exists")
            else:
                print(f"Error adding {col}: {e}")
                
    conn.commit()
    conn.close()

if __name__ == "__main__":
    alter_db()
