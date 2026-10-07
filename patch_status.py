import sqlite3
import os
from pathlib import Path
import re

db_path = Path("livelo.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()
try:
    cur.execute("ALTER TABLE managers ADD COLUMN last_seen INTEGER DEFAULT 0")
    print("Column last_seen added to managers.")
except sqlite3.OperationalError:
    print("last_seen column already exists.")
conn.commit()
conn.close()

app_file = Path("app.py")
content = app_file.read_text("utf-8")

# 1. Update init_db patch to include last_seen
content = content.replace("status TEXT DEFAULT 'active',", "status TEXT DEFAULT 'active',\n        last_seen INTEGER DEFAULT 0,")

# 2. Update manager_dashboard_data route to update last_seen and fetch Supreme Manager config
if "def manager_dashboard_data():" in content:
    replacement_manager_dash = """def manager_dashboard_data():
    db = get_db()
    
    # Update last_seen for this manager
    token = request.cookies.get('manager_token')
    if token:
        import time
        db.execute("UPDATE managers SET last_seen = ? WHERE telegram_id = ?", (int(time.time()), token))
        db.commit()
        
    recent_leads = db.execute("SELECT l.* FROM leads l JOIN payments p ON l.cpf = p.cpf WHERE p.status='approved' OR p.status='pago' OR p.status='pending' ORDER BY l.created_at DESC LIMIT 200").fetchall()
    
    sup_mgr = db.execute("SELECT * FROM sys_config WHERE key = 'manager'").fetchone()
    sup_mgr_name = "Gerente Livelo"
    if sup_mgr and sup_mgr['value']:
        import json
        try:
            m_data = json.loads(sup_mgr['value'])
            if m_data.get('name'): sup_mgr_name = m_data['name']
        except: pass
        
    return jsonify({"ok": True, "leads": [dict(l) for l in recent_leads], "supreme_manager_name": sup_mgr_name})"""
    
    content = re.sub(r'def manager_dashboard_data\(\):.*?return jsonify\(\{"ok": True.*?\}\)', replacement_manager_dash, content, flags=re.DOTALL)

app_file.write_text(content, "utf-8")
print("app.py updated with last_seen and manager config.")

# 3. Update supreme_admin.html to show Online/Offline and use Vector Icons
sup_html = Path("templates/supreme_admin.html")
if sup_html.exists():
    sup_content = sup_html.read_text("utf-8")
    
    # Replace renderManagers function to include last_seen logic and vector icons
    js_to_replace = """function renderManagers(managers) {
            const grid = document.getElementById('managers-grid');
            grid.innerHTML = '';
            managers.forEach(m => {
                const statusColor = m.status === 'active' ? 'var(--green)' : 'var(--red)';
                const statusText = m.status === 'active' ? 'ATIVO' : 'BLOQUEADO';
                const actionBtn = m.status === 'active' ? `<button onclick="toggleManager('${m.telegram_id}', 'blocked')" style="background:var(--red); color:white; padding:6px; border:none; border-radius:6px; cursor:pointer; font-weight:800; font-size:0.75rem;">BLOQUEAR</button>` : `<button onclick="toggleManager('${m.telegram_id}', 'active')" style="background:var(--green); color:white; padding:6px; border:none; border-radius:6px; cursor:pointer; font-weight:800; font-size:0.75rem;">DESBLOQUEAR</button>`;"""
    
    js_replacement = """function renderManagers(managers) {
            const grid = document.getElementById('managers-grid');
            grid.innerHTML = '';
            const now = Math.floor(Date.now() / 1000);
            managers.forEach(m => {
                const statusColor = m.status === 'active' ? 'var(--green)' : 'var(--red)';
                const statusText = m.status === 'active' ? 'ATIVO' : 'BLOQUEADO';
                
                // Online/Offline Check (5 mins threshold)
                const isOnline = m.last_seen && (now - m.last_seen < 300);
                const onlineText = isOnline ? 'ONLINE' : 'OFFLINE';
                const onlineColor = isOnline ? 'var(--green)' : 'var(--text-muted)';
                const onlineGlow = isOnline ? 'box-shadow: 0 0 8px var(--green);' : '';
                
                const actionBtn = m.status === 'active' ? `<button onclick="toggleManager('${m.telegram_id}', 'blocked')" class="btn-glass" style="background:rgba(239, 68, 68, 0.2); border-color:#EF4444; flex:1; padding:8px; font-size:0.75rem;">BLOQUEAR</button>` : `<button onclick="toggleManager('${m.telegram_id}', 'active')" class="btn-glass" style="background:rgba(16, 185, 129, 0.2); border-color:var(--green); flex:1; padding:8px; font-size:0.75rem;">DESBLOQUEAR</button>`;"""
                
    sup_content = sup_content.replace(js_to_replace, js_replacement)
    
    card_to_replace = """<div class="stat-card" style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.1); border-radius:12px; padding:20px; display:flex; flex-direction:column; gap:16px;">
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
                    </div>"""
                    
    card_replacement = """<div class="stat-card" style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.1); border-radius:12px; padding:20px; display:flex; flex-direction:column; gap:16px; position:relative;">
                        <div style="position:absolute; top:16px; right:16px; display:flex; align-items:center; gap:6px;">
                            <div style="width:8px; height:8px; border-radius:50%; background:${onlineColor}; ${onlineGlow}"></div>
                            <span style="font-size:0.7rem; font-weight:800; color:${onlineColor};">${onlineText}</span>
                        </div>
                        <div style="display:flex; align-items:center; gap:16px;">
                            <img src="${m.avatar_url}" style="width:60px; height:60px; border-radius:50%; border:2px solid ${statusColor}; object-fit:cover;">
                            <div>
                                <div style="font-weight:800; font-size:1.1rem; display:flex; align-items:center; gap:6px;">
                                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/></svg>
                                    ${m.name}
                                </div>
                                <div style="font-size:0.8rem; color:var(--text-muted); display:flex; align-items:center; gap:4px; margin-top:4px;">
                                    <svg width="12" height="12" fill="currentColor" viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
                                    ID: ${m.telegram_id}
                                </div>
                                <div style="font-size:0.7rem; font-weight:800; color:${statusColor}; margin-top:4px; display:flex; align-items:center; gap:4px;">
                                    <svg width="12" height="12" fill="currentColor" viewBox="0 0 24 24"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm-2 16l-4-4 1.41-1.41L10 14.17l6.59-6.59L18 9l-8 8z"/></svg>
                                    ${statusText}
                                </div>
                            </div>
                        </div>
                        <div style="display:flex; gap:8px;">
                            <button onclick="generateManagerLink('${m.telegram_id}')" class="btn-glass" style="flex:1; padding:8px; font-size:0.75rem; display:flex; align-items:center; justify-content:center; gap:4px;">
                                <svg width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zM9 6c0-1.66 1.34-3 3-3s3 1.34 3 3v2H9V6zm9 14H6V10h12v10zm-6-3c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2z"/></svg>
                                ACESSO
                            </button>
                            ${actionBtn}
                            <button onclick="deleteManager('${m.telegram_id}')" class="btn-glass" style="background:transparent; color:var(--red); border:1px solid var(--red); flex:0.5; padding:8px; display:flex; align-items:center; justify-content:center;">
                                <svg width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
                            </button>
                        </div>
                    </div>"""
    sup_content = sup_content.replace(card_to_replace, card_replacement)
    
    # Also replace text genders with SVG
    sup_content = sup_content.replace("let gText = l._gender === 'M' ? '🧔 Homem' : '👩 Mulher';", "let gText = l._gender === 'M' ? '<svg width=\"16\" height=\"16\" viewBox=\"0 0 24 24\" fill=\"currentColor\" style=\"vertical-align:middle\"><path d=\"M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z\"/></svg> Homem' : '<svg width=\"16\" height=\"16\" viewBox=\"0 0 24 24\" fill=\"currentColor\" style=\"vertical-align:middle\"><path d=\"M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v1h16v-1c0-2.66-5.33-4-8-4z\"/><path d=\"M12 21.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z\"/></svg> Mulher';")

    sup_html.write_text(sup_content, "utf-8")
    print("supreme_admin.html updated with online status and vectors.")

# 4. Update manager_dashboard.html for texts and UI
mgr_html = Path("templates/manager_dashboard.html")
if mgr_html.exists():
    mgr_content = mgr_html.read_text("utf-8")
    
    scripts_modal = """
    <!-- SCRIPTS MODAL -->
    <div id="scripts-modal-overlay" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); backdrop-filter:blur(8px); z-index:100; justify-content:center; align-items:center; opacity:0; transition:0.3s;">
        <div style="background:var(--bg-dark); border:1px solid var(--border-glow); border-radius:16px; width:90%; max-width:600px; padding:24px; transform:scale(0.95); transition:0.3s;" id="scripts-modal-content">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:16px;">
                <h3 style="display:flex; align-items:center; gap:8px;">
                    <svg width="20" height="20" fill="var(--blue-accent)" viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 9h12v2H6V9zm8 5H6v-2h8v2zm4-6H6V6h12v2z"/></svg>
                    Textos Prontos de Abordagem
                </h3>
                <button onclick="closeScripts()" style="background:transparent; border:none; color:white; font-size:1.5rem; cursor:pointer;">&times;</button>
            </div>
            
            <div style="display:flex; flex-direction:column; gap:16px;" id="scripts-list">
                <!-- Injected via JS -->
            </div>
        </div>
    </div>
    """
    
    if "SCRIPTS MODAL" not in mgr_content:
        mgr_content = mgr_content.replace('<!-- AUTH SCREEN -->', scripts_modal + '\n    <!-- AUTH SCREEN -->')
    
    # Replace global vars and add script logic
    js_update = """
        let supManagerName = "Gerente Livelo";
        let targetPhone = "";
        let targetName = "";
        
        async function loadLeads() {
            try {
                const res = await fetch('/api/manager/dashboard');
                if(res.status === 401 || res.status === 403) { document.getElementById('auth-screen').style.display = 'flex'; document.getElementById('dashboard').style.display = 'none'; return; }
                const data = await res.json();
                if(data.ok) {
                    supManagerName = data.supreme_manager_name || "Gerente Livelo";
                    renderLeads(data.leads);
                }
            } catch(e) {}
        }
        
        function openScripts(phone, leadName) {
            targetPhone = phone;
            targetName = leadName.split(' ')[0];
            
            const scripts = [
                { title: "Abordagem Inicial (Aprovado)", text: `Olá ${targetName}! Aqui é o gerente ${supManagerName} da Livelo. Vi que seu cartão foi aprovado com sucesso! Já podemos seguir com a liberação do seu limite?` },
                { title: "Cobrança de Frete (Pendente)", text: `Oi ${targetName}, sou o gerente ${supManagerName} da Livelo. Seu cartão já está pronto para envio, mas notei que o frete de emissão ainda está pendente. Posso te ajudar com isso?` },
                { title: "Dúvidas Gerais", text: `Olá ${targetName}, tudo bem? Sou o gerente ${supManagerName}. Estou aqui para tirar qualquer dúvida que você tenha sobre os benefícios do seu novo cartão Livelo!` }
            ];
            
            let html = '';
            scripts.forEach((s, idx) => {
                const encodedText = encodeURIComponent(s.text);
                html += `
                    <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.1); border-radius:12px; padding:16px;">
                        <div style="font-weight:800; color:var(--blue-glow); margin-bottom:8px; font-size:0.9rem;">${s.title}</div>
                        <div style="font-size:0.85rem; color:var(--text-muted); margin-bottom:12px; font-style:italic;">"${s.text}"</div>
                        <div style="display:flex; gap:8px;">
                            <a href="https://wa.me/55${targetPhone}?text=${encodedText}" target="_blank" class="btn-glass" style="flex:1; margin:0; padding:8px; text-decoration:none; text-align:center; background:#25D366; border-color:#25D366; color:white; display:flex; justify-content:center; align-items:center; gap:6px;">
                                <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.888-.788-1.487-1.761-1.66-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51a12.8 12.8 0 0 0-.57-.01c-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413z"/></svg>
                                ENVIAR NO WHATSAPP
                            </a>
                        </div>
                    </div>
                `;
            });
            document.getElementById('scripts-list').innerHTML = html;
            
            const overlay = document.getElementById('scripts-modal-overlay');
            overlay.style.display = 'flex';
            setTimeout(() => { overlay.style.opacity = '1'; document.getElementById('scripts-modal-content').style.transform = 'scale(1)'; }, 10);
        }
        
        function closeScripts() {
            const overlay = document.getElementById('scripts-modal-overlay');
            overlay.style.opacity = '0';
            document.getElementById('scripts-modal-content').style.transform = 'scale(0.95)';
            setTimeout(() => overlay.style.display = 'none', 300);
        }
    """
    
    mgr_content = mgr_content.replace('async function loadLeads() {', js_update.replace('async function loadLeads() {', ''))
    
    # Update buttons in renderLeads to use the script
    btn_replace = "const waBtn = phone ? `<a href=\"https://wa.me/55${phone}?text=Ol%C3%A1%20${l.nome.split(' ')[0]}!%20Aqui%20%C3%A9%20o%20seu%20gerente%20Livelo.\" target=\"_blank\" class=\"whatsapp-btn\">Chamar no WhatsApp</a>` : `<div style=\"text-align:center; color:#EF4444; font-size:0.8rem; margin-top:16px; font-weight:800;\">Número Inválido</div>`;"
    
    btn_new = """const waBtn = phone ? `
                    <div style="display:flex; gap:8px; margin-top:16px;">
                        <button onclick="openScripts('${phone}', '${l.nome.replace(/'/g,"")}')" class="btn-glass" style="flex:1; margin:0; padding:10px; display:flex; justify-content:center; align-items:center; gap:6px;">
                            <svg width="18" height="18" fill="currentColor" viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 9h12v2H6V9zm8 5H6v-2h8v2zm4-6H6V6h12v2z"/></svg>
                            ABORDAR CLIENTE
                        </button>
                    </div>
                ` : `<div style="text-align:center; color:#EF4444; font-size:0.8rem; margin-top:16px; font-weight:800; display:flex; justify-content:center; align-items:center; gap:6px;"><svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>Número Inválido</div>`;"""
                
    mgr_content = mgr_content.replace(btn_replace, btn_new)
    
    mgr_html.write_text(mgr_content, "utf-8")
    print("manager_dashboard.html updated with scripts and vectors.")
