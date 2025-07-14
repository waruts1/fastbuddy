import os
import sys
from flask import Flask, request
from dotenv import load_dotenv
import telebot
from html import escape
from datetime import datetime, timedelta
from util.logger import log
from handlers.menu import get_menu_text
from handlers.knowledge_base import get_knowledge_base_text
from handlers.start_fast import handle_start_fast
from handlers.stop_fast import handle_stop_fast
from handlers.view_profile import handle_view_profile
from handlers.update_profile import start_profile_update , handle_profile_update_reply

# Load environment variables
load_dotenv()
now = datetime.utcnow()
# Flask app
app = Flask(__name__)

# Telegram bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Missing BOT_TOKEN in environment.")
bot = telebot.TeleBot(BOT_TOKEN)

# Add current dir to path
sys.path.insert(0, os.path.dirname(__file__))

# Import database helpers (or fallbacks)
try:
    from db import user_exists, save_user , has_active_session , get_active_session, complete_session, add_star
except ImportError:
    def user_exists(user_id): return False
    def save_user(user_id, name): pass

# --- Web Routes ---

@app.route("/")
def index():
    return "âœ… FastBuddy bot is live."

@app.route("/hello")
def hello():
    return "ðŸ‘‹ Hello from FastBuddy!"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        update_json = request.get_json(force=True)
        update = telebot.types.Update.de_json(update_json)
        message = update.message

        if message:
            chat_id = message.chat.id
            text = message.text.strip().lower()

            valid_commands = [
                '/start',
                '/menu',
                '/start_fast',
                '/stop_fast',
                '/knowledge_base',
                '/view_profile',
                '/update_profile'
            ]

            if text == '/start':
                name = escape(message.from_user.first_name or "there")
                log(f"Received Message from {name}")
                bot.send_message(chat_id, f"Hi <b>{name}</b>, welcome to <b>FastBuddy</b> 🚀", parse_mode='HTML')
                bot.send_message(chat_id, get_menu_text(), parse_mode='HTML')

            elif text == '/menu':
                send_main_menu(bot, chat_id)

            elif text.startswith('/start_fast'):
                handle_start_fast(bot, chat_id, text)

            elif text == '/stop_fast':
                handle_stop_fast(bot, chat_id)

            elif text == '/knowledge_base':
                kb_text = get_knowledge_base_text()
                bot.send_message(chat_id, kb_text, parse_mode='HTML')

            elif text == '/view_profile':
                handle_view_profile(bot, chat_id)

            elif text == '/update_profile':
                start_profile_update(bot, chat_id)

            elif text.startswith('/'):  # User typed an invalid /command
                bot.send_message(chat_id, "❌ Invalid option. Please choose from the menu below.")
                bot.send_message(chat_id, get_menu_text(), parse_mode='HTML')

            else:
                handle_profile_update_reply(bot, message)

        return "ok", 200
        
    except Exception as e:
        timestamp = (datetime.utcnow() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
        with open("/home/smiles/public_html/api/fastbuddy/bot-log.txt", "a") as f:
            f.write(f"[{timestamp}] [ERROR webhook] {str(e)}\n")
    return "error", 500

# WSGI entry point
application = app

if __name__ == '__main__':
    app.run(debug=True)
