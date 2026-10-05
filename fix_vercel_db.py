import os
with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

# Replace DB_PATH and UPLOAD_DIR
old_path_code = """# ── PATHS ──────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent
DB_PATH    = BASE_DIR / "livelo.db"
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)"""

new_path_code = """import shutil
# ── PATHS ──────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent
if os.environ.get("VERCEL"):
    DB_PATH = Path("/tmp/livelo.db")
    UPLOAD_DIR = Path("/tmp/uploads")
    # Copy db to tmp if not exists
    if not DB_PATH.exists() and (BASE_DIR / "livelo.db").exists():
        shutil.copy2(BASE_DIR / "livelo.db", DB_PATH)
else:
    DB_PATH    = BASE_DIR / "livelo.db"
    UPLOAD_DIR = BASE_DIR / "static" / "uploads"

try:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass"""

code = code.replace(old_path_code, new_path_code)

# Replace WAL mode because WAL doesn't work well sometimes on tmp / nfs
old_db_code = """        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")"""

new_db_code = """        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode=WAL")
        except Exception:
            pass"""

code = code.replace(old_db_code, new_db_code)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Vercel DB paths patched!")
