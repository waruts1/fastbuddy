import os
import sys
from flask import Flask, request
from dotenv import load_dotenv
import telebot
from html import escape
from datetime import datetime, timedelta
from util.logger import log
from handlers.menu import get_menu_text ,send_main_menu
from handlers.knowledge_base import get_knowledge_base_text
from handlers.start_fast import handle_start_fast
from handlers.stop_fast import handle_stop_fast
from handlers.view_profile import handle_view_profile
from handlers.calorie_lookup import get_nutrition_info
from handlers.update_profile import start_profile_update , handle_profile_update_reply
from handlers.support import handle_support_reply
import json


# Load environment variables
load_dotenv()
now = datetime.utcnow()
# Flask app
app = Flask(__name__)
user_update_state = {}
# Telegram bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Missing BOT_TOKEN in environment.")
bot = telebot.TeleBot(BOT_TOKEN)
pending_stop_confirmation = {}
# Add current dir to path
sys.path.insert(0, os.path.dirname(__file__))

# Import database helpers (or fallbacks)
# try:
#     from db import user_exists, save_user , has_active_session , get_active_session, complete_session, add_star
# except ImportError:
#     def user_exists(user_id): return False
#     def save_user(user_id, name): pass

# --- Web Routes ---
# def get_feedback_keyboard():
#     markup = InlineKeyboardMarkup()
#     markup.add(InlineKeyboardButton("Suggest a Feature", callback_data='feature'))
#     markup.add(InlineKeyboardButton("File a Complaint", callback_data='complaint'))
#     markup.add(InlineKeyboardButton("Report a Bug", callback_data='bug'))
#     return markup
    
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
        name = escape(message.from_user.first_name or "there")

        if message:
            chat_id = message.chat.id
            text = message.text.strip().lower()

            # Step 1: Handle pending stop confirmation first
            if chat_id in pending_stop_confirmation:
                response = text.lower()
                if response in ['yes', 'y']:
                    session_id = pending_stop_confirmation.pop(chat_id)
                    complete_session(session_id)
                    bot.send_message(chat_id, "⏱ You stopped your fast early. Stay strong and try again next time!")
                elif response in ['no', 'n']:
                    pending_stop_confirmation.pop(chat_id)
                    bot.send_message(chat_id, "👍 Keep going! You're doing great!")
                else:
                    bot.send_message(chat_id, "❓ Please reply with 'Yes' or 'No'")
                return "ok", 200  # stop further processing

            # Step 2: Regular command handling
            if text == '/start':
                bot.send_message(chat_id, f"Hi <b>{name}</b>, welcome to <b>FastBuddy</b> 🚀", parse_mode='HTML')
                bot.send_message(chat_id, "/help - display commands to assist 🚀", parse_mode='HTML')

            elif text == '/menu':
                send_main_menu(bot, chat_id)

            elif text == '/help':
                bot.send_message(chat_id, get_menu_text(), parse_mode='HTML')

            elif text.startswith('/start_fast'):
                handle_start_fast(bot, chat_id, text)

            elif text == '/stop_fast':
                handle_stop_fast(bot, chat_id)

            elif text == '/knowledge_base':
                kb_text = get_knowledge_base_text()
                bot.send_message(chat_id, kb_text, parse_mode='HTML')

            elif text.startswith('/calories'):
                parts = text.split(maxsplit=1)
                if len(parts) == 2:
                    food_name = parts[1]
                    reply = get_nutrition_info(food_name)
                    bot.send_message(chat_id, reply, parse_mode='HTML')
                else:
                    bot.send_message(chat_id, "Usage: /calories [food name]\nExample: /calories banana", parse_mode='HTML')

            elif text == '/support':
                send_support_menu(bot, chat_id)

            elif text == '/view_profile':
                handle_view_profile(bot, chat_id)

            elif text == '/update_profile':
                start_profile_update(bot, name, chat_id)
            
            elif text == '/status':
                handle_status(bot, chat_id)

            elif text.startswith('/'):  # Unrecognized slash command
                bot.send_message(chat_id, "❌ Invalid option. Please choose from the menu below.")
                bot.send_message(chat_id, get_menu_text(), parse_mode='HTML')

            elif chat_id in user_update_state:
                handle_profile_update_reply(bot, message)

            else:
                handle_support_reply(bot, message)

        return "ok", 200

    except Exception as e:
        log(f"[App.py ERROR webhook] {str(e)}", level="WARNING", feature="telegram_webhook")
        return "error", 500

# WSGI entry point
application = app

if __name__ == '__main__':
    app.run(debug=True)
