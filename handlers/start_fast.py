# start_fast.py
from util.fasting import start_fast
from telebot import TeleBot
from db import has_active_session , get_active_session, complete_session, add_star
from util.logger import log
from datetime import timedelta
def handle_start_fast(bot: TeleBot, chat_id: int, text: str):
    
    log(f"starting start_fast", level="WARNING", feature="start_fast")
    parts = text.split()
    
    gmt3_start_time = start_time + timedelta(hours=3)
    gmt3_stop_time = stop_time + timedelta(hours=3)
    
    if len(parts) == 2 and parts[1].isdigit():
        fast_hours = int(parts[1])

        if has_active_session(chat_id):
            bot.send_message(chat_id, "⏳ You already have an active fasting session.")
        else:
            start_time, stop_time, fast_hours = start_fast(chat_id, fast_hours)
            bot.send_message(
                chat_id,
                f"✅ Fast started at <b>{start_time.strftime('%Y-%m-%d %H:%M UTC')}</b> for <b>{fast_hours} hours</b>.\n"\
                f"⏰ It will end at <b>{stop_time.strftime('%Y-%m-%d %H:%M UTC')}</b>.",
                parse_mode='HTML'
            )
    else:
        bot.send_message(
            chat_id,
            "❗ Please provide the fasting hours like this:\n"
            "<code>/start_fast 16</code>, where 16 is the number of hours \n\n"
            "ℹ️ You can also update your profile (/update_profile) to store your default fast hours.",
            parse_mode='HTML'
        )
