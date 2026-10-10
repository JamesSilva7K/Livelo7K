import time
import uuid
import json
import hmac
import hashlib
import requests

api_key = 'c7_live_44748a7a2531729b8f17c3e2f63fb037a0c67807d110ad1d3373bec47dc44b31'
api_secret = '45528e14d91b78dd3eacc10e3088dfb9fe351a79011981d9c0675e78d5663f41cfd61cff90a1a6c085788f6befe4b8781d950575640d249a98e149c8728e89b9'

ts = str(int(time.time()))
nonce = str(uuid.uuid4())
payload = {
    "amount": 10.50,
    "externalId": f"test_{int(time.time())}",
    "callbackUrl": "https://example.com/api/webhook/c7",
    "acquirer_code": "2"
}

body_str = json.dumps(payload, separators=(',', ':'), ensure_ascii=False)
msg = f"{ts}.{nonce}.{body_str}"
sig = hmac.new(api_secret.encode('utf-8'), msg.encode('utf-8'), hashlib.sha256).hexdigest()
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "X-C7-Timestamp": ts,
    "X-C7-Nonce": nonce,
    "X-C7-Signature": sig,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("Testing API carteirado7.com Adquirente 2...")
try:
    resp = requests.post("https://api.carteirado7.com/v2/payment/create", data=body_str.encode('utf-8'), headers=headers, timeout=10)
    print(f"Status Code: {resp.status_code}")
    print("Response JSON:")
    try:
        print(json.dumps(resp.json(), indent=2))
    except:
        print(resp.text)
except Exception as e:
    print(f"Error: {e}")
