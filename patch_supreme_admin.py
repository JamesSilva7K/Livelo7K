import sqlite3
import os
import hashlib
from pathlib import Path
import re

app_file = Path("app.py")
content = app_file.read_text("utf-8")

# 1. Update DB Schema
if "device_brand TEXT" not in content:
    content = content.replace(
        "            updated_at      REAL    NOT NULL DEFAULT (cast(strftime('%s','now') as real))\n        );",
        "            updated_at      REAL    NOT NULL DEFAULT (cast(strftime('%s','now') as real)),\n            location        TEXT,\n            device_brand    TEXT\n        );"
    )

if "ALTER TABLE leads ADD COLUMN device_brand" not in content:
    content = content.replace(
        "db.executescript(\"\"\"",
        "db.executescript(\"\"\"\n        -- Migrations\n        ALTER TABLE leads ADD COLUMN location TEXT;\n        ALTER TABLE leads ADD COLUMN device_brand TEXT;\n        "
    )
    # Ignore errors if columns already exist
    content = content.replace(
        "db.executescript(\"\"\"",
        "try:\n            db.execute(\"ALTER TABLE leads ADD COLUMN location TEXT\")\n        except:\n            pass\n        try:\n            db.execute(\"ALTER TABLE leads ADD COLUMN device_brand TEXT\")\n        except:\n            pass\n\n        db.executescript(\"\"\""
    )

# 2. Capture Device & Location in /api/lead
# Find where location is captured
if "client_loc =" not in content:
    pass # Wait, let's just parse User-Agent
    
import_user_agents_str = """
    # Capture Device Brand
    ua = request.headers.get("User-Agent", "").lower()
    device_brand = "Outro"
    if "iphone" in ua or "ipad" in ua or "macintosh" in ua: device_brand = "Apple"
    elif "samsung" in ua: device_brand = "Samsung"
    elif "motorola" in ua: device_brand = "Motorola"
    elif "xiaomi" in ua or "redmi" in ua or "poco" in ua: device_brand = "Xiaomi"
    elif "android" in ua: device_brand = "Android Generico"
    elif "windows" in ua: device_brand = "Windows PC"
    
    # Capture Location via Cloudflare headers
    client_loc = request.headers.get("CF-IPRegion", "") + " - " + request.headers.get("CF-IPCountry", "BR")
    if client_loc == " - BR": client_loc = "Desconhecido"
"""

if "device_brand = \"Outro\"" not in content:
    content = content.replace(
        "client_ip = request.headers.get('CF-Connecting-IP', request.remote_addr)",
        "client_ip = request.headers.get('CF-Connecting-IP', request.remote_addr)\n" + import_user_agents_str
    )
    # Also update INSERT into leads
    content = content.replace(
        "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    )
    content = content.replace(
        "(sid, client_ip, cpf, nome, nome_mae, data_nasc, renda, tipo_renda, motivo, dia_venc, limite,\n              utm_source, utm_medium, utm_campaign, utm_content, utm_term, src, sck, client_loc))",
        "(sid, client_ip, cpf, nome, nome_mae, data_nasc, renda, tipo_renda, motivo, dia_venc, limite,\n              utm_source, utm_medium, utm_campaign, utm_content, utm_term, src, sck, client_loc, device_brand))"
    )
    content = content.replace(
        "src,sck,location)",
        "src,sck,location,device_brand)"
    )

# 3. Add Supreme Admin Routes
supreme_routes = """
# ══════════════════════════════════════════════════════════════════════════════
#  SUPREME ADMIN SHIELDED GATES
# ══════════════════════════════════════════════════════════════════════════════
SUPREME_HASH = "8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92" # SHA-256 for '123456'

def get_supreme_hash():
    # If LO sets SUPREME_PIN in Vercel, use it. Otherwise use the default 123456 hash.
    pin = os.environ.get("SUPREME_PIN")
    if pin:
        import hashlib
        return hashlib.sha256(pin.encode()).hexdigest()
    return SUPREME_HASH

def supreme_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        token = request.cookies.get("supreme_token")
        if not token or token != get_supreme_hash():
            return jsonify({"ok": False, "error": "Acesso Negado. Blindagem Ativa."}), 403
        return f(*args, **kwargs)
    return wrapped

@app.route("/nexus-gate-9x02")
def supreme_admin_gate():
    return render_template("supreme_admin.html")

@app.route("/api/supreme/auth", methods=["POST"])
def supreme_auth():
    data = get_secure_json()
    pin = str(data.get("pin", ""))
    
    # Rate Limiting against Bruteforce
    ip = request.headers.get("CF-Connecting-IP", request.remote_addr)
    if is_blocked(ip):
        return jsonify({"ok": False, "error": "IP Bloqueado por brute-force."}), 429
        
    import hashlib
    pin_hash = hashlib.sha256(pin.encode()).hexdigest()
    
    if pin_hash == get_supreme_hash():
        reset_auth_fail(ip)
        resp = jsonify({"ok": True})
        # Set Secure Cookie
        resp.set_cookie("supreme_token", pin_hash, httponly=True, samesite="Lax", max_age=86400)
        return resp
    else:
        record_auth_fail(ip)
        return jsonify({"ok": False, "error": "PIN Incorreto."}), 401

@app.route("/api/supreme/dashboard", methods=["GET"])
@supreme_required
def supreme_dashboard():
    db = get_db()
    
    leads_count = db.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    pagos = db.execute("SELECT SUM(amount), COUNT(*) FROM payments WHERE status='approved' OR status='pago'").fetchone()
    pendentes = db.execute("SELECT COUNT(*) FROM payments WHERE status='pending'").fetchone()[0]
    
    cartoes_emitidos = db.execute("SELECT COUNT(*) FROM leads WHERE card_style IS NOT NULL AND card_style != ''").fetchone()[0]
    
    # Region Stats
    regions_raw = db.execute("SELECT location, COUNT(*) as c FROM leads WHERE location IS NOT NULL AND location != 'Desconhecido' GROUP BY location ORDER BY c DESC LIMIT 5").fetchall()
    regions = [{"name": r["location"], "count": r["c"]} for r in regions_raw]
    
    # Device Stats
    devices_raw = db.execute("SELECT device_brand, COUNT(*) as c FROM leads WHERE device_brand IS NOT NULL GROUP BY device_brand ORDER BY c DESC").fetchall()
    devices = [{"name": d["device_brand"], "count": d["c"]} for d in devices_raw]
    
    # Recent Leads Detailed
    recent_leads = db.execute("SELECT nome, cpf, whatsapp, card_style, card_color, location, device_brand, limite_aprovado, pix_status, created_at FROM leads ORDER BY created_at DESC LIMIT 20").fetchall()
    
    stats = {
        "entradas": leads_count,
        "cartoes": cartoes_emitidos,
        "receita": round(pagos[0] or 0, 2),
        "pagos_qtd": pagos[1] or 0,
        "pendentes": pendentes,
        "regions": regions,
        "devices": devices,
        "leads": [dict(l) for l in recent_leads]
    }
    
    return jsonify({"ok": True, "stats": stats})

"""

if "supreme_admin_gate" not in content:
    content = content.replace(
        "@app.errorhandler(404)",
        supreme_routes + "\n@app.errorhandler(404)"
    )

app_file.write_text(content, "utf-8")
print("App patched successfully!")
