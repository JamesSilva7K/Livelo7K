import telebot
from telebot.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton, MenuButtonWebApp
import requests
import sqlite3
import os

# ==========================================
# CONFIGURACOES DO BOT
# ==========================================
BOT_TOKEN      = os.environ.get("BOT_TOKEN",      "SEU_TOKEN_AQUI")
ADMIN_CHAT_ID  = os.environ.get("ADMIN_CHAT_ID",  "SEU_ID_AQUI")
BOT_SECRET     = os.environ.get("BOT_SECRET",     "livelo_bot_secret_2026")
BASE_URL       = os.environ.get("RENDER_EXTERNAL_URL", "http://localhost:5050")
WEBAPP_URL     = f"{BASE_URL}/tg_webapp"
API_BASE       = BASE_URL

suporte_raw    = os.environ.get("BASIC_ADMIN_IDS", "")
SUPPORT_ADMINS = [x.strip() for x in suporte_raw.split(",")] if suporte_raw else ["ID_SUPORTE_1"]

bot = telebot.TeleBot(BOT_TOKEN)

def is_supreme(message):
    return str(message.chat.id) == str(ADMIN_CHAT_ID)

def set_logo_via_api(logo_url):
    try:
        r = requests.post(
            f"{API_BASE}/api/internal/set-logo",
            json={"logo_url": logo_url},
            headers={"X-Bot-Secret": BOT_SECRET},
            timeout=8
        )
        return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

@bot.message_handler(commands=["start", "menu", "painel"])
def send_welcome(message):
    chat_id = str(message.chat.id)
    if chat_id == ADMIN_CHAT_ID:
        bot.set_chat_menu_button(
            message.chat.id,
            MenuButtonWebApp(type="web_app", text="Painel Supremo", web_app=WebAppInfo(url=WEBAPP_URL))
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("👑 Abrir Painel Supremo", web_app=WebAppInfo(url=WEBAPP_URL)))
        texto = (
            "👑 *Painel Admin Supremo — Livelo*\n\n"
            "Acesso total concedido.\n\n"
            "📋 *Comandos de Logo:*\n"
            "/logo — Ver instrucoes\n"
            "/logo\\_url `<link>` — Definir logo por URL\n"
            "/logo\\_reset — Restaurar logo padrao\n"
            "/logo\\_atual — Ver logo atual"
        )
        bot.send_message(message.chat.id, texto, parse_mode="Markdown", reply_markup=markup)
    elif chat_id in SUPPORT_ADMINS:
        bot.set_chat_menu_button(
            message.chat.id,
            MenuButtonWebApp(type="web_app", text="Gestao de Leads", web_app=WebAppInfo(url=WEBAPP_URL))
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📊 Acessar Gestao de Leads", web_app=WebAppInfo(url=WEBAPP_URL)))
        bot.send_message(message.chat.id,
            "🛡️ *Painel de Suporte — Livelo*\n\nAcompanhe os leads em tempo real.",
            parse_mode="Markdown", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Acesso negado.")

@bot.message_handler(commands=["logo"])
def cmd_logo_help(message):
    if not is_supreme(message):
        bot.send_message(message.chat.id, "Acesso negado.")
        return
    bot.send_message(message.chat.id,
        "🎨 *Alterar Logo da Pagina de Leads*\n\n"
        "1 — Envie uma *foto* diretamente aqui\n"
        "2 — Use `/logo_url https://link.com/logo.png`\n\n"
        "Para restaurar o padrao: /logo\\_reset\n"
        "Para ver a logo atual: /logo\\_atual",
        parse_mode="Markdown")

@bot.message_handler(commands=["logo_url"])
def cmd_logo_url(message):
    if not is_supreme(message):
        bot.send_message(message.chat.id, "Acesso negado.")
        return
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2 or not parts[1].startswith("http"):
        bot.send_message(message.chat.id, "Uso: /logo\\_url https://link-da-imagem.com/logo.png", parse_mode="Markdown")
        return
    logo_url = parts[1].strip()
    bot.send_message(message.chat.id, "Atualizando logo...")
    result = set_logo_via_api(logo_url)
    if result.get("ok"):
        bot.send_message(message.chat.id,
            f"Logo atualizada!\n{logo_url}\n\nTodos os leads verao a nova logo.",
            parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, f"Erro: {result.get('error', 'desconhecido')}")

@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    if not is_supreme(message):
        return
    bot.send_message(message.chat.id, "Processando imagem...")
    photo    = message.photo[-1]
    file_info = bot.get_file(photo.file_id)
    file_url  = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
    try:
        img_resp = requests.get(file_url, timeout=15)
        img_resp.raise_for_status()
        ext  = file_info.file_path.rsplit(".", 1)[-1] if "." in file_info.file_path else "jpg"
        fname = f"logo_tg_{photo.file_id[:10]}.{ext}"
        upload = requests.post(
            f"{API_BASE}/api/internal/set-logo-file",
            files={"logo_file": (fname, img_resp.content, f"image/{ext}")},
            headers={"X-Bot-Secret": BOT_SECRET},
            timeout=15
        )
        if upload.status_code == 404:
            result = set_logo_via_api(file_url)
        else:
            result = upload.json()
        if result.get("ok"):
            bot.send_message(message.chat.id, "Logo atualizada com sucesso!")
        else:
            bot.send_message(message.chat.id, f"Erro: {result.get('error')}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Erro: {e}")

@bot.message_handler(commands=["logo_reset"])
def cmd_logo_reset(message):
    if not is_supreme(message):
        bot.send_message(message.chat.id, "Acesso negado.")
        return
    result = set_logo_via_api("/static/images/manager_default.svg")
    if result.get("ok"):
        bot.send_message(message.chat.id, "Logo restaurada ao padrao Livelo!")
    else:
        bot.send_message(message.chat.id, f"Erro: {result.get('error')}")

@bot.message_handler(commands=["logo_atual"])
def cmd_logo_atual(message):
    if not is_supreme(message):
        bot.send_message(message.chat.id, "Acesso negado.")
        return
    try:
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "livelo.db")
        conn = sqlite3.connect(db_path)
        row  = conn.execute("SELECT value FROM sys_config WHERE key='system_logo_url'").fetchone()
        conn.close()
        url = row[0] if row else "(padrao)"
        bot.send_message(message.chat.id, f"Logo atual:\n{url}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Erro: {e}")

if __name__ == "__main__":
    print("Bot Telegram Livelo iniciado.")
    print(f"  Admin ID : {ADMIN_CHAT_ID}")
    print(f"  Base URL : {BASE_URL}")
    bot.infinity_polling()
