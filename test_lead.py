import requests
import json

STATE = {
  "sessionId": "test-session-123",
  "cpf": "68600010008",
  "nome": "Test",
  "nome_mae": "Test Mae",
  "data_nasc": "01/01/2000",
  "renda": "1000",
  "tipo_renda": "CLT",
  "dia_vencimento": "10",
  "color": "gradient_pink",
  "style": "standard",
  "managerWa": "5511999999999",
  "paymentId": None,
  "pixCode": None
}

r1 = requests.post("http://127.0.0.1:5050/api/cpf", json={"cpf": "68600010008", "data_nasc": "01/01/2000"})
print("/api/cpf:", r1.status_code, r1.text)

r2 = requests.post("http://127.0.0.1:5050/api/lead", json=STATE)
print("/api/lead:", r2.status_code, r2.text)
