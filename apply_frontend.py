import os

HTML_FILE = "d:/Paginas ADS/Livelo/templates/supreme_admin.html"

with open(HTML_FILE, "r", encoding="utf-8") as f:
    html = f.read()

# Replace CSS
old_css = """        /* PIN Screen */
        #pin-screen { display: flex; flex-direction: column; align-items: center; width: 100%; max-width: 400px; z-index: 10; }
        .pin-display { display: flex; gap: 12px; margin: 30px 0; }
        .pin-dot { width: 16px; height: 16px; border-radius: 50%; border: 2px solid var(--pink-accent); transition: all 0.2s; }
        .pin-dot.filled { background: var(--pink-accent); box-shadow: 0 0 10px var(--pink-glow); }
        .numpad { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; width: 100%; }
        .num-btn { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: white; font-size: 1.5rem; font-weight: 600; padding: 20px; border-radius: 12px; cursor: pointer; transition: all 0.2s; }
        .num-btn:hover { background: rgba(229, 20, 122, 0.2); border-color: var(--pink-accent); }
        .num-btn:active { transform: scale(0.95); }"""

new_css = """        /* PREMIUM PIN SCREEN */
        #pin-screen { display: flex; flex-direction: column; align-items: center; width: 100%; max-width: 440px; z-index: 10; padding: 50px 40px; background: rgba(10, 10, 15, 0.85); -webkit-backdrop-filter: blur(25px); backdrop-filter: blur(25px); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 24px; box-shadow: 0 30px 60px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255,255,255,0.1); position: relative; overflow: hidden; transition: all 0.5s; }
        #pin-screen::before { content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(229,20,122,0.15) 0%, transparent 60%); z-index: -1; animation: pulseGlow 6s infinite alternate; }
        
        .role-badge { display: inline-flex; align-items: center; gap: 8px; color: #fff; font-size: 0.75rem; font-weight: 800; letter-spacing: 2px; padding: 8px 16px; background: linear-gradient(90deg, rgba(229,20,122,0.3), rgba(0,0,0,0)); border-left: 3px solid var(--pink-accent); border-radius: 4px; margin-bottom: 30px; text-transform: uppercase; }
        
        .pin-title { font-size: 1.8rem; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 8px; background: linear-gradient(135deg, #fff, #aaa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; }
        
        .pin-display { display: flex; gap: 16px; margin: 40px 0; }
        .pin-dot { width: 16px; height: 16px; border-radius: 50%; border: 2px solid rgba(255,255,255,0.1); background: rgba(0,0,0,0.5); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: inset 0 2px 4px rgba(0,0,0,0.5); }
        .pin-dot.filled { border-color: var(--pink-accent); background: var(--pink-accent); box-shadow: 0 0 15px var(--pink-glow), 0 0 30px var(--pink-accent); transform: scale(1.2); }
        
        .numpad { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; width: 100%; }
        .num-btn { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); color: #fff; font-size: 1.5rem; font-weight: 500; padding: 22px; border-radius: 16px; cursor: pointer; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); position: relative; overflow: hidden; display: flex; justify-content: center; align-items: center; }
        .num-btn::after { content: ''; position: absolute; width: 100%; height: 100%; background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%); top: 0; left: 0; opacity: 0; transition: opacity 0.3s; }
        .num-btn:hover { background: rgba(255,255,255,0.08); border-color: rgba(255,255,255,0.2); transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.3); }
        .num-btn:hover::after { opacity: 1; }
        .num-btn:active { transform: translateY(0) scale(0.95); background: rgba(229,20,122,0.2); border-color: var(--pink-accent); }
        
        .action-btn { font-size: 1rem; font-weight: 700; letter-spacing: 1px; }
        .clear-btn { color: var(--red); background: rgba(239, 68, 68, 0.05); }
        .submit-btn { color: var(--green); background: rgba(16, 185, 129, 0.05); }
        .clear-btn:hover { background: rgba(239, 68, 68, 0.15); border-color: rgba(239,68,68,0.3); box-shadow: 0 10px 20px rgba(239,68,68,0.2); }
        .submit-btn:hover { background: rgba(16, 185, 129, 0.15); border-color: rgba(16,185,129,0.3); box-shadow: 0 10px 20px rgba(16,185,129,0.2); }
        
        @keyframes pulseGlow { 0% { opacity: 0.5; transform: scale(0.9); } 100% { opacity: 1; transform: scale(1.1); } }"""

if old_css in html:
    html = html.replace(old_css, new_css)
else:
    print("CSS block not found!")

# Replace HTML
old_html = """    <!-- SECURE PIN LOGIN -->
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
    </div>"""

new_html = """    <!-- SECURE PIN LOGIN -->
    <div id="pin-screen">
        <div class="role-badge">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"></path></svg>
            <span id="role-text">PORTA CRIPTOGRAFADA</span>
        </div>
        
        <h2 class="pin-title">ACESSO RESTRITO</h2>
        <p style="color:var(--text-muted); font-size:0.9rem;">Autenticação requerida. Insira o PIN de 6 dígitos.</p>
        
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
            <button class="num-btn action-btn clear-btn" onclick="clearPin()">DEL</button>
            <button class="num-btn" onclick="addPin('0')">0</button>
            <button class="num-btn action-btn submit-btn" onclick="submitPin()">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
            </button>
        </div>
        
        <button onclick="recoverPin()" style="margin-top:30px; background:transparent; border:none; color:rgba(255,255,255,0.4); text-decoration:none; cursor:pointer; font-size:0.8rem; transition: color 0.3s;" onmouseover="this.style.color='#fff'" onmouseout="this.style.color='rgba(255,255,255,0.4)'">Esqueci o PIN (Enviar no Telegram Privado)</button>
        <div id="pin-error" style="color:var(--red); font-size:0.85rem; margin-top:16px; height:16px; font-weight:600;"></div>
    </div>"""

if old_html in html:
    html = html.replace(old_html, new_html)
else:
    print("HTML block not found!")


# Replace JS submit function
old_js = """        async function submitPin() {
            if(currentPin.length !== 6) return;
            const errDiv = document.getElementById('pin-error');
            errDiv.innerText = "Verificando criptografia...";
            try {
                const res = await fetch('/api/supreme/auth', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({pin: currentPin}) });"""

new_js = """        async function submitPin() {
            if(currentPin.length !== 6) return;
            const errDiv = document.getElementById('pin-error');
            errDiv.innerText = "Verificando criptografia avançada...";
            errDiv.style.color = "var(--text-muted)";
            try {
                const portId = "{{ port_id|default('') }}";
                const res = await fetch('/api/supreme/auth', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({pin: currentPin, port_id: portId}) });"""

if old_js in html:
    html = html.replace(old_js, new_js)
else:
    print("JS block not found!")

# Add logic to hide elements if role is unknown or to show role text
role_script = """
        window.onload = () => { 
            const roleType = "{{ role_type|default('supreme') }}";
            if (roleType === "supreme") {
                document.getElementById('role-text').innerText = "SUPREME ADMIN PORT";
                document.querySelector('.role-badge').style.borderLeftColor = "#10B981";
                document.querySelector('.role-badge').style.background = "linear-gradient(90deg, rgba(16,185,129,0.3), rgba(0,0,0,0))";
            } else if (roleType !== "unknown") {
                document.getElementById('role-text').innerText = "MANAGER PORT";
                document.querySelector('.role-badge').style.borderLeftColor = "#3B82F6";
                document.querySelector('.role-badge').style.background = "linear-gradient(90deg, rgba(59,130,246,0.3), rgba(0,0,0,0))";
            }
            if(document.cookie.includes('supreme_token=')) loadDashboard(); 
        };"""

if "window.onload = () => { if(document.cookie.includes('supreme_token=')) loadDashboard(); };" in html:
    html = html.replace("window.onload = () => { if(document.cookie.includes('supreme_token=')) loadDashboard(); };", role_script)
else:
    print("Window onload block not found!")

with open(HTML_FILE, "w", encoding="utf-8") as f:
    f.write(html)

print("Frontend updated successfully.")
