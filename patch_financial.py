import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Add get_financeiro to the bot_gateway
gateway_patch = """
    elif action == "get_payments":
        limit = payload.get("limit", 10)
        rows = db.execute("SELECT * FROM payments ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return jsonify({"ok": True, "payments": [dict(r) for r in rows]})
        
    elif action == "get_financeiro":
        total_leads = db.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        pagos = db.execute("SELECT SUM(amount), COUNT(*) FROM payments WHERE status='approved' OR status='pago'").fetchone()
        pendentes = db.execute("SELECT COUNT(*) FROM payments WHERE status='pending'").fetchone()[0]
        
        stats = {
            "qtd_leads": total_leads,
            "total_pago": f"{pagos[0] or 0:.2f}",
            "qtd_pago": pagos[1] or 0,
            "qtd_pendente": pendentes
        }
        return jsonify({"ok": True, "stats": stats})
"""

content = re.sub(r'    elif action == "get_payments":.*?return jsonify\(\{"ok": True, "payments": \[dict\(r\) for r in rows\]\}\)', gateway_patch, content, flags=re.DOTALL)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Added get_financeiro to app.py!")
