from pathlib import Path
import re

# 1. Update supreme_admin.html
html_file = Path("templates/supreme_admin.html")
content = html_file.read_text("utf-8")

# Add the new tab button if not there
if "Gestão de Equipe" not in content:
    content = content.replace(
        '<button class="tab-btn" onclick="switchTab(\'tab-config\', this)">Configurações</button>',
        '<button class="tab-btn" onclick="switchTab(\'tab-config\', this)">Configurações</button>\n            <button class="tab-btn" onclick="switchTab(\'tab-equipe\', this)">Gestão de Equipe</button>'
    )
    
    # Add the new tab content
    equipe_tab = """
        <!-- TAB: EQUIPE -->
        <div id="tab-equipe" class="tab-content">
            <div class="glass-panel" style="width:100%;">
                <div class="stat-title" style="margin-bottom: 20px; display:flex; justify-content:space-between;">
                    <span>Gerenciamento de Administradores Normais (Gerentes)</span>
                    <div style="display:flex; gap:10px;">
                        <input type="text" id="new-manager-id" class="input-glass" style="width:200px;" placeholder="Telegram ID">
                        <button class="btn-glass" onclick="addManager()">ADICIONAR</button>
                    </div>
                </div>
                <div class="grid-container" id="managers-grid">
                    <!-- Loaded dynamically -->
                </div>
            </div>
        </div>
    """
    content = content.replace('<!-- MODAL PROFILE -->', equipe_tab + '\n    <!-- MODAL PROFILE -->')
    
    # Add JS for team management
    js_equipe = """
        async function loadManagers() {
            try {
                const res = await fetch('/api/supreme/managers');
                const data = await res.json();
                if(data.ok) renderManagers(data.managers);
            } catch(e) {}
        }
        
        function renderManagers(managers) {
            const grid = document.getElementById('managers-grid');
            grid.innerHTML = '';
            managers.forEach(m => {
                const statusColor = m.status === 'active' ? 'var(--green)' : 'var(--red)';
                const statusText = m.status === 'active' ? 'ATIVO' : 'BLOQUEADO';
                const actionBtn = m.status === 'active' ? `<button onclick="toggleManager('${m.telegram_id}', 'blocked')" style="background:var(--red); color:white; padding:6px; border:none; border-radius:6px; cursor:pointer; font-weight:800; font-size:0.75rem;">BLOQUEAR</button>` : `<button onclick="toggleManager('${m.telegram_id}', 'active')" style="background:var(--green); color:white; padding:6px; border:none; border-radius:6px; cursor:pointer; font-weight:800; font-size:0.75rem;">DESBLOQUEAR</button>`;
                
                grid.innerHTML += `
                    <div class="stat-card" style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.1); border-radius:12px; padding:20px; display:flex; flex-direction:column; gap:16px;">
                        <div style="display:flex; align-items:center; gap:16px;">
                            <img src="${m.avatar_url}" style="width:60px; height:60px; border-radius:50%; border:2px solid ${statusColor}; object-fit:cover;">
                            <div>
                                <div style="font-weight:800; font-size:1.1rem;">${m.name}</div>
                                <div style="font-size:0.8rem; color:var(--text-muted);">ID: ${m.telegram_id}</div>
                                <div style="font-size:0.7rem; font-weight:800; color:${statusColor}; margin-top:4px;">${statusText}</div>
                            </div>
                        </div>
                        <div style="display:flex; gap:8px;">
                            <button onclick="generateManagerLink('${m.telegram_id}')" class="btn-glass" style="flex:1; padding:8px; font-size:0.8rem;">GERAR ACESSO</button>
                            ${actionBtn}
                            <button onclick="deleteManager('${m.telegram_id}')" style="background:transparent; color:var(--red); border:1px solid var(--red); padding:6px; border-radius:6px; cursor:pointer; font-weight:800; font-size:0.75rem;">EXCLUIR</button>
                        </div>
                    </div>
                `;
            });
        }
        
        async function addManager() {
            const tid = document.getElementById('new-manager-id').value;
            if(!tid) return;
            const res = await fetch('/api/supreme/managers', {method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({telegram_id: tid})});
            const data = await res.json();
            if(data.ok) { document.getElementById('new-manager-id').value = ''; loadManagers(); showNotification('Gerente Adicionado!'); }
            else alert(data.error);
        }
        
        async function toggleManager(tid, status) {
            await fetch('/api/supreme/managers', {method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify({telegram_id: tid, status: status})});
            loadManagers(); showNotification('Status alterado!');
        }
        
        async function deleteManager(tid) {
            if(!confirm("Certeza que deseja excluir o gerente?")) return;
            await fetch('/api/supreme/managers', {method: 'DELETE', headers: {'Content-Type':'application/json'}, body: JSON.stringify({telegram_id: tid})});
            loadManagers(); showNotification('Gerente excluído!');
        }
        
        async function generateManagerLink(tid) {
            showNotification('Gerando porta criptografada...', 'pending');
            const res = await fetch('/api/supreme/manager_invite', {method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({telegram_id: tid})});
            const data = await res.json();
            if(data.ok) showNotification('Acesso enviado no Telegram do Gerente!', 'success');
            else showNotification('Erro: ' + data.error, 'error');
        }
        
        function showNotification(msg, type='success') {
            const notif = document.createElement('div');
            notif.innerText = msg;
            notif.style.cssText = `position:fixed; bottom:20px; right:20px; padding:16px 24px; border-radius:12px; color:white; font-weight:800; z-index:9999; animation: slideIn 0.3s forwards; box-shadow:0 10px 30px rgba(0,0,0,0.5);`;
            if(type==='success') notif.style.background = 'var(--green)';
            if(type==='error') notif.style.background = 'var(--red)';
            if(type==='pending') notif.style.background = 'var(--pink-accent)';
            document.body.appendChild(notif);
            setTimeout(() => {
                notif.style.animation = 'slideOut 0.3s forwards';
                setTimeout(()=>notif.remove(), 300);
            }, 4000);
        }
        
        // Add CSS animations for notifications
        const style = document.createElement('style');
        style.innerHTML = `@keyframes slideIn { from { transform:translateX(100%); opacity:0;} to { transform:translateX(0); opacity:1;} } @keyframes slideOut { from { transform:translateX(0); opacity:1;} to { transform:translateX(100%); opacity:0;} }`;
        document.head.appendChild(style);
    """
    content = content.replace('loadConfig();', 'loadConfig();\n                    loadManagers();')
    content = content.replace('async function loadConfig()', js_equipe + '\n        async function loadConfig()')
    html_file.write_text(content, "utf-8")
    print("supreme_admin.html patched.")

# 2. Create manager_dashboard.html
manager_html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexus Gate | Terminal do Gerente</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        
        :root {
            --bg-dark: #0A0A0A;
            --bg-panel: rgba(20, 20, 20, 0.8);
            --border-glow: rgba(59, 130, 246, 0.3);
            --blue-accent: #3B82F6;
            --blue-glow: #60A5FA;
            --text-main: #FFFFFF;
            --text-muted: #A0A0A0;
            --green: #10B981;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        body { background-color: var(--bg-dark); color: var(--text-main); min-height: 100vh; display: flex; justify-content: center; align-items: center; overflow-x: hidden; }

        .glass-panel { background: var(--bg-panel); backdrop-filter: blur(16px); border: 1px solid var(--border-glow); border-radius: 20px; padding: 40px; box-shadow: 0 0 40px rgba(0, 0, 0, 0.5); }
        .input-glass { width: 100%; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: white; padding: 12px; border-radius: 8px; outline: none; transition: border-color 0.3s; text-align: center; font-size:1.5rem; font-weight:800; letter-spacing:8px; }
        .input-glass:focus { border-color: var(--blue-accent); }
        .btn-glass { background: rgba(59, 130, 246, 0.2); color: white; border: 1px solid var(--blue-accent); padding: 12px 20px; border-radius: 8px; font-weight: 800; cursor: pointer; transition: all 0.3s; width: 100%; margin-top:20px; }
        .btn-glass:hover { background: var(--blue-accent); box-shadow: 0 0 15px var(--blue-glow); transform: translateY(-2px); }

        #auth-screen { display: flex; flex-direction: column; align-items: center; width: 100%; max-width: 400px; z-index: 10; animation: fadeIn 0.5s; }
        #dashboard { display: none; width: 100%; max-width: 1200px; padding: 40px 20px; flex-direction: column; animation: fadeIn 0.5s; align-self: flex-start; margin: 0 auto; }
        
        .dash-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; border-bottom: 1px solid var(--border-glow); padding-bottom: 20px; }
        
        .leads-container { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 24px; }
        .lead-card { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 16px; padding: 24px; transition: 0.3s; position: relative; overflow: hidden; }
        .lead-card:hover { border-color: var(--blue-accent); transform: translateY(-5px); box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        .lead-card::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 4px; background: var(--blue-accent); }
        
        .lead-name { font-size: 1.2rem; font-weight: 800; margin-bottom: 8px; }
        .lead-detail { font-size: 0.85rem; color: var(--text-muted); margin-bottom: 4px; display:flex; justify-content:space-between; border-bottom:1px dashed rgba(255,255,255,0.1); padding-bottom:4px; }
        
        .whatsapp-btn { display: flex; align-items: center; justify-content: center; gap: 8px; background: #25D366; color: white; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: 800; margin-top: 16px; transition: 0.3s; width:100%; }
        .whatsapp-btn:hover { background: #1EBE55; transform: scale(1.02); }

        /* Loader */
        .loader { width: 48px; height: 48px; border: 5px solid rgba(255,255,255,0.1); border-bottom-color: var(--blue-accent); border-radius: 50%; display: inline-block; animation: rotation 1s linear infinite; }
        #loading-screen { display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:var(--bg-dark); z-index:999; justify-content:center; align-items:center; flex-direction:column; gap:20px; }

        @keyframes rotation { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>

    <div id="loading-screen">
        <span class="loader"></span>
        <div style="font-weight:800; letter-spacing:2px; color:var(--blue-accent);">DESCRIPTOGRAFANDO PORTA...</div>
    </div>

    <!-- AUTH SCREEN -->
    <div id="auth-screen" class="glass-panel">
        <div style="color:var(--blue-accent); font-size:0.85rem; font-weight:600; padding:8px 16px; background:rgba(59,130,246,0.1); border:1px solid rgba(59,130,246,0.3); border-radius:8px; margin-bottom:20px;">
            PORTA CRIPTOGRAFADA ÚNICA
        </div>
        <h2 style="font-weight: 800; letter-spacing: 2px; text-transform: uppercase;">Acesso do Gerente</h2>
        <p style="color:var(--text-muted); font-size:0.85rem; margin-top:10px; text-align:center; margin-bottom:24px;">Insira o código de 6 dígitos enviado no seu Telegram.</p>
        
        <input type="text" id="access-code" class="input-glass" maxlength="6" autocomplete="off">
        <button class="btn-glass" onclick="authenticate()">LIBERAR ACESSO</button>
        <div id="auth-error" style="color:#EF4444; font-size:0.85rem; margin-top:16px; text-align:center; height:16px;"></div>
    </div>

    <!-- DASHBOARD -->
    <div id="dashboard">
        <div class="dash-header">
            <div>
                <h1 style="font-size:1.8rem; font-weight:800; letter-spacing:1px; color:var(--blue-accent);">Painel de Atendimento</h1>
                <p style="color:var(--text-muted); font-size:0.9rem; margin-top:5px;">Lista de clientes prontos para contato.</p>
            </div>
            <button class="btn-glass" style="width:auto; margin:0;" onclick="location.reload()">ATUALIZAR LISTA</button>
        </div>
        
        <div class="leads-container" id="leads-grid"></div>
    </div>

    <script>
        const hashStr = "{{ hash }}";
        
        async function authenticate() {
            const code = document.getElementById('access-code').value;
            if(code.length !== 6) return;
            const errDiv = document.getElementById('auth-error');
            errDiv.style.color = "var(--blue-accent)"; errDiv.innerText = "Autenticando...";
            
            try {
                const res = await fetch('/api/manager/auth', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({hash: hashStr, code: code}) });
                const data = await res.json();
                if(data.ok) {
                    document.getElementById('auth-screen').style.display = 'none';
                    document.getElementById('loading-screen').style.display = 'flex';
                    setTimeout(() => {
                        document.getElementById('loading-screen').style.display = 'none';
                        document.getElementById('dashboard').style.display = 'flex';
                        loadLeads();
                    }, 1500);
                } else throw new Error(data.error);
            } catch(e) {
                errDiv.style.color = "#EF4444"; errDiv.innerText = e.message;
            }
        }
        
        window.onload = () => { if(document.cookie.includes('manager_token=')) {
            document.getElementById('auth-screen').style.display = 'none';
            document.getElementById('dashboard').style.display = 'flex';
            loadLeads();
        }};
        
        async function loadLeads() {
            try {
                const res = await fetch('/api/manager/dashboard');
                if(res.status === 401 || res.status === 403) { document.getElementById('auth-screen').style.display = 'flex'; document.getElementById('dashboard').style.display = 'none'; return; }
                const data = await res.json();
                if(data.ok) renderLeads(data.leads);
            } catch(e) {}
        }
        
        function validatePhone(phone) {
            if(!phone) return null;
            const clean = phone.replace(/\\D/g, '');
            if(clean.length >= 10 && clean.length <= 11) return clean;
            return null;
        }
        
        function renderLeads(leads) {
            const grid = document.getElementById('leads-grid');
            grid.innerHTML = '';
            leads.forEach(l => {
                const phone = validatePhone(l.whatsapp);
                const waBtn = phone ? `<a href="https://wa.me/55${phone}?text=Ol%C3%A1%20${l.nome.split(' ')[0]}!%20Aqui%20%C3%A9%20o%20seu%20gerente%20Livelo." target="_blank" class="whatsapp-btn">Chamar no WhatsApp</a>` : `<div style="text-align:center; color:#EF4444; font-size:0.8rem; margin-top:16px; font-weight:800;">Número Inválido</div>`;
                
                grid.innerHTML += `
                    <div class="lead-card">
                        <div class="lead-name">${l.nome}</div>
                        <div class="lead-detail"><span>CPF</span><span style="color:white; font-weight:600;">${l.cpf}</span></div>
                        <div class="lead-detail"><span>Cartão</span><span style="color:var(--blue-glow); font-weight:600;">${l.card_style||'-'}</span></div>
                        <div class="lead-detail"><span>Limite</span><span style="color:var(--green); font-weight:600;">R$ ${l.limite_aprovado||'0'}</span></div>
                        <div class="lead-detail"><span>WhatsApp</span><span style="color:white; font-weight:600;">${l.whatsapp||'-'}</span></div>
                        ${waBtn}
                    </div>
                `;
            });
        }
    </script>
</body>
</html>
"""

manager_path = Path("templates/manager_dashboard.html")
manager_path.write_text(manager_html, "utf-8")
print("manager_dashboard.html created.")
