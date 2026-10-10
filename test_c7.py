import sqlite3, os, hmac, hashlib, time, uuid, json, requests
from dotenv import load_dotenv

def test_c7():
    load_dotenv()
    api_key = os.environ.get("C7_API_KEY")
    api_secret = os.environ.get("C7_API_SECRET")
    
    print(f"Loaded KEY from .env: {api_key[:15]}...")
    
    db = sqlite3.connect('livelo.db')
    db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('c7_api_key', ?)", (api_key,))
    db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('c7_api_secret', ?)", (api_secret,))
    db.commit()

    if not api_key: return

    for acq in ['1', '2', '']:
        ts = str(int(time.time()))
        nonce = str(uuid.uuid4())
        payload = {
            'amount': 29.90,
            'callbackUrl': 'https://livelocartaolimite.vercel.app/api/webhook/c7',
            'externalId': 'TEST_'+str(int(time.time())),
            'payerName': 'Joao Silva',
            'payerDocument': '14887154674'
        }
        if acq:
            payload['acquirer_code'] = acq

        body_str = json.dumps(payload, separators=(',', ':'))
        msg = f'{ts}.{nonce}.{body_str}'
        sig = hmac.new(api_secret.encode('utf-8'), msg.encode('utf-8'), hashlib.sha256).hexdigest()
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'X-C7-Timestamp': ts,
            'X-C7-Nonce': nonce,
            'X-C7-Signature': sig,
            'User-Agent': 'Mozilla/5.0'
        }
        print(f"\n--- Testing Acquirer '{acq}' ---")
        try:
            resp = requests.post('https://api.carteirado7.com/v2/payment/create', data=body_str, headers=headers, timeout=10)
            print('C7 STATUS:', resp.status_code)
            print('C7 BODY:', resp.text[:300])
        except Exception as e:
            print('C7 EXCEPTION:', str(e))

if __name__ == '__main__':
    test_c7()
