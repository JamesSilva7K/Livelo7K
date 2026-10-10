import requests
import sqlite3

def test():
    cpf_val = "15905049769"
    db = sqlite3.connect('livelo.db')
    db.row_factory = sqlite3.Row
    token_row = db.execute("SELECT value FROM sys_config WHERE key='cpf_api_token' OR key='cpf_token' ORDER BY key ASC LIMIT 1").fetchone()
    cpf_token = token_row["value"] if token_row and token_row["value"] else "3019c16c241c14fdd68dc4389ae48b2e1322c5435671ef18a633b206aa70293b"
    
    headers = {"x-api-key": cpf_token, "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    resp = requests.get(f"https://api.cpfhub.io/cpf/{cpf_val}", headers=headers, timeout=10)
    print(resp.status_code)
    print(resp.text)

test()
