from db import get_connection
from html import escape
from util.logger import log
def handle_view_profile(bot, chat_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (chat_id,))
        user = cursor.fetchone()
        
        print("View Profile " + user)
        log("Webhook received")  # INFO level by default
        log("User not found in database", level="WARNING")
        log("Critical DB failure", level="ERROR")
        if not user:
            bot.send_message(chat_id, "⚠️ You are not registered yet. Use /register first.")
            return

        # Fetch profile info
        cursor.execute("""
            SELECT gender, weight_kg, height_cm, fast_hours, phone, email
            FROM user_profiles UP
            LEFT JOIN users U ON UP.user_id = U.id
            WHERE U.telegram_id = %s
        """, (chat_id,))
        profile = cursor.fetchone()

        # Prepare message
        msg_lines = [f"👤 <b>Your Profile Info</b>"]

        # From users table
        msg_lines.append(f"Phone: {escape(user.get('phone') or 'Not set')}")
        msg_lines.append(f"Email: {escape(user.get('email') or 'Not set')}")

        # From profile table (may be None)
        if profile:
            msg_lines.append(f"Gender: {escape(profile.get('gender') or 'Not set')}")
            msg_lines.append(f"Weight (kg): {profile.get('weight_kg') or 'Not set'}")
            msg_lines.append(f"Height (cm): {profile.get('height_cm') or 'Not set'}")
            msg_lines.append(f"Preferred Fast Hours: {profile.get('fast_hours') or 'Not set'}")
        else:
            msg_lines.append("No additional profile info found.")

        message = "\n".join(msg_lines)
        bot.send_message(chat_id, message, parse_mode='HTML')

    except Exception as e:
        bot.send_message(chat_id, "❌ Could not retrieve profile info.")
        bot.send_message(chat_id, "/update_profile to add data")
        with open("/home/smiles/public_html/api/fastbuddy/bot-log.txt", "a") as f:
            f.write(f"[ERROR view_profile] {str(e)}\n")
    finally:
        cursor.close()
        conn.close()
