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

    # Compare against current time +3 GMT (Kenya time)
    now_gmt3 = datetime.utcnow() + timedelta(hours=3)

    if stop_time >= now_gmt3:
        complete_session(session['id'])
        add_star(chat_id)
        bot.send_message(chat_id, "🎉 Congratulations! You've completed your fast and earned a ⭐️ star!")
    else:
        complete_session(session['id'])
        bot.send_message(chat_id, "⏱ You stopped your fast early. Stay strong and try again next time!")