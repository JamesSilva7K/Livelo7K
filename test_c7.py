import sqlite3, os, hmac, hashlib, time, uuid, json, requests

def test_c7():
    db = sqlite3.connect('livelo.db')
    db.row_factory = sqlite3.Row
    row_key = db.execute("SELECT value FROM sys_config WHERE key='c7_api_key'").fetchone()
    api_key = row_key['value'] if row_key else None
    row_sec = db.execute("SELECT value FROM sys_config WHERE key='c7_api_secret'").fetchone()
    api_secret = row_sec['value'] if row_sec else None
    if not api_key: return
        
    ts = str(int(time.time()))
    nonce = str(uuid.uuid4())
    payload = {
        'amount': 29.90, 
        'callbackUrl': 'https://livelocartaolimite.vercel.app/api/webhook/c7',
        'externalId': 'TEST_'+str(int(time.time())),
        'acquirer_code': '1',
        'payerName': 'Joao Silva',
        'payerDocument': '14887154674'
    }
    body_str = json.dumps(payload, separators=(',', ':'))
    msg = f'{ts}.{nonce}.{body_str}'
    sig = hmac.new(api_secret.encode('utf-8'), msg.encode('utf-8'), hashlib.sha256).hexdigest()
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'X-C7-Timestamp': ts,
        'X-C7-Nonce': nonce,
        'X-C7-Signature': sig,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    print("Sending C7 Request...")
    try:
        resp = requests.post('https://api.carteirado7.com/v2/payment/create', data=body_str, headers=headers, timeout=10)
        print('C7 STATUS:', resp.status_code)
        print('C7 BODY:', resp.text[:300])
    except Exception as e:
        print('C7 EXCEPTION:', str(e))

if __name__ == '__main__':
    test_c7()


