from db import get_connection
from telebot import TeleBot
from html import escape
from db import get_connection
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from util.logger import log


# Step 1: Ask which field to update
from telebot.types import ReplyKeyboardRemove

# Global state to track which step a user is in
user_update_state = {}

def start_profile_update(bot, name ,chat_id):
    # Remove keyboard to allow free text input
    bot.send_message(
        chat_id,
        "📝 What would you like to update?\nYou can type: gender, weight, height, email, or phone.",
        reply_markup=ReplyKeyboardRemove()
    )
    user_update_state[chat_id] = {'step': 'choose_field'}

# Step 2: Handle user reply
def handle_profile_update_reply(bot, message):
    chat_id = message.chat.id
    state = user_update_state.get(chat_id)

    if not state:
        return

    step = state['step']
    text = message.text.strip().lower()

    if step == 'choose_field':
        if text in ['gender', 'weight', 'height', 'email', 'phone']:
            user_update_state[chat_id] = {
                'step': 'awaiting_value',
                'field': text
            }
            bot.send_message(chat_id, f"Enter your new {text}:")
        else:
            bot.send_message(chat_id, "❌ Invalid choice. Please use /update_profile again.")
            user_update_state.pop(chat_id, None)

    elif step == 'awaiting_value':
        field = state['field']
        value = text
        save_to_db(chat_id, field, value)
        bot.send_message(chat_id, f"✅ Your {field} has been updated.")
        user_update_state.pop(chat_id, None)


def save_to_db(chat_id, field, value):
    from db import get_connection  # assuming get_connection is in db.py

    # Simple logger
    def log_error(msg):
        with open("/home/smiles/public_html/api/fastbuddy/bot-log.txt", "a") as f:
            timestamp = (datetime.utcnow() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] [ERROR save_to_db] {msg}\n")

    allowed_fields_users = ['email', 'phone']
    allowed_fields_profile = ['weight', 'height', 'gender']

    if field not in allowed_fields_users + allowed_fields_profile:
        log_error(f"Rejected unknown field: {field}")
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # ✅ Ensure user exists
        cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (chat_id,))
        user = cursor.fetchone()

        if not user:
            # Auto-register user with empty name
            cursor.execute(
                "INSERT INTO users (telegram_id, created_at, updated_at) VALUES (%s, NOW(), NOW())",
                (chat_id,)
            )
            conn.commit()
            user_id = cursor.lastrowid
        else:
            user_id = user[0]

        if field in allowed_fields_users:
            cursor.execute(
                f"UPDATE users SET {field} = %s, updated_at = NOW() WHERE id = %s",
                (value, user_id)
            )
        else:
            # Ensure profile exists
            cursor.execute("SELECT id FROM user_profile WHERE user_id = %s", (user_id,))
            profile = cursor.fetchone()

            if field == 'weight':
                column = 'weight_kgs'
            elif field == 'height':
                column = 'height_cm'
            else:
                column = field  # gender, etc.

            if profile:
                cursor.execute(
                    f"UPDATE user_profiles SET {column} = %s, updated_at = NOW() WHERE user_id = %s",
                    (value, user_id)
                )
            else:
                cursor.execute(
                    f"INSERT INTO user_profiles (user_id, {column}, created_at, updated_at) VALUES (%s, %s, NOW(), NOW())",
                    (user_id, value)
                )

        conn.commit()

    except Exception as e:
        log("Missing field in profile update", level="WARNING", feature="view_profile")
        log_error(str(e))
    finally:
        cursor.close()
        conn.close()