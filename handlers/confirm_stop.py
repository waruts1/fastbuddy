# handlers/confirm_stop.py

from db import get_pending_confirmation, cancel_session, delete_pending_confirmation
from telebot import TeleBot

def handle_stop_confirmation(bot: TeleBot, chat_id: int, text: str) -> bool:
    pending = get_pending_confirmation(chat_id)
    if not pending:
        return False  # No pending confirmation; skip this handler

    if text.lower() in ['yes', 'y']:
        cancel_session(pending['session_id'], status="cancelled")
        delete_pending_confirmation(chat_id)
        bot.send_message(chat_id, "⏱ You stopped your fast early. Stay strong and try again next time!")
    elif text.lower() in ['no', 'n']:
        delete_pending_confirmation(chat_id)
        bot.send_message(chat_id, "👍 Keep going! You're doing great!")
    else:
        bot.send_message(chat_id, "❓ Please reply with 'Yes' or 'No'")
    
    return True  # We handled this message
