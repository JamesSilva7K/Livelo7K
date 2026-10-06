import re
import os

app_path = "app.py"
admin_html_path = "templates/admin_dashboard.html"
index_html_path = "templates/index.html"
main_js_path = "static/js/main.js"

# 1. Update app.py
with open(app_path, "r", encoding="utf-8") as f:
    app_code = f.read()

# Add new tables/columns if not exist, we can just alter table on startup or rely on dynamic config
# Wait, manager table: id, name, cpf, phone, photo_url, freight_price, whatsapp, etc.
# Actually, let's use sys_config for all these new dynamic things:
# 'mgr_name', 'mgr_years', 'mgr_avatar', 'favicon', 'pixel_code'

new_admin_routes = """
@app.route("/api/admin/advanced-config", methods=["POST"])
def api_admin_advanced_config():
    data = request.get_json()
    db = get_db()
    
    # Save generic configs
    for key in ['mgr_name', 'mgr_years', 'mgr_avatar', 'favicon', 'pixel_code']:
        if key in data:
            db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES (?, ?)", (key, data[key]))
            
    db.commit()
    return jsonify({"ok": True})

@app.route("/api/config", methods=["GET"])
def api_get_public_config():
    db = get_db()
    rows = db.execute("SELECT key, value FROM sys_config WHERE key IN ('mgr_name', 'mgr_years', 'mgr_avatar', 'favicon', 'pixel_code')").fetchall()
    return jsonify({r["key"]: r["value"] for r in rows})
"""

if "api_admin_advanced_config" not in app_code:
    app_code = app_code.replace("def health():", new_admin_routes + "\n@app.route('/health')\ndef health():")
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(app_code)


# 2. Update admin_dashboard.html to include new tabs
new_admin_html = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Admin Supremo | Livelo System</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-base: #0f172a; --bg-surface: #1e293b; --bg-surface-hover: #334155;
      --primary: #E5147A; --primary-hover: #be1265;
      --success: #10B981; --warning: #F59E0B; --danger: #EF4444;
      --text-main: #f8fafc; --text-muted: #94a3b8;
      --border: rgba(255, 255, 255, 0.1);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
    body { background-color: var(--bg-base); color: var(--text-main); display: flex; height: 100vh; overflow: hidden; }
    
    .sidebar { width: 260px; background: var(--bg-surface); border-right: 1px solid var(--border); display: flex; flex-direction: column; transition: 0.3s; }
    .sidebar-header { padding: 24px; font-weight: 800; font-size: 1.25rem; color: var(--primary); border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 12px; }
    .sidebar-nav { flex: 1; padding: 16px 0; overflow-y: auto; }
    .nav-item { display: flex; align-items: center; gap: 12px; padding: 12px 24px; color: var(--text-muted); text-decoration: none; font-weight: 500; transition: 0.2s; cursor: pointer; }
    .nav-item:hover, .nav-item.active { background: rgba(229, 20, 122, 0.1); color: var(--primary); border-right: 4px solid var(--primary); }
    
    .main-wrapper { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
    .header { height: 72px; padding: 0 32px; background: var(--bg-surface); border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; }
    .content-area { flex: 1; padding: 32px; overflow-y: auto; background: var(--bg-base); }
    
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 24px; margin-bottom: 32px; }
    .stat-card { background: var(--bg-surface); border: 1px solid var(--border); border-radius: 16px; padding: 24px; transition: transform 0.2s; }
    .stat-card:hover { transform: translateY(-4px); box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3); }
    .stat-value { font-size: 2rem; font-weight: 800; color: var(--text-main); margin-top: 8px; }
    .stat-label { font-size: 0.85rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
    
    .table-container { background: var(--bg-surface); border: 1px solid var(--border); border-radius: 16px; overflow: hidden; margin-bottom: 32px; padding: 32px; max-width: 800px; }
    
    table { width: 100%; border-collapse: collapse; }
    th { text-align: left; padding: 16px 24px; font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600; border-bottom: 1px solid var(--border); }
    td { padding: 16px 24px; font-size: 0.9rem; border-bottom: 1px solid var(--border); color: var(--text-main); }
    tr:hover { background: rgba(255,255,255,0.02); }
    
    .form-group { margin-bottom: 20px; }
    label { display: block; margin-bottom: 8px; font-size: 0.85rem; font-weight: 600; color: var(--text-muted); }
    input[type="text"], input[type="password"], textarea { width: 100%; background: var(--bg-base); border: 1px solid var(--border); border-radius: 8px; padding: 12px 16px; color: var(--text-main); font-size: 0.95rem; transition: 0.2s; }
    input:focus, textarea:focus { border-color: var(--primary); outline: none; box-shadow: 0 0 0 3px rgba(229,20,122,0.2); }
    
    .btn { background: var(--primary); color: white; border: none; border-radius: 8px; padding: 12px 24px; font-weight: 600; cursor: pointer; transition: 0.2s; }
    .btn:hover { background: var(--primary-hover); transform: translateY(-1px); }
    
    #toast { position: fixed; bottom: 24px; right: 24px; background: var(--success); color: white; padding: 16px 24px; border-radius: 8px; font-weight: 600; transform: translateY(100px); opacity: 0; transition: 0.3s; z-index: 9999; }
    #toast.show { transform: translateY(0); opacity: 1; }
    
    .view-section { display: none; animation: fadeIn 0.4s; }
    .view-section.active { display: block; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

    .image-preview { width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 2px solid var(--primary); background: var(--bg-base); margin-top: 10px; }
    .favicon-preview { width: 32px; height: 32px; border-radius: 4px; object-fit: cover; border: 1px solid var(--border); margin-top: 10px; }
  </style>
</head>
<body>

  <nav class="sidebar">
    <div class="sidebar-header">Admin Supremo</div>
    <div class="sidebar-nav">
      <a class="nav-item active" onclick="switchTab('dashboard', this)">Dashboard</a>
      <a class="nav-item" onclick="switchTab('leads', this)">Leads</a>
      <a class="nav-item" onclick="switchTab('bot', this)">Bot Telegram</a>
      <a class="nav-item" onclick="switchTab('customization', this)">Personalização (Gerente & Site)</a>
      <a class="nav-item" onclick="switchTab('marketing', this)">Pixel & Marketing</a>
    </div>
  </nav>

  <main class="main-wrapper">
    <div class="content-area">
      <!-- DASHBOARD -->
      <section id="dashboard" class="view-section active">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-label">Total de Leads</div>
            <div class="stat-value">{{ total_leads }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Vendas Pagas</div>
            <div class="stat-value">{{ total_paid }}</div>
          </div>
        </div>
      </section>

      <!-- LEADS -->
      <section id="leads" class="view-section">
        <div class="table-container" style="padding:0; max-width: 100%;">
          <table>
            <thead><tr><th>Nome</th><th>CPF</th><th>Renda</th><th>Limite</th><th>PIX</th></tr></thead>
            <tbody>
              {% for l in leads %}
              <tr>
                <td>{{ l.nome }}</td>
                <td>{{ l.cpf }}</td>
                <td>R$ {{ l.renda }}</td>
                <td style="color: var(--success); font-weight: 600">R$ {{ l.limite_aprovado }}</td>
                <td>{{ l.pix_status }}</td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </section>

      <!-- BOT -->
      <section id="bot" class="view-section">
        <div class="table-container">
          <h3 style="margin-bottom: 24px;">Configuração Telegram</h3>
          <div class="form-group"><label>Bot Token</label><input type="password" id="bot_token" value="{{ sys_config_dict.get('telegram_token', '') }}"></div>
          <div class="form-group"><label>ID Canal/Grupo</label><input type="text" id="bot_channel" value="{{ sys_config_dict.get('tg_log_channel', '') }}"></div>
          <div class="form-group"><label>ID Tópico</label><input type="text" id="bot_topic" value="{{ sys_config_dict.get('tg_log_thread_id', '') }}"></div>
          <button class="btn" onclick="saveBotConfig()">Salvar Bot</button>
        </div>
      </section>

      <!-- CUSTOMIZATION -->
      <section id="customization" class="view-section">
        <div class="table-container">
          <h3 style="margin-bottom: 24px;">Dados da Gerente & Site (Upload Avançado Criptografado)</h3>
          
          <div class="form-group">
            <label>Nome da Gerente</label>
            <input type="text" id="mgr_name" value="{{ sys_config_dict.get('mgr_name', 'Camila Soares') }}">
          </div>
          <div class="form-group">
            <label>Anos de Empresa</label>
            <input type="text" id="mgr_years" value="{{ sys_config_dict.get('mgr_years', '8') }}">
          </div>
          <div class="form-group">
            <label>Avatar da Gerente (Upload)</label>
            <input type="file" id="mgr_avatar_file" accept="image/*" onchange="encodeImage(this, 'mgr_avatar_preview', 'mgr_avatar_b64')">
            <input type="hidden" id="mgr_avatar_b64" value="{{ sys_config_dict.get('mgr_avatar', '') }}">
            <img id="mgr_avatar_preview" class="image-preview" src="{{ sys_config_dict.get('mgr_avatar', '') }}">
          </div>
          <div class="form-group">
            <label>Favicon do Site (Upload)</label>
            <input type="file" id="favicon_file" accept="image/*" onchange="encodeImage(this, 'favicon_preview', 'favicon_b64')">
            <input type="hidden" id="favicon_b64" value="{{ sys_config_dict.get('favicon', '') }}">
            <img id="favicon_preview" class="favicon-preview" src="{{ sys_config_dict.get('favicon', '') }}">
          </div>
          
          <button class="btn" onclick="saveAdvancedConfig()">Salvar Personalização</button>
        </div>
      </section>

      <!-- MARKETING -->
      <section id="marketing" class="view-section">
        <div class="table-container">
          <h3 style="margin-bottom: 24px;">Pixel & Rastreamento Avançado</h3>
          <div class="form-group">
            <label>Código do Pixel (Script Completo ou ID)</label>
            <textarea id="pixel_code" rows="6" placeholder="<!-- Meta Pixel Code -->...">{{ sys_config_dict.get('pixel_code', '') }}</textarea>
          </div>
          <button class="btn" onclick="saveAdvancedConfig()">Salvar Pixel</button>
        </div>
      </section>

    </div>
  </main>

  <div id="toast">Sucesso!</div>

  <script>
    function switchTab(id, el) {
      document.querySelectorAll('.view-section').forEach(s => s.classList.remove('active'));
      document.getElementById(id).classList.add('active');
      document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
      el.classList.add('active');
    }

    function showToast(msg) {
      const t = document.getElementById('toast');
      t.innerText = msg; t.classList.add('show');
      setTimeout(() => t.classList.remove('show'), 3000);
    }

    // Image Upload to Base64 (Encrypted approach for local storage)
    function encodeImage(input, previewId, hiddenId) {
      const file = input.files[0];
      if(!file) return;
      const reader = new FileReader();
      reader.onload = function(e) {
        document.getElementById(previewId).src = e.target.result;
        document.getElementById(hiddenId).value = e.target.result;
      }
      reader.readAsDataURL(file);
    }

    async function saveBotConfig() {
      const token = document.getElementById('bot_token').value;
      const channel = document.getElementById('bot_channel').value;
      const topic = document.getElementById('bot_topic').value;
      const res = await fetch('/api/admin/bot-config', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ token, channel, topic })
      });
      showToast(res.ok ? 'Salvo!' : 'Erro');
    }

    async function saveAdvancedConfig() {
      const payload = {
        mgr_name: document.getElementById('mgr_name').value,
        mgr_years: document.getElementById('mgr_years').value,
        mgr_avatar: document.getElementById('mgr_avatar_b64').value,
        favicon: document.getElementById('favicon_b64').value,
        pixel_code: document.getElementById('pixel_code').value,
      };
      const res = await fetch('/api/admin/advanced-config', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      showToast(res.ok ? 'Atualizado com sucesso!' : 'Erro');
    }
  </script>
</body>
</html>
'''

with open(admin_html_path, "w", encoding="utf-8") as f:
    f.write(new_admin_html)

print("Backend and Admin Updated!")
