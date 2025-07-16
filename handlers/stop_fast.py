# stop_fast.py

from datetime import datetime, timedelta
from db import get_active_session, complete_session, add_star
from telebot import TeleBot

def handle_stop_fast(bot: TeleBot, chat_id: int):
    session = get_active_session(chat_id)
    
    if not session:
        bot.send_message(chat_id, "🚫 You don’t have any active fasting session.")
        return

    stop_time_str = session['stop_time']
    
    try:
        stop_time = datetime.strptime(stop_time_str, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        stop_time = datetime.strptime(stop_time_str, "%Y-%m-%d %H:%M:%S")

    now_gmt3 = datetime.utcnow() + timedelta(hours=3)

    if stop_time >= now_gmt3:
        complete_session(session['id'])
        add_star(chat_id)
        bot.send_message(chat_id, "🎉 Congratulations! You've completed your fast and earned a ⭐️ star!")
    else:
        # Save pending confirmation state
        pending_stop_confirmation[chat_id] = session['id']
        bot.send_message(
            chat_id,
            "⚠️ You haven’t reached your fasting goal yet.\n"
            "Do you still want to stop the fast? (Yes/No)"
        )
