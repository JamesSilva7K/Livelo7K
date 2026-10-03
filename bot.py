import telebot
from telebot.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton, MenuButtonWebApp
import sqlite3

# ==========================================
# CONFIGURAÇÕES DO BOT
# ==========================================
import os
BOT_TOKEN = os.environ.get("BOT_TOKEN", "SEU_TOKEN_AQUI")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID", "SEU_ID_AQUI")

# Lista de IDs de Admins de Suporte (que só verão os leads)
SUPPORT_ADMINS = ["ID_SUPORTE_1", "ID_SUPORTE_2"] 

# ATENÇÃO: Web Apps do Telegram EXIGEM HTTPS. 
# Se estiver rodando local, use o ngrok (ex: ngrok http 5050) e cole o link HTTPS aqui:
WEBAPP_URL_SUPREMO = "https://SEU_LINK_NGROK_AQUI/tg_webapp"
WEBAPP_URL_LEADS = "https://SEU_LINK_NGROK_AQUI/tg_webapp_leads"

bot = telebot.TeleBot(BOT_TOKEN)

# ==========================================
# COMANDOS
# ==========================================
@bot.message_handler(commands=['start', 'menu', 'painel'])
def send_welcome(message):
    chat_id = str(message.chat.id)
    
    # ── ACESSO: ADMIN SUPREMO ──
    if chat_id == ADMIN_CHAT_ID:
        bot.set_chat_menu_button(
            message.chat.id,
            MenuButtonWebApp(type="web_app", text="Painel Supremo", web_app=WebAppInfo(url=WEBAPP_URL_SUPREMO))
        )
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("👑 Abrir Painel Supremo", web_app=WebAppInfo(url=WEBAPP_URL_SUPREMO)))
        
        texto = (
            "👑 *Painel Admin Supremo — Livelo*\n\n"
            "Acesso total concedido. Você tem o controle de todo o sistema."
        )
        bot.send_message(message.chat.id, texto, parse_mode="Markdown", reply_markup=markup)
        
    # ── ACESSO: ADMIN DE SUPORTE ──
    elif chat_id in SUPPORT_ADMINS:
        bot.set_chat_menu_button(
            message.chat.id,
            MenuButtonWebApp(type="web_app", text="Gestão de Leads", web_app=WebAppInfo(url=WEBAPP_URL_LEADS))
        )
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📊 Acessar Gestão de Leads", web_app=WebAppInfo(url=WEBAPP_URL_LEADS)))
        
        texto = (
            "🛡️ *Painel de Suporte — Livelo*\n\n"
            "Bem-vindo! Você tem acesso exclusivo ao relatório profundo dos Leads.\n"
            "Acompanhe quem pagou o frete e quem abandonou o procedimento em tempo real."
        )
        bot.send_message(message.chat.id, texto, parse_mode="Markdown", reply_markup=markup)
        
    # ── ACESSO: NEGADO ──
    else:
        bot.send_message(message.chat.id, "⛔ Acesso negado. Você não tem permissão para usar este bot.")

if __name__ == "__main__":
    print("🤖 Bot Telegram com WebApp iniciado.")
    bot.infinity_polling()
