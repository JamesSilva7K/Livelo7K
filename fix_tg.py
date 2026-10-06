tg_path = "templates/tg_webapp.html"
with open(tg_path, "r", encoding="utf-8") as f:
    tg_html = f.read()

# 1. Fix the fetch URL
tg_html = tg_html.replace("fetch('/api/tg/auth'", "fetch('/api/tg_auth'")

# 2. Fix the Geo UI string replacement since regex failed
old_lead_card = """          <div class="lead-card" onclick="tg.showAlert('CPF: ${l.cpf}\\nNome: ${l.nome}\\nWhatsApp: ${l.whatsapp || '-'}')">
            <div>
              <div class="l-name">${l.nome}</div>
              <div class="l-doc">${l.cpf} • R$ ${l.renda || '0'}</div>
            </div>
            <div class="badge ${st}">${stTxt}</div>
          </div>"""

new_lead_card = """          <div class="lead-card" onclick="tg.showAlert('CPF: ${l.cpf}\\nNome: ${l.nome}\\nWhatsApp: ${l.whatsapp || '-'}\\nIP: ${l.ip || '-'}\\nGeo: ${l.location || '-'}')">
            <div>
              <div class="l-name">${l.nome}</div>
              <div class="l-doc">${l.cpf} • R$ ${l.renda || '0'}</div>
              <div style="font-size:0.65rem; color:var(--text-dim); margin-top:4px;">📍 ${l.location || l.ip || 'Sem Localização'}</div>
            </div>
            <div class="badge ${st}">${stTxt}</div>
          </div>"""

tg_html = tg_html.replace(old_lead_card, new_lead_card)

with open(tg_path, "w", encoding="utf-8") as f:
    f.write(tg_html)

print("Fixed tg_webapp.html!")
