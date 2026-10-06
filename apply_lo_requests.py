import os

def patch_file(filepath, search, replace):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    if search in content:
        content = content.replace(search, replace)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Patched {filepath}")
    else:
        print(f"Could not find search string in {filepath}")

def main():
    bot_file = r"d:\Paginas ADS\Livelo\bot.py"
    js_file = r"d:\Paginas ADS\Livelo\static\js\main.js"
    
    # 1. Faster callbacks in bot.py
    with open(bot_file, "r", encoding="utf-8") as f:
        bot_content = f.read()
    
    # Move answer_callback_query
    bot_content = bot_content.replace(
        "    if not is_admin(chat_id, user_id):",
        "    try:\n        bot.answer_callback_query(call.id)\n    except:\n        pass\n    if not is_admin(chat_id, user_id):"
    )
    bot_content = bot_content.replace("    bot.answer_callback_query(call.id)", "")
    
    # 2. Add preview for manager
    manager_preview_code = """
    elif data == "preview_manager" and is_supreme(chat_id, user_id):
        res = api_call("get_config")
        cfg = res.get("config", {}) if res.get("ok") else {}
        name = cfg.get('mgr_name', 'Não def.')
        years = cfg.get('mgr_years', 'Não def.')
        avatar = cfg.get('mgr_avatar', '')
        
        caption = f"👩‍💼 <b>Preview da Gerente</b>\\n\\n" \\
                  f"<b>Nome:</b> {name}\\n" \\
                  f"<b>Anos na Empresa:</b> {years}\\n" \\
                  f"<i>Este será o visual exibido no painel do lead (Melhor gerente 2023-{years})</i>"
                  
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✅ Confirmar", callback_data="menu_config"))
        
        if avatar.startswith("data:image"):
            import base64
            from io import BytesIO
            img_data = base64.b64decode(avatar.split(",")[1])
            bot.send_photo(chat_id, BytesIO(img_data), caption=caption, reply_markup=markup, parse_mode="HTML")
        else:
            bot.send_message(chat_id, caption + "\\n[Sem foto carregada]", reply_markup=markup, parse_mode="HTML")
"""
    if 'data == "preview_manager"' not in bot_content:
        bot_content = bot_content.replace('    elif data == "menu_config" and is_supreme(chat_id, user_id):', manager_preview_code + '\n    elif data == "menu_config" and is_supreme(chat_id, user_id):')
        
    bot_content = bot_content.replace(
        'InlineKeyboardButton(f"🖼️ Alterar Favicon", callback_data="wait_img_favicon"),',
        'InlineKeyboardButton(f"🖼️ Alterar Favicon", callback_data="wait_img_favicon"),\n            InlineKeyboardButton("👁️ Preview Gerente", callback_data="preview_manager"),'
    )
    
    # 3. Add easy log channel setup
    log_setup_code = """
@bot.message_handler(commands=['setlog'])
def cmd_setlog(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not is_supreme(chat_id, user_id):
        return
        
    thread_id = message.message_thread_id or 0
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📢 Canal Principal", callback_data=f"bindlog_tg_log_channel_{chat_id}_{thread_id}"),
        InlineKeyboardButton("📝 Leads", callback_data=f"bindlog_tg_log_leads_{chat_id}_{thread_id}"),
        InlineKeyboardButton("💸 Pagamentos", callback_data=f"bindlog_tg_log_pagamentos_{chat_id}_{thread_id}"),
        InlineKeyboardButton("🚪 Entradas/Acessos", callback_data=f"bindlog_tg_log_acessos_{chat_id}_{thread_id}")
    )
    bot.reply_to(message, "Selecione para qual módulo este chat será o canal de Log:", reply_markup=markup)

"""
    if 'cmd_setlog' not in bot_content:
        bot_content = bot_content.replace('# --- MENU INICIAL ---', log_setup_code + '\n# --- MENU INICIAL ---')
        
    bindlog_code = """
    elif data.startswith("bindlog_") and is_supreme(chat_id, user_id):
        parts = data.split("_")
        # bindlog_tg_log_leads_-100123_0
        db_key = "_".join(parts[1:-2])
        bind_chat_id = parts[-2]
        bind_thread_id = parts[-1]
        
        updates = {db_key: bind_chat_id}
        if bind_thread_id != "0":
            updates["tg_log_thread_id"] = bind_thread_id
            
        res = api_call("set_config", updates)
        if res.get("ok"):
            bot.send_message(chat_id, f"✅ Chat {bind_chat_id} vinculado ao log '{db_key}' com sucesso!")
        else:
            bot.send_message(chat_id, f"❌ Erro ao vincular: {res.get('error')}")
"""
    if 'data.startswith("bindlog_")' not in bot_content:
        bot_content = bot_content.replace('    elif data.startswith("set_") and is_supreme(chat_id, user_id):', bindlog_code + '\n    elif data.startswith("set_") and is_supreme(chat_id, user_id):')

    with open(bot_file, "w", encoding="utf-8") as f:
        f.write(bot_content)
    print("Patched bot.py")

    # 4. Format limit to BRL in main.js
    patch_file(js_file,
               "if ($id('approved-limit')) $id('approved-limit').textContent = data.limite;",
               "if ($id('approved-limit')) $id('approved-limit').textContent = parseFloat(data.limite).toLocaleString('pt-BR', {style: 'currency', currency: 'BRL'});")

if __name__ == "__main__":
    main()
