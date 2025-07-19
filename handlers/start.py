from db import user_exists, save_user, get_user_profile
from html import escape
from handlers.menu import send_main_menu

def handle_start(bot, message):
    chat_id = message.chat.id
    telegram_user = message.from_user

    name = escape(telegram_user.first_name or "there")

    # Check if user exists
    if not user_exists(chat_id):
        save_user(chat_id, telegram_user.first_name + " " + telegram_user.last_name, telegram_user.username)
        bot.send_message(chat_id, f"👋 Hi <b>{name}</b>, welcome to <b>FastBuddy</b><br>You may we update your profile 🚀", parse_mode='HTML')
        send_main_menu(bot, chat_id)
    else:
        bot.send_message(chat_id, f"👋 Hi again <b>{name}</b>!", parse_mode='HTML')
        send_main_menu(bot, chat_id)
    # Fetch user profile
    profile = get_user_profile(chat_id)

    # If profile is missing, prompt user to update it
    if not profile:
        bot.send_message(chat_id, "⚠️ You haven't set up your profile yet. Please use /update_profile to complete it.", parse_mode='HTML')

    send_main_menu(bot, chat_id)