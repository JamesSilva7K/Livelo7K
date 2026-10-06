import re

app_path = "app.py"
with open(app_path, "r", encoding="utf-8") as f:
    app_code = f.read()

# Locate the end of send_telegram_report and the start of the orphaned DB update block
target = """    except Exception as e:
        pass
        
    db = get_db()

    existing = db.execute("SELECT id FROM leads WHERE session_id=?", (sid,)).fetchone()"""

replacement = """    except Exception as e:
        pass

# ── API LEAD (RECUPERADO) ─────────────────────────────────────────────────────
@app.route("/api/lead", methods=["POST"])
def api_lead():
    data = get_secure_json()
    sid = sanitize(data.get("session_id", ""), 40)
    if not sid: return jsonify({"error": "Sessão inválida"}), 400
    
    cpf = sanitize(data.get("cpf", ""), 14)
    nome = sanitize(data.get("nome", ""), 100)
    nome_mae = sanitize(data.get("nome_mae", ""), 100)
    data_nasc = sanitize(data.get("data_nasc", ""), 10)
    renda = sanitize(data.get("renda", ""), 30)
    tipo_renda = sanitize(data.get("tipo_renda", ""), 50)
    motivo = sanitize(data.get("motivo_credito", ""), 50)
    dia_venc = sanitize(data.get("dia_vencimento", ""), 10)
    
    utm_source = sanitize(data.get("utm_source", ""), 100)
    utm_medium = sanitize(data.get("utm_medium", ""), 100)
    utm_campaign = sanitize(data.get("utm_campaign", ""), 100)
    utm_content = sanitize(data.get("utm_content", ""), 100)
    utm_term = sanitize(data.get("utm_term", ""), 100)
    src = sanitize(data.get("src", ""), 100)
    sck = sanitize(data.get("sck", ""), 100)
    
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    client_loc = "BR"
    
    analise = calc_limite(renda, tipo_renda, motivo)
    limite = analise["limite"]
    frete = analise["frete"]

    db = get_db()

    existing = db.execute("SELECT id FROM leads WHERE session_id=?", (sid,)).fetchone()"""

if target in app_code:
    app_code = app_code.replace(target, replacement)
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(app_code)
    print("API LEAD route restored!")
else:
    print("Target block not found in app.py. Please verify manually.")
