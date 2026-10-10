import time
import uuid
import json
import hmac
import hashlib
import requests

# ─── Credenciais novas (10/10/2026) ───────────────────────────────────────────
api_key    = 'c7_live_886a0ddc60040fc340191da87d875c0d73e2acbbbea79a534c0782a23b11be0d'
api_secret = '6df27379be2618bae4c69bff936e062472493b0e4427191229a1f44327c3949ce9738bc1825f721fc49472231e9b39a8ab62cde958a15a387101874218790ea6'
BASE = "https://api.carteirado7.com/v2"

def sign(body_str: str) -> dict:
    ts    = str(int(time.time()))
    nonce = str(uuid.uuid4())
    msg   = f"{ts}.{nonce}.{body_str}"
    sig   = hmac.new(api_secret.encode(), msg.encode(), hashlib.sha256).hexdigest()
    return {
        "Authorization":  f"Bearer {api_key}",
        "Content-Type":   "application/json",
        "X-C7-Timestamp": ts,
        "X-C7-Nonce":     nonce,
        "X-C7-Signature": sig,
        "User-Agent":     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"
    }


# ── 1. Saldo ──────────────────────────────────────────────────────────────────
print("\n══ SALDO DA CONTA ══")
try:
    body = "{}"
    resp = requests.post(f"{BASE}/account/balance", data=body.encode(), headers=sign(body), timeout=10)
    print(f"Status: {resp.status_code}")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Erro: {e}")


# ── 2. Criar PIX (testa adquirentes 2 → 1 → auto) ────────────────────────────
for acq in ["2", "1", ""]:
    label = acq if acq else "Auto"
    print(f"\n══ CRIAR PIX — Adquirente {label} ══")
    payload = {
        "amount": 10.50,
        "externalId": f"test_{int(time.time())}_{label}",
        "callbackUrl": "https://example.com/api/webhook/c7",
    }
    if acq:
        payload["acquirer_code"] = acq

    body_str = json.dumps(payload, separators=(',', ':'), ensure_ascii=False)
    try:
        resp = requests.post(f"{BASE}/payment/create", data=body_str.encode(), headers=sign(body_str), timeout=10)
        print(f"Status: {resp.status_code}")
        print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
        if resp.status_code in (200, 201) and resp.json().get("ok"):
            print(f"✅ Adquirente {label} funcionou — parando aqui.")
            break
    except Exception as e:
        print(f"Erro: {e}")
    time.sleep(1)  # cooldown entre tentativas

