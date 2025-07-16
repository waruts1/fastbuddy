# handlers/status.py

from datetime import datetime, timedelta
from db import get_full_user_profile, get_active_session, get_recent_sessions, get_completed_fast_hours_this_week
from telebot import TeleBot

def handle_status(bot: TeleBot, chat_id: int):
    try:
        user, profile = get_full_user_profile(chat_id)

        if not user:
            bot.send_message(chat_id, "⚠️ You are not registered yet. Use /update_profile to start.")
            return

        # Active fasting session?
        active_session = get_active_session(chat_id)
        is_fasting = bool(active_session)

        # Check profile completeness
        required_fields = ['gender', 'weight_kgs', 'height_cm', 'fast_hours']
        profile_complete = profile and all(profile.get(f) for f in required_fields)

        # Weekly fasting hours
        total_hours = get_completed_fast_hours_this_week(chat_id)

        # Last session info
        latest = get_recent_sessions(chat_id, limit=1)
        if latest:
            last = latest[0]
            last_session = f"{last['start_time'].strftime('%Y-%m-%d %H:%M')} for {last['fast_hours']}h"
        else:
            last_session = "None"

        # Message to user
        msg = f"""
📊 <b>Your FastBuddy Status</b>

🔥 Fasting Now: {'✅ Yes' if is_fasting else '❌ No'}
📋 Profile Complete: {'✅ Yes' if profile_complete else '❌ No'}
🕓 Total Hours Fasted This Week: <b>{total_hours} hours</b>
⏰ Last Session: {last_session}
"""
        bot.send_message(chat_id, msg.strip(), parse_mode='HTML')

    except Exception as e:
        from util.logger import log
        bot.send_message(chat_id, "❌ Could not fetch your status.")
        log(f"[handle_status error] {str(e)}", level="ERROR", feature="status")
