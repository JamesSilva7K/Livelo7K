import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# I will find the start of tg_webapp routes and remove them all until bot-gateway
# Wait, it's safer to just replace specific functions with empty strings using regex.
routes_to_remove = [
    r'@app\.route\("/api/tg_webapp/update", methods=\["POST"\]\)\ndef api_tg_webapp_update\(\):.*?return jsonify\(\{"ok": True\}\)',
    r'@app\.route\("/api/tg_admin_update_settings", methods=\["POST"\]\)\ndef api_tg_admin_update_settings\(\):.*?(?=@app\.route)',
    r'@app\.route\("/api/tg_admin_action", methods=\["POST"\]\)\ndef api_tg_admin_action\(\):.*?(?=@app\.route)',
    r'@app\.route\("/tg_webapp"\)\ndef tg_webapp\(\):.*?(?=@app\.route)',
    r'@app\.route\("/tg_webapp_leads"\)\ndef tg_webapp_leads\(\):.*?(?=@app\.route)',
    r'@app\.route\("/admin/login"\)\ndef admin_login\(\):.*?(?=@app\.route)',
    r'@app\.route\("/admin/tg_callback"\)\ndef admin_tg_callback\(\):.*?(?=@app\.route)',
    r'@app\.route\("/admin/logout"\)\ndef admin_logout\(\):.*?(?=@app\.route)',
    r'@app\.route\("/admin"\)\n@app\.route\("/admin/"\)\n@require_admin\ndef admin_dashboard\(\):.*?(?=@app\.route)',
    r'@app\.route\("/admin/manager", methods=\["POST"\]\)\n@require_admin\ndef admin_manager\(\):.*?(?=@app\.route)',
    r'@app\.route\("/admin/logo", methods=\["POST"\]\)\n@require_admin\ndef admin_set_logo\(\):.*?(?=@app\.route)',
    r'@app\.route\("/admin/logo", methods=\["GET"\]\)\n@require_admin\ndef admin_get_logo\(\):.*?(?=@app\.route)',
    r'@app\.route\("/admin/change-password", methods=\["POST"\]\)\n@require_admin\ndef admin_change_password\(\):.*?(?=@app\.route)',
    r'@app\.route\("/admin/api_cpf_update", methods=\["POST"\]\)\n@require_admin\ndef admin_api_cpf_update\(\):.*?(?=@app\.route)',
    r'@app\.route\("/admin/api/stats"\)\n@require_admin\ndef admin_api_stats\(\):.*?(?=@app\.route)',
    r'@app\.route\("/admin/api/leads"\)\n@require_admin\ndef admin_api_leads\(\):.*?(?=@app\.route)',
    r'@app\.route\("/admin/api/logo", methods=\["POST"\]\)\n@require_admin\ndef admin_api_logo\(\):.*?(?=@app\.route)',
    r'@app\.route\("/api/admin/bot-config".*?(?=@app\.route)',
    r'@app\.route\("/api/admin/advanced-config".*?(?=@app\.route)',
]

for pat in routes_to_remove:
    content = re.sub(pat, "\n", content, flags=re.DOTALL)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Removed all web admin routes from app.py!")
