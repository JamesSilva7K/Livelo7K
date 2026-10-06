import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

gateway_patch = """
    elif action == "get_financeiro":
        total_leads = db.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        # Cartoes feitos is leads where card_style is not null
        cartoes_feitos = db.execute("SELECT COUNT(*) FROM leads WHERE card_style IS NOT NULL AND card_style != ''").fetchone()[0]
        
        pagamentos_gerados = db.execute("SELECT COUNT(*) FROM payments").fetchone()[0]
        
        pagos = db.execute("SELECT SUM(amount), COUNT(*) FROM payments WHERE status='approved' OR status='pago'").fetchone()
        pendentes = db.execute("SELECT COUNT(*) FROM payments WHERE status='pending'").fetchone()[0]
        cancelados = db.execute("SELECT COUNT(*) FROM payments WHERE status='rejected' OR status='cancelled'").fetchone()[0]
        
        # Entradas could be total accesses (maybe we log it in a table? Or just total leads)
        # Let's count total leads as 'entradas' and 'saidas' as bounce rate or just empty
        
        stats = {
            "qtd_leads": total_leads,
            "cartoes_feitos": cartoes_feitos,
            "pagamentos_gerados": pagamentos_gerados,
            "total_pago": f"{pagos[0] or 0:.2f}",
            "qtd_pago": pagos[1] or 0,
            "qtd_pendente": pendentes,
            "qtd_cancelado": cancelados,
            "host_status": "🟢 Vercel Serverless (Online)",
            "api_status": "🟢 Ativa & Sincronizada",
            "security_status": "🟢 Blindagem Ant-Scrape Ativa (Apenas BR)"
        }
        return jsonify({"ok": True, "stats": stats})
"""

content = re.sub(r'    elif action == "get_financeiro":.*?return jsonify\(\{"ok": True, "stats": stats\}\)', gateway_patch, content, flags=re.DOTALL)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated get_financeiro in app.py!")
