# handlers/status.py
from util.logger import log
from datetime import datetime, timedelta
from db import get_user_profile, get_active_session, get_recent_sessions, get_completed_fast_hours_this_week
from telebot import TeleBot

def handle_status(bot: TeleBot, chat_id: int):
    log(f"[handle_status chat_id] {chat_id}", level="INFO", feature="chat_id")
    active_session = get_active_session(chat_id)
    log(f"[handle_status session] {active_session}", level="INFO", feature="active sessions")
    try:
        profile = get_user_profile(chat_id)

        if not profile:
            bot.send_message(chat_id, "⚠️ You are not registered yet. Use /update_profile to start.")
            return

        log(f"[handle_status user] {profile}", level="INFO", feature="fetch user")
        
        # Active fasting session?
        active_session = get_active_session(chat_id)
        is_fasting = bool(active_session)

        # Check profile completeness
        required_fields = ['gender', 'weight_kgs', 'height_cms', 'fast_hours']
        profile_complete = profile and all(profile.get(f) for f in required_fields)

        # Weekly fasting hours
        total_hours = get_completed_fast_hours_this_week(chat_id)

        # Last session info
        latest = get_recent_sessions(chat_id, limit=1)
        if latest:
            last = latest[0]
            input_format = "%Y-%m-%d %H:%M:%S.%f"
            dt_object = datetime.strptime(last['start_time'], input_format)
            formatted_time = dt_object.strftime("%Y-%m-%d %I:%M %p").lower()
            last_session = f"{formatted_time} for {last['fast_hours']}h"
        else:
            last_session = "None"

        # Message to user
        msg = f"""
📊 <b>Your FastBuddy Status</b>\n
--------------------------------------
🔥 Fasting Now: {'✅ Yes' if is_fasting else '❌ No'}
📋 Profile Complete: {'✅ Yes' if profile_complete else '❌ No'}
🕓 Total Hrs Fasted This Week: <b>{total_hours} </b>
⏰ Last Session: {last_session}
"""
        bot.send_message(chat_id, msg.strip(), parse_mode='HTML')

    except Exception as e:
   
        bot.send_message(chat_id, "❌ Could not fetch your status.")
        log(f"[handle_status error] {str(e)}", level="ERROR", feature="status")
