import os, requests

def test_cpf():
    print("Sending CPFHub Request...")
    # Read from .env
    env_key = None
    if os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('CPFHUB_API_KEY='):
                    env_key = line.strip().split('=', 1)[1]
    
    if not env_key:
        print("No CPFHUB_API_KEY found in .env")
        return
        
    cpf = '14887154674'
    headers = {"x-api-key": env_key}
    try:
        resp = requests.get(f"https://api.cpfhub.io/cpf/{cpf}", headers=headers, timeout=10)
        print('CPF STATUS:', resp.status_code)
        print('CPF BODY:', resp.text[:300])
    except Exception as e:
        print('CPF EXCEPTION:', str(e))

if __name__ == '__main__':
    test_cpf()
