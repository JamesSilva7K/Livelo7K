import os
import re

APP_FILE = "d:/Paginas ADS/Livelo/app.py"
BOT_FILE = "d:/Paginas ADS/Livelo/bot.py"
HTML_FILE = "d:/Paginas ADS/Livelo/templates/supreme_admin.html"

# 1. UPDATE APP.PY
with open(APP_FILE, "r", encoding="utf-8") as f:
    app_code = f.read()

# Replace generate_otp
old_generate_otp = """    if action == "generate_otp":
        tg_id = str(payload.get("tg_id", ""))
        supreme_id = os.environ.get("ID_ADMIN_SUPREMO", os.environ.get("SUPREME_ADMIN_ID", os.environ.get("ADMIN_CHAT_ID", "none")))
        
        if tg_id == supreme_id:
            role = "supreme"
        else:
            mgr = db.execute("SELECT id FROM managers WHERE telegram_id = ?", (tg_id,)).fetchone()
            if not mgr:
                return {"ok": False, "error": "Acesso Negado: Você não é um gerente autorizado."}
            role = f"manager_{tg_id}"

        import random, string, hashlib, time
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        expires = time.time() + 300 # 5 minutes
        db.execute("INSERT INTO otp_tokens (token_hash, role, expires_at) VALUES (?, ?, ?)", (code_hash, role, expires))
        db.commit()
        return {"ok": True, "code": code}"""

new_generate_otp = """    if action == "generate_otp":
        tg_id = str(payload.get("tg_id", ""))
        supreme_id = os.environ.get("ID_ADMIN_SUPREMO", os.environ.get("SUPREME_ADMIN_ID", os.environ.get("ADMIN_CHAT_ID", "none")))
        
        if tg_id == supreme_id:
            role = "supreme"
        else:
            mgr = db.execute("SELECT id FROM managers WHERE telegram_id = ?", (tg_id,)).fetchone()
            if not mgr:
                return {"ok": False, "error": "Acesso Negado: Você não é um gerente autorizado."}
            role = f"manager_{tg_id}"

        import random, string, hashlib, time, uuid
        code = ''.join(random.choices(string.digits, k=6)) # 6-digit numeric PIN
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        expires = time.time() + 300 # 5 minutes
        port_id = str(uuid.uuid4().hex)[:12]
        
        # We ensure the port_id column exists
        try:
            db.execute("INSERT INTO otp_tokens (token_hash, role, expires_at, port_id) VALUES (?, ?, ?, ?)", (code_hash, role, expires, port_id))
        except:
            db.execute("INSERT INTO otp_tokens (token_hash, role, expires_at) VALUES (?, ?, ?)", (code_hash, role, expires))
        db.commit()
        
        url_path = f"/nexus-supreme/{port_id}" if role == "supreme" else f"/nexus-admin/{port_id}"
        return {"ok": True, "code": code, "url_path": url_path, "role": role}"""

app_code = app_code.replace(old_generate_otp, new_generate_otp)

# Replace the old fixed route with dynamic routes
old_route = """@app.route("/nexus-gate-9x02")
def supreme_admin_gate():
    db = get_db()
    if check_admin_lock(db):
        return render_template("supreme_admin.html", error="SISTEMA BLOQUEADO. O Administrador Supremo precisa liberar via Bot do Telegram usando /liberar.")
    return render_template("supreme_admin.html")"""

new_route = """@app.route("/nexus-supreme/<port_id>")
@app.route("/nexus-admin/<port_id>")
def supreme_admin_gate(port_id):
    db = get_db()
    if check_admin_lock(db):
        return render_template("supreme_admin.html", port_id=port_id, error="SISTEMA BLOQUEADO. O Administrador Supremo precisa liberar via Bot do Telegram usando /liberar.")
    
    # Check if port_id is valid in our DB (optional visual check, we still require PIN)
    try:
        otp = db.execute("SELECT role FROM otp_tokens WHERE port_id = ? AND used = 0", (port_id,)).fetchone()
        role_type = otp['role'] if otp else "unknown"
    except:
        role_type = "unknown"
        
    return render_template("supreme_admin.html", port_id=port_id, role_type=role_type)"""

app_code = app_code.replace(old_route, new_route)

# Replace the old /api/supreme/auth to use port_id
old_auth = """    # Check Intelligent OTP
    otp = db.execute("SELECT role FROM otp_tokens WHERE token_hash = ? AND used = 0 AND expires_at > ?", (pin_hash, time.time())).fetchone()"""

new_auth = """    port_id = data.get("port_id", "")
    # Check Intelligent OTP
    try:
        if port_id:
            otp = db.execute("SELECT role FROM otp_tokens WHERE token_hash = ? AND port_id = ? AND used = 0 AND expires_at > ?", (pin_hash, port_id, time.time())).fetchone()
        else:
            otp = db.execute("SELECT role FROM otp_tokens WHERE token_hash = ? AND used = 0 AND expires_at > ?", (pin_hash, time.time())).fetchone()
    except:
        otp = db.execute("SELECT role FROM otp_tokens WHERE token_hash = ? AND used = 0 AND expires_at > ?", (pin_hash, time.time())).fetchone()
"""
app_code = app_code.replace(old_auth, new_auth)

with open(APP_FILE, "w", encoding="utf-8") as f:
    f.write(app_code)


# 2. UPDATE BOT.PY
with open(BOT_FILE, "r", encoding="utf-8") as f:
    bot_code = f.read()

old_bot_code = """    if res.get("ok"):
        txt = (
            "🔐 <b>ACESSO AO PAINEL BLINDADO</b>\\n\\n"
            f"🔗 <b>URL:</b> {BASE_URL}/nexus-gate-9x02\\n"
            f"🔑 <b>Código Dinâmico (OTP):</b> <code>{res['code']}</code>\\n\\n"
            "<i>Válido por 5 minutos. Uso único.</i>\\n"
            "<i>Cuidado: Se errar o código 3 vezes o sistema será bloqueado por segurança!</i>"
        )
        bot.reply_to(message, txt)"""

new_bot_code = """    if res.get("ok"):
        url_path = res.get("url_path", "/nexus-gate-9x02")
        role_name = "SUPREMO" if res.get("role") == "supreme" else "GERENTE"
        txt = (
            f"🔐 <b>ACESSO AO PAINEL BLINDADO ({role_name})</b>\\n\\n"
            f"🔗 <b>URL Única:</b> {BASE_URL}{url_path}\\n"
            f"🔑 <b>PIN Dinâmico (OTP):</b> <code>{res['code']}</code>\\n\\n"
            "<i>Válido por 5 minutos. Uso único.</i>\\n"
            "<i>Cuidado: Se errar o PIN 3 vezes o sistema será bloqueado por segurança!</i>"
        )
        bot.reply_to(message, txt)"""

bot_code = bot_code.replace(old_bot_code, new_bot_code)

old_fallback = """            txt = (
                "🔐 <b>ACESSO AO PAINEL SUPREMO (Fallback)</b>\\n\\n"
                f"🔗 <b>URL:</b> {BASE_URL}/nexus-gate-9x02\\n"
                f"🔑 <b>PIN de Acesso:</b> <code>{pin}</code>\\n\\n"
                "<i>Cuidado: Se errar o PIN 3 vezes o sistema será bloqueado por segurança!</i>"
            )"""

new_fallback = """            txt = (
                "🔐 <b>ACESSO AO PAINEL SUPREMO (Fallback)</b>\\n\\n"
                f"🔗 <b>URL:</b> {BASE_URL}/nexus-supreme/fallback\\n"
                f"🔑 <b>PIN de Acesso:</b> <code>{pin}</code>\\n\\n"
                "<i>Cuidado: Se errar o PIN 3 vezes o sistema será bloqueado por segurança!</i>"
            )"""

bot_code = bot_code.replace(old_fallback, new_fallback)

with open(BOT_FILE, "w", encoding="utf-8") as f:
    f.write(bot_code)

print("Backend updated.")
