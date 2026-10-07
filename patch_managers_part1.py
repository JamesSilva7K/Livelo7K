import sqlite3
from pathlib import Path

# 1. Update Database Schema
db_path = Path("livelo.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute('''
    CREATE TABLE IF NOT EXISTS managers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id TEXT UNIQUE NOT NULL,
        name TEXT,
        avatar_url TEXT,
        status TEXT DEFAULT 'active',
        created_at INTEGER
    )
''')
cur.execute('''
    CREATE TABLE IF NOT EXISTS manager_links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hash TEXT UNIQUE NOT NULL,
        telegram_id TEXT NOT NULL,
        access_code TEXT NOT NULL,
        used INTEGER DEFAULT 0,
        created_at INTEGER
    )
''')
conn.commit()
conn.close()
print("DB schema updated.")

# 2. Patch app.py to include new routes and DB init
app_file = Path("app.py")
content = app_file.read_text("utf-8")

if "CREATE TABLE IF NOT EXISTS managers" not in content:
    # Inject DB init
    init_db_patch = '''
    db.execute("""CREATE TABLE IF NOT EXISTS managers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id TEXT UNIQUE NOT NULL,
        name TEXT,
        avatar_url TEXT,
        status TEXT DEFAULT 'active',
        created_at INTEGER
    )""")
    db.execute("""CREATE TABLE IF NOT EXISTS manager_links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hash TEXT UNIQUE NOT NULL,
        telegram_id TEXT NOT NULL,
        access_code TEXT NOT NULL,
        used INTEGER DEFAULT 0,
        created_at INTEGER
    )""")
    '''
    content = content.replace('db.execute("""CREATE TABLE IF NOT EXISTS sys_config', init_db_patch + '\n    db.execute("""CREATE TABLE IF NOT EXISTS sys_config')

# Append new routes
new_routes = """
# ==========================================
# MANAGERS (NORMAL ADMINS) ROUTES
# ==========================================
import secrets
import time
import requests
from functools import wraps

def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('manager_token')
        if not token:
            return jsonify({"ok": False, "error": "Acesso Negado."}), 401
        db = get_db()
        mgr = db.execute("SELECT * FROM managers WHERE telegram_id = ? AND status='active'", (token,)).fetchone()
        if not mgr:
            return jsonify({"ok": False, "error": "Acesso Negado ou Bloqueado."}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route("/api/supreme/managers", methods=["GET", "POST", "DELETE", "PUT"])
@supreme_required
def api_manage_managers():
    db = get_db()
    if request.method == "GET":
        mgrs = db.execute("SELECT * FROM managers ORDER BY created_at DESC").fetchall()
        return jsonify({"ok": True, "managers": [dict(m) for m in mgrs]})
        
    if request.method == "POST":
        data = request.json
        tid = data.get("telegram_id")
        if not tid: return jsonify({"ok": False, "error": "Telegram ID obrigatório"})
        
        # Try to fetch Telegram Avatar and Name using Bot API
        bot_token = os.environ.get('BOT_TOKEN')
        name = "Gerente"
        avatar = "https://ui-avatars.com/api/?name=Gerente&background=random"
        if bot_token:
            try:
                # getChat
                chat_res = requests.get(f"https://api.telegram.org/bot{bot_token}/getChat?chat_id={tid}").json()
                if chat_res.get("ok"):
                    first_name = chat_res["result"].get("first_name", "")
                    last_name = chat_res["result"].get("last_name", "")
                    name = f"{first_name} {last_name}".strip() or "Gerente"
                    
                # getUserProfilePhotos
                photo_res = requests.get(f"https://api.telegram.org/bot{bot_token}/getUserProfilePhotos?user_id={tid}&limit=1").json()
                if photo_res.get("ok") and photo_res["result"]["total_count"] > 0:
                    file_id = photo_res["result"]["photos"][0][0]["file_id"]
                    file_res = requests.get(f"https://api.telegram.org/bot{bot_token}/getFile?file_id={file_id}").json()
                    if file_res.get("ok"):
                        file_path = file_res["result"]["file_path"]
                        avatar = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
            except Exception as e:
                pass
                
        try:
            db.execute("INSERT INTO managers (telegram_id, name, avatar_url, created_at) VALUES (?, ?, ?, ?)", (tid, name, avatar, int(time.time())))
            db.commit()
            return jsonify({"ok": True})
        except sqlite3.IntegrityError:
            return jsonify({"ok": False, "error": "Gerente já existe."})
            
    if request.method == "PUT":
        data = request.json
        tid = data.get("telegram_id")
        status = data.get("status")
        db.execute("UPDATE managers SET status = ? WHERE telegram_id = ?", (status, tid))
        db.commit()
        return jsonify({"ok": True})
        
    if request.method == "DELETE":
        data = request.json
        tid = data.get("telegram_id")
        db.execute("DELETE FROM managers WHERE telegram_id = ?", (tid,))
        db.execute("DELETE FROM manager_links WHERE telegram_id = ?", (tid,))
        db.commit()
        return jsonify({"ok": True})

@app.route("/api/supreme/manager_invite", methods=["POST"])
@supreme_required
def api_manager_invite():
    data = request.json
    tid = data.get("telegram_id")
    db = get_db()
    mgr = db.execute("SELECT * FROM managers WHERE telegram_id = ? AND status='active'", (tid,)).fetchone()
    if not mgr: return jsonify({"ok": False, "error": "Gerente não encontrado ou bloqueado."})
    
    link_hash = secrets.token_urlsafe(32)
    access_code = str(secrets.randbelow(900000) + 100000) # 6 digit code
    
    db.execute("INSERT INTO manager_links (hash, telegram_id, access_code, created_at) VALUES (?, ?, ?, ?)", (link_hash, tid, access_code, int(time.time())))
    db.commit()
    
    bot_token = os.environ.get('BOT_TOKEN')
    domain = request.host_url.rstrip('/')
    link = f"{domain}/nexus-manager/{link_hash}"
    
    msg = f"🔐 *Acesso Gerado*\n\nSeu link único e criptografado: {link}\n\nSeu código de acesso: `{access_code}`\n\n_Este link é de uso único._"
    
    if bot_token:
        try:
            requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={
                "chat_id": tid,
                "text": msg,
                "parse_mode": "Markdown"
            })
            return jsonify({"ok": True})
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)})
    return jsonify({"ok": False, "error": "Bot token não configurado."})

@app.route("/nexus-manager/<hash_str>", methods=["GET"])
def manager_view(hash_str):
    db = get_db()
    link = db.execute("SELECT * FROM manager_links WHERE hash = ?", (hash_str,)).fetchone()
    if not link or link['used']:
        return "Link inválido ou já utilizado.", 403
    return render_template("manager_dashboard.html", hash=hash_str)

@app.route("/api/manager/auth", methods=["POST"])
def manager_auth():
    data = request.json
    hash_str = data.get("hash")
    code = data.get("code")
    
    db = get_db()
    link = db.execute("SELECT * FROM manager_links WHERE hash = ? AND access_code = ?", (hash_str, code)).fetchone()
    if not link or link['used']:
        return jsonify({"ok": False, "error": "Código ou link inválido."}), 403
        
    db.execute("UPDATE manager_links SET used = 1 WHERE hash = ?", (hash_str,))
    db.commit()
    
    resp = jsonify({"ok": True})
    resp.set_cookie("manager_token", link['telegram_id'], httponly=True, samesite="Lax", max_age=43200) # 12 hours
    return resp

@app.route("/api/manager/dashboard", methods=["GET"])
@manager_required
def manager_dashboard_data():
    db = get_db()
    # Managers only see leads with payments approved or pending (who ordered cards)
    # The prompt says: "clientes que realizaram compra pedido do cartao completo e pagando o frete"
    recent_leads = db.execute("SELECT l.* FROM leads l JOIN payments p ON l.cpf = p.cpf WHERE p.status='approved' OR p.status='pago' OR p.status='pending' ORDER BY l.created_at DESC LIMIT 200").fetchall()
    return jsonify({"ok": True, "leads": [dict(l) for l in recent_leads]})
"""

if "api_manage_managers" not in content:
    app_file.write_text(content + "\n" + new_routes, "utf-8")
    print("app.py patched with manager routes.")
else:
    print("app.py already has manager routes.")
