import re

def update_app_py():
    with open('app.py', 'r', encoding='utf-8') as f:
        code = f.read()

    # 1. Add STEP_ACTION icon
    code = code.replace('"INFO_ADDED": "📝"', '"INFO_ADDED": "📝",\n            "STEP_ACTION": "🖱️"')

    # 2. Add /api/log-action route
    log_action_route = """@app.route("/api/log-action", methods=["POST"])
def api_log_action():
    data = request.get_json() or {}
    sid = sanitize(data.get("session_id", ""), 40)
    action = sanitize(data.get("action", ""), 100)
    details = sanitize(data.get("details", ""), 200)
    
    # Store action in DB or just forward to TG
    if sid and action:
        texto = f"{action}" + (f": {details}" if details else "")
        import threading
        threading.Thread(target=send_telegram_notify, args=(sid, f"STEP_ACTION: {texto}")).start()
    return jsonify({"ok": True})
"""
    if "api_log_action" not in code:
        code = code.replace("@app.route('/health')", log_action_route + "\n@app.route('/health')")

    # 3. Security Headers Middleware (Military Shielding)
    security_headers = """
@app.after_request
def apply_security_headers(response):
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    # Basic Anti-Bot logic could go here
    return response
"""
    if "apply_security_headers" not in code:
        code = code.replace("app = Flask(__name__)", "app = Flask(__name__)\n" + security_headers)

    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)

update_app_py()
print("App updated with log-action and security headers")
