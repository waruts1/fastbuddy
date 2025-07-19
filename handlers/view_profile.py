from db import get_connection , get_user_profile_data , user_exists
from html import escape
from util.logger import log
def handle_view_profile(bot, chat_id):
    try:
        user, profile = get_user_profile_data(chat_id)
        log(f"[view profile handler INFO] {profile}", level="ERROR", feature="view_profile")
        if not profile:
            bot.send_message(chat_id, "⚠️ You are not registered yet. Use /update_profile first.")
            return

        # Build profile response
        msg_lines = [f"👤 <b>Your Profile Info</b>"]
        msg_lines.append(f"Phone: {escape(user.get('phone') or 'Not set')}")
        msg_lines.append(f"Email: {escape(user.get('email') or 'Not set')}")

        if profile:
            msg_lines.append(f"Gender: {escape(profile.get('gender') or 'Not set')}")
            msg_lines.append(f"Weight (kg): {profile.get('weight_kgs') or 'Not set'}")
            msg_lines.append(f"Height (cm): {profile.get('height_cm') or 'Not set'}")
            msg_lines.append(f"Preferred Fast Hours: {profile.get('fast_hours') or 'Not set'}")
        else:
            msg_lines.append("No additional profile info found.")

        message = "\n".join(msg_lines)
        bot.send_message(chat_id, message, parse_mode='HTML')

    except Exception as e:
        bot.send_message(chat_id, "❌ Could not retrieve profile info.")
        bot.send_message(chat_id, "/update_profile to add data")
        log(f"[view_profile ERROR] {str(e)}", level="ERROR", feature="view_profile")
