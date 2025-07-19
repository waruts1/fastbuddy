from db import get_active_session, update_start_time
from datetime import datetime, timedelta
from telebot import TeleBot

def handle_edit_fast(bot: TeleBot, chat_id: int, text: str):
    session = get_active_session(chat_id)

    if not session:
        bot.send_message(chat_id, "⚠️ You don’t have an active fasting session.")
        return

    parts = text.split()
    if len(parts) < 2:
        bot.send_message(chat_id, "⛔ Please use the format:\n/edit_fast YYYY-MM-DD HH:MM")
        return

    try:
        new_start_time = datetime.strptime(parts[1] + " " + parts[2], "%Y-%m-%d %H:%M")
    except Exception:
        bot.send_message(chat_id, "❌ Invalid datetime format.\nPlease use:\n/edit_fast 2025-07-17 08:06")
        return

    update_start_time(session['telegram_id'], new_start_time)
    bot.send_message(chat_id, f"✅ Start time updated to {new_start_time.strftime('%Y-%m-%d %H:%M')}")
