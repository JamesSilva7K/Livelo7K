import re

with open("bot.py", "r", encoding="utf-8") as f:
    content = f.read()

bot_patch = """
    elif data == "menu_financeiro" and is_supreme(chat_id):
        res = api_call("get_financeiro")
        if res.get("ok"):
            f = res.get("stats", {})
            txt = (
                "📈 <b>DASHBOARD SUPREMO & MÉTRICAS</b> 📈\\n"
                "──────────────────────\\n"
                f"🛡️ <b>Blindagem:</b> {f.get('security_status', '🔴 Desativada')}\\n"
                f"📡 <b>Status da API:</b> {f.get('api_status', '🔴 Offline')}\\n"
                f"🖥️ <b>Host:</b> {f.get('host_status', '🔴 Offline')}\\n"
                "──────────────────────\\n"
                f"👥 <b>Entradas (Leads):</b> {f.get('qtd_leads', 0)}\\n"
                f"💳 <b>Cartões Feitos:</b> {f.get('cartoes_feitos', 0)}\\n"
                f"🧾 <b>Pagamentos Gerados:</b> {f.get('pagamentos_gerados', 0)}\\n"
                f"💸 <b>Pagamentos Confirmados:</b> {f.get('qtd_pago', 0)}\\n"
                f"⏳ <b>Pagamentos Pendentes:</b> {f.get('qtd_pendente', 0)}\\n"
                f"❌ <b>Pagamentos Cancelados:</b> {f.get('qtd_cancelado', 0)}\\n"
                "──────────────────────\\n"
                f"💰 <b>Total Faturado Real:</b> R$ {f.get('total_pago', '0,00')}\\n"
            )
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔙 Voltar", callback_data="menu_main"))
            bot.edit_message_text(txt, chat_id, msg_id, reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, "Erro ao carregar painel financeiro.")
"""

content = re.sub(r'    elif data == "menu_financeiro" and is_supreme\(chat_id\):.*?bot\.answer_callback_query\(call\.id, "Erro ao carregar painel financeiro\."\)', bot_patch.strip('\n'), content, flags=re.DOTALL)

with open("bot.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated bot.py with advanced metrics and statuses!")
