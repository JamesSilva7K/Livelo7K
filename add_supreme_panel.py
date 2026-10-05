import re

# 1. Update app.py
with open(r'd:\Paginas ADS\Livelo\app.py', 'r', encoding='utf-8') as f:
    app_code = f.read()

# Make lookup_cpf use sys_config for token
cpf_func_old = """        try:
            import requests
            token = "219648175aXyEcieuSW396568120"
            url = f"https://ws.hubdodesenvolvedor.com.br/v2/cadastropf/?cpf={cpf}&token={token}" """

cpf_func_new = """        try:
            import requests
            db = get_db()
            row = db.execute("SELECT value FROM sys_config WHERE key='cpf_token'").fetchone()
            token = row["value"] if row else "219648175aXyEcieuSW396568120"
            url = f"https://ws.hubdodesenvolvedor.com.br/v2/cadastropf/?cpf={cpf}&token={token}" """

app_code = app_code.replace(cpf_func_old, cpf_func_new)

# Update /api/tg_admin_update_settings to save cpf_token
update_settings_old = """    whatsapp = data.get("whatsapp")
    
    db = get_db()"""

update_settings_new = """    whatsapp = data.get("whatsapp")
    cpf_token = data.get("cpf_token")
    
    db = get_db()
    if cpf_token is not None:
        db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('cpf_token', ?)", (cpf_token,))"""

app_code = app_code.replace(update_settings_old, update_settings_new)

# Update /api/tg_webapp/data to return cpf_token so the frontend can populate it
# Wait, the route is /api/tg_webapp/data or something similar?
# Let's find how stats are sent. Oh, it's /api/tg_webapp/data or the /tg_webapp endpoint just renders it. 
# There's a route that returns stats. Let's look for 'def ' below '/api/tg_admin_update_settings'.
# Actually, the user logs in via /api/tg_auth. We can return it there.
tg_auth_old = """        "leads": leads,
        "frete_atual": frete_atual,
        "mgr_whatsapp": mgr_whatsapp"""

tg_auth_new = """        "leads": leads,
        "frete_atual": frete_atual,
        "mgr_whatsapp": mgr_whatsapp,
        "cpf_token": db.execute("SELECT value FROM sys_config WHERE key='cpf_token'").fetchone()["value"] if db.execute("SELECT value FROM sys_config WHERE key='cpf_token'").fetchone() else "219648175aXyEcieuSW396568120\""""

# Let's use regex to inject it into the return jsonify({ ... }) of the stats route.
app_code = re.sub(
    r'("mgr_whatsapp": mgr_whatsapp\n\s*})\)',
    r'"mgr_whatsapp": mgr_whatsapp,\n        "cpf_token": db.execute("SELECT value FROM sys_config WHERE key=\'cpf_token\'").fetchone()["value"] if db.execute("SELECT value FROM sys_config WHERE key=\'cpf_token\'").fetchone() else ""\n    })',
    app_code
)


with open(r'd:\Paginas ADS\Livelo\app.py', 'w', encoding='utf-8') as f:
    f.write(app_code)


# 2. Update tg_webapp.html
with open(r'd:\Paginas ADS\Livelo\templates\tg_webapp.html', 'r', encoding='utf-8') as f:
    tg_code = f.read()

# Add Token input
config_box_old = """        <div class="config-row">
          <div class="config-label"><svg class="icon" style="color:#25D366"><use href="#ic-whatsapp"></use></svg> WhatsApp Suporte</div>
          <input type="text" id="cfg-wa" class="config-input" placeholder="5511999999999">
        </div>
        <button class="btn-save" onclick="saveConfigs()">Salvar Configurações</button>"""

config_box_new = """        <div class="config-row">
          <div class="config-label"><svg class="icon" style="color:#25D366"><use href="#ic-whatsapp"></use></svg> WhatsApp Suporte</div>
          <input type="text" id="cfg-wa" class="config-input" placeholder="5511999999999">
        </div>
        <div class="config-row">
          <div class="config-label">🔑 Token API CPF</div>
          <input type="text" id="cfg-cpf-token" class="config-input" placeholder="Token da Hub...">
        </div>
        <button class="btn-save" onclick="saveConfigs()">Salvar Configurações</button>"""

tg_code = tg_code.replace(config_box_old, config_box_new)

# Update saveConfigs
save_old = """    async function saveConfigs() {
      const frete = document.getElementById('cfg-frete').value;
      const wa = document.getElementById('cfg-wa').value;
      tg.HapticFeedback.impactOccurred('light');
      
      try {
        const res = await fetch('/api/tg_admin_update_settings', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({ supreme_id: SUPREME_ID, freight_price: frete, whatsapp: wa })"""

save_new = """    async function saveConfigs() {
      const frete = document.getElementById('cfg-frete').value;
      const wa = document.getElementById('cfg-wa').value;
      const cpf_token = document.getElementById('cfg-cpf-token').value;
      tg.HapticFeedback.impactOccurred('light');
      
      try {
        const res = await fetch('/api/tg_admin_update_settings', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({ supreme_id: SUPREME_ID, freight_price: frete, whatsapp: wa, cpf_token: cpf_token })"""

tg_code = tg_code.replace(save_old, save_new)

# Populate values (assuming data.cpf_token is returned)
populate_old = """          document.getElementById('cfg-frete').value = data.frete_atual || "";
          document.getElementById('cfg-wa').value = data.mgr_whatsapp || "";"""

populate_new = """          document.getElementById('cfg-frete').value = data.frete_atual || "";
          document.getElementById('cfg-wa').value = data.mgr_whatsapp || "";
          if(data.cpf_token) document.getElementById('cfg-cpf-token').value = data.cpf_token;"""

tg_code = tg_code.replace(populate_old, populate_new)

with open(r'd:\Paginas ADS\Livelo\templates\tg_webapp.html', 'w', encoding='utf-8') as f:
    f.write(tg_code)

print("Painel Supremo Atualizado!")
