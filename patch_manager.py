from pathlib import Path

app_file = Path("app.py")
content = app_file.read_text("utf-8")

if "/api/supreme/manager" not in content:
    manager_route = """
@app.route("/api/supreme/manager", methods=["GET", "POST"])
@supreme_required
def supreme_manager():
    db = get_db()
    if request.method == "GET":
        mgr = dict(db.execute("SELECT * FROM manager WHERE id=1").fetchone())
        return jsonify({"ok": True, "manager": mgr})
        
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        name = data.get("name")
        photo = data.get("photo_url")
        since = data.get("since_year")
        
        updates = []
        params = []
        if name:
            updates.append("name=?")
            params.append(name)
        if photo:
            updates.append("photo_url=?")
            params.append(photo)
        if since:
            updates.append("since_year=?")
            params.append(since)
            
        if updates:
            params.append(1) # for id=1
            query = f"UPDATE manager SET {', '.join(updates)}, updated_at=cast(strftime('%s','now') as real) WHERE id=?"
            db.execute(query, params)
            db.commit()
            
        return jsonify({"ok": True})
"""
    content = content.replace(
        "@app.errorhandler(404)",
        manager_route + "\n@app.errorhandler(404)"
    )
    app_file.write_text(content, "utf-8")
    print("Manager endpoints added to app.py")

html_file = Path("templates/supreme_admin.html")
html = html_file.read_text("utf-8")

if "Gerenciar Gerente" not in html:
    manager_ui = """
        <!-- GERENTE CONFIG -->
        <div class="glass-panel" style="width:100%; margin-top: 40px; display:flex; gap:20px; flex-wrap:wrap;">
            <div style="flex:1; min-width:300px;">
                <div class="stat-title" style="margin-bottom: 20px;">Gerenciar Gerente (Interface Avançada)</div>
                <div style="display:flex; flex-direction:column; gap:16px;">
                    <div>
                        <label style="font-size:0.8rem; color:var(--text-muted); display:block; margin-bottom:8px;">Nome do Gerente</label>
                        <input type="text" id="mgr-name" style="width:100%; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); color:white; padding:12px; border-radius:8px; outline:none;">
                    </div>
                    <div>
                        <label style="font-size:0.8rem; color:var(--text-muted); display:block; margin-bottom:8px;">Tempo de Empresa (Ex: Desde 2021)</label>
                        <input type="number" id="mgr-since" style="width:100%; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); color:white; padding:12px; border-radius:8px; outline:none;">
                    </div>
                    <div>
                        <label style="font-size:0.8rem; color:var(--text-muted); display:block; margin-bottom:8px;">Foto do Gerente (Upload Criptografado)</label>
                        <input type="file" id="mgr-photo" accept="image/*" style="width:100%; background:rgba(255,255,255,0.05); color:white; padding:12px; border-radius:8px;">
                    </div>
                    <button onclick="saveManager()" style="background:var(--pink-accent); color:white; border:none; padding:16px; border-radius:8px; font-weight:800; cursor:pointer; margin-top:10px;">SALVAR ALTERAÇÕES (BLINDADO)</button>
                    <div id="mgr-status" style="color:var(--green); font-size:0.85rem; margin-top:8px;"></div>
                </div>
            </div>
            <div style="flex:0.5; min-width:250px; display:flex; flex-direction:column; align-items:center; justify-content:center; background:rgba(0,0,0,0.3); border-radius:12px; padding:20px;">
                <img id="mgr-preview" src="" style="width:120px; height:120px; border-radius:50%; border:3px solid var(--pink-accent); object-fit:cover; margin-bottom:16px;">
                <div id="mgr-name-preview" style="font-size:1.2rem; font-weight:800;">Nome</div>
                <div id="mgr-since-preview" style="font-size:0.85rem; color:var(--text-muted);">Desde 2025</div>
            </div>
        </div>
"""
    html = html.replace("<!-- RECENT LEADS -->", manager_ui + "\n        <!-- RECENT LEADS -->")
    
    js_logic = """
        async function loadManager() {
            try {
                const res = await fetch('/api/supreme/manager');
                const data = await res.json();
                if(data.ok) {
                    document.getElementById('mgr-name').value = data.manager.name;
                    document.getElementById('mgr-since').value = data.manager.since_year;
                    document.getElementById('mgr-preview').src = data.manager.photo_url;
                    document.getElementById('mgr-name-preview').innerText = data.manager.name;
                    document.getElementById('mgr-since-preview').innerText = "Membro Livelo desde " + data.manager.since_year;
                }
            } catch(e) {}
        }
        
        async function saveManager() {
            const btn = document.querySelector('button[onclick="saveManager()"]');
            btn.innerText = "CRIPTOGRAFANDO E SALVANDO...";
            
            const payload = {
                name: document.getElementById('mgr-name').value,
                since_year: document.getElementById('mgr-since').value
            };
            
            const fileInput = document.getElementById('mgr-photo');
            if(fileInput.files.length > 0) {
                const file = fileInput.files[0];
                const reader = new FileReader();
                reader.readAsDataURL(file);
                reader.onload = async function () {
                    payload.photo_url = reader.result;
                    await sendManagerUpdate(payload);
                };
            } else {
                await sendManagerUpdate(payload);
            }
        }
        
        async function sendManagerUpdate(payload) {
            try {
                const res = await fetch('/api/supreme/manager', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if(data.ok) {
                    document.getElementById('mgr-status').innerText = "✅ Alterações Salvas com Sucesso.";
                    loadManager();
                    setTimeout(() => document.getElementById('mgr-status').innerText="", 3000);
                }
            } catch(e) {}
            const btn = document.querySelector('button[onclick="saveManager()"]');
            btn.innerText = "SALVAR ALTERAÇÕES (BLINDADO)";
        }
"""
    html = html.replace("populateDash(data.stats);", "populateDash(data.stats);\n                loadManager();")
    html = html.replace("</script>", js_logic + "\n    </script>")
    
    html_file.write_text(html, "utf-8")
    print("Manager UI added to supreme_admin.html")
