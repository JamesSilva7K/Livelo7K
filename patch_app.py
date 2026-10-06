import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# I will add the bot-gateway route right before @app.route('/health') near the end.
gateway_code = """
@app.route("/api/internal/bot-gateway", methods=["POST"])
def api_bot_gateway():
    secret = os.environ.get("BOT_SECRET", "livelo_bot_secret_2026")
    if request.headers.get("X-Bot-Secret", "") != secret:
        return jsonify({"ok": False, "error": "Unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    action = data.get("action")
    payload = data.get("payload", {})
    db = get_db()
    
    if action == "get_config":
        rows = db.execute("SELECT key, value FROM sys_config").fetchall()
        return jsonify({"ok": True, "config": {r["key"]: r["value"] for r in rows}})
        
    elif action == "set_config":
        for k, v in payload.items():
            db.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES (?, ?)", (k, v))
        db.commit()
        return jsonify({"ok": True})
        
    elif action == "get_leads":
        limit = payload.get("limit", 10)
        rows = db.execute("SELECT * FROM leads ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return jsonify({"ok": True, "leads": [dict(r) for r in rows]})
        
    elif action == "get_payments":
        limit = payload.get("limit", 10)
        rows = db.execute("SELECT * FROM payments ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return jsonify({"ok": True, "payments": [dict(r) for r in rows]})
        
    return jsonify({"ok": False, "error": "Unknown action"}), 400

"""

if "api_bot_gateway" not in content:
    content = content.replace("@app.route('/health')", gateway_code + "\n@app.route('/health')")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Patched app.py successfully!")
