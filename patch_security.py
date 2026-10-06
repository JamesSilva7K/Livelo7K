import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

security_patch = """
# ==========================================
# 🛡️ SECURITY & INTRUSION DETECTION
# ==========================================
@app.before_request
def security_shield():
    # Skip security for static files, API gateway, and images
    path = request.path
    if path.startswith("/static") or path.startswith("/api/internal"):
        return
        
    # Check CF-IPCountry (if on Cloudflare) or Vercel specific headers
    # Vercel provides 'x-vercel-ip-country'
    country = request.headers.get("x-vercel-ip-country")
    if not country:
        country = request.headers.get("CF-IPCountry")
        
    # Block if country is known and NOT Brazil
    if country and country.upper() != "BR":
        return "Access Denied: Region not supported.", 403

    # Bot/Scraper protection (Block Headless browsers)
    ua = request.headers.get("User-Agent", "").lower()
    suspicious_uas = ["headless", "puppeteer", "bot", "crawler", "spider", "curl", "wget"]
    if any(s in ua for s in suspicious_uas):
        return "Access Denied: Suspicious User-Agent.", 403

@app.errorhandler(404)
def page_not_found(e):
    path = request.path.lower()
    # Intrusion detection
    bad_paths = [".env", "wp-admin", "wp-login", "config.php", ".git", "phpinfo", "database.sql"]
    if any(bp in path for bp in bad_paths):
        # Someone is scanning! Send alert.
        ip = request.headers.get('x-forwarded-for', request.remote_addr)
        if ip:
            ip = ip.split(',')[0].strip()
        alert_msg = f"🚨 <b>TENTATIVA DE INVASÃO!</b> 🚨\\n\\n🌍 <b>IP Atacante:</b> <code>{ip}</code>\\n🕵️ <b>Alvo:</b> <code>{path}</code>\\n🛡️ <b>Ação:</b> IP Bloqueado automaticamente pela Blindagem."
        
        # Send to tg_log_acessos or supreme admin
        import requests
        with get_db_connection() as db:
            cfg = get_sys_config(db)
        
        chat_id = cfg.get("tg_log_acessos") or os.environ.get("ADMIN_CHAT_ID")
        if chat_id:
            requests.post(f"https://api.telegram.org/bot{os.environ.get('BOT_TOKEN')}/sendMessage",
                          json={"chat_id": chat_id, "text": alert_msg, "parse_mode": "HTML"}, timeout=5)
            
        return "Not Found", 404
        
    return "Not Found", 404
"""

# Find a good place to insert this, maybe right after app initialization or before the first route
insert_pos = content.find("@app.route")
if insert_pos != -1:
    content = content[:insert_pos] + security_patch + "\n\n" + content[insert_pos:]

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Injected Security Shield into app.py!")
