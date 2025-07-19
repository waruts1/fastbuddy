import os
import sys
from flask import Flask, request
from dotenv import load_dotenv
import telebot
from html import escape
from datetime import datetime, timedelta
from util.logger import log
from handlers.menu import get_menu_text ,send_main_menu , send_users_submenu , send_fasting_submenu , get_feedback_keyboard
from handlers.knowledge_base import get_knowledge_base_text
from handlers.start_fast import handle_start_fast
from handlers.stop_fast import handle_stop_fast
from handlers.view_profile import handle_view_profile
from handlers.calorie_lookup import get_nutrition_info
from handlers.update_profile import start_profile_update , handle_update_callback , handle_input_value
from handlers.support import handle_support_reply , send_support_menu
from handlers.progress import handle_progress
import json
from handlers.start import handle_start
from handlers.status import handle_status
from db import get_pending_confirmation, delete_pending_confirmation, complete_session
from database.user_states import set_user_state, get_user_state
from handlers.confirm_stop import handle_stop_confirmation
from handlers.edit_fast import handle_edit_fast
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
pending_stop_confirmation = {}
user_update_profile = {}

# Add current dir to path
sys.path.insert(0, os.path.dirname(__file__))

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

        if update.callback_query:
            call = update.callback_query
            chat_id = call.message.chat.id
            data = call.data
            log(f"[Webhook INFO] Received callback: {data}", level="INFO")

            if data.startswith("update_"):
                return handle_update_callback(bot, call)

            return "ok", 200

        message = update.message
        if not message:
            return "ok", 200  # no message to handle

        chat_id = message.chat.id
        name = escape(message.from_user.first_name or "there")
        text = (message.text or "").strip().lower()

        # Handle state-based input first
        state = get_user_state(chat_id)
        if state and state.get('step') == 'awaiting_input':
            return handle_input_value(bot, message)

        # Your other command handlers...
        if text == '/update_profile':
            start_profile_update(bot, name, chat_id)
            return "ok", 200
        
        if message:
            chat_id = message.chat.id
            text = message.text.strip().lower()

        # other commands here...
        # Step 2: Regular command handling
            if text == '/start':
                handle_start(bot,message)

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
                log(f"[App.py INFO update_profile] {user_update_profile}", level="WARNING", feature="start_profile_update")
                start_profile_update(bot, name, chat_id)
            
            elif text == '/status':
                handle_status(bot, chat_id)

            elif text.startswith('/'):  # Unrecognized slash command
                bot.send_message(chat_id, "❌ Invalid option. Please choose from the menu below.")
                bot.send_message(chat_id, get_menu_text(), parse_mode='HTML')

            else:
                handle_support_reply(bot, message)

        return "ok", 200

    except Exception as e:
        log(f"[App.py ERROR webhook] {str(e)}", level="ERROR", feature="telegram_webhook")
        return "error", 500



# WSGI entry point
application = app

if __name__ == '__main__':
    app.run(debug=True)
