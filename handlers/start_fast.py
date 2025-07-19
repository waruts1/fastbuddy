# start_fast.py
from util.fasting import start_fast
from telebot import TeleBot
from db import has_active_session , get_active_session, complete_session, add_star ,get_user_profile
from util.logger import log
from datetime import timedelta

def handle_start_fast(bot: TeleBot, chat_id: int, text: str):
    parts = text.split()
    profile = get_user_profile(chat_id)

    if len(parts) == 2 and parts[1].isdigit():
        fast_hours = int(parts[1])
        source = "custom"
    elif profile and profile.get('fast_hours') is not None:
        fast_hours = profile['fast_hours']
        source = "default"
    else:
        bot.send_message(
        chat_id,
        "❗ Please provide fasting hours like this:\n"
        "<code>/start_fast 16</code>\n\n"
        "ℹ️ Or update your profile to set your default fast hours using /update_profile",
        parse_mode='HTML'
    )
        return

    # Start the fast
    start_time, stop_time, fast_hours = start_fast(chat_id, fast_hours)

    # Format time to GMT+3
    gmt3_start = start_time
    gmt3_stop = stop_time

    # Notify user
    note = "🗓 Using your profile's default fasting hours." if source == "default" else "⏱ Using your custom fasting hours."

    bot.send_message(
        chat_id,
        f"✅ Fast started at <b>{gmt3_start.strftime('%Y-%m-%d %H:%M')}</b> for <b>{fast_hours} hours</b>.\n\n"
        f"⏰ It will end at <b>{gmt3_stop.strftime('%Y-%m-%d %H:%M')}</b>.\n\n"
        f"{note}\n\n"
        f"🛠 You can edit the start time anytime using:\n\n"
        f"<code>/edit_fast YYYY-MM-DD HH:MM</code>\n\n"
        f"Example: <code>/edit_fast {gmt3_start.strftime('%Y-%m-%d')} 08:06</code>",

    parse_mode='HTML'
    )
