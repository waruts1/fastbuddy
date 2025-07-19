from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import os
from dotenv import load_dotenv
# Load environment variables
load_dotenv()
admin_chat_id = os.getenv("ADMIN_CHAT_ID") # Replace with your Telegram user ID

# Memory to track who is sending feedback or contacting
user_support_state = {}

def send_support_menu(bot, chat_id):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.row(KeyboardButton("📩 Feedback"), KeyboardButton("📞 Contact Us"))
    keyboard.row(KeyboardButton("❌ Cancel"))
    markup.row(KeyboardButton("/menu"))
    bot.send_message(chat_id, "How can we help you?", reply_markup=keyboard)
    user_support_state[chat_id] = "awaiting_choice"


def handle_support_reply(bot, message):
    chat_id = message.chat.id
    text = message.text.strip()

    state = user_support_state.get(chat_id)

    if state == "awaiting_choice":
        if text == "📩 Feedback":
            user_support_state[chat_id] = "sending_feedback"
            bot.send_message(chat_id, "Please type your feedback message:")
        elif text == "📞 Contact Us":
            user_support_state[chat_id] = "sending_contact"
            bot.send_message(chat_id, "Please type your message and we’ll get back to you:")
        elif text == "❌ Cancel":
            bot.send_message(chat_id, "Cancelled. Let us know if you need help.")
            user_support_state.pop(chat_id, None)
        else:
            bot.send_message(chat_id, "❌ Invalid option. Please choose from the menu again.")
            send_support_menu(bot, chat_id)

    elif state == "sending_feedback":
        forward = f"📝 <b>Feedback from {chat_id}:</b>\n\n{text}"
        bot.send_message(admin_chat_id, forward, parse_mode='HTML')
        bot.send_message(chat_id, "✅ Thank you for your feedback!")
        user_support_state.pop(chat_id, None)

    elif state == "sending_contact":
        forward = f"📞 <b>Support Message from {chat_id}:</b>\n\n{text}"
        bot.send_message(admin_chat_id, forward, parse_mode='HTML')
        bot.send_message(chat_id, "✅ We’ve received your message. We’ll get back to you soon.")
        user_support_state.pop(chat_id, None)
