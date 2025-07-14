from db import get_connection
from telebot import TeleBot
from html import escape
from db import get_connection
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# Store user states
user_update_state = {}

# Step 1: Ask which field to update
from telebot.types import ReplyKeyboardRemove

def start_profile_update(bot, chat_id):
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
    conn = get_connection()
    cursor = conn.cursor()

    user_query = "SELECT id FROM users WHERE telegram_id = %s"
    cursor.execute(user_query, (chat_id,))
    user = cursor.fetchone()

    if not user:
        return

    user_id = user[0]

    if field in ['email', 'phone']:
        cursor.execute(f"UPDATE users SET {field} = %s, updated_at = NOW() WHERE id = %s", (value, user_id))
    else:
        # Ensure user_profile exists
        cursor.execute("SELECT id FROM user_profile WHERE user_id = %s", (user_id,))
        profile = cursor.fetchone()

        if profile:
            cursor.execute(f"UPDATE user_profile SET {field}_kg = %s, updated_at = NOW() WHERE user_id = %s", (value, user_id)) if field == 'weight' \
                else cursor.execute(f"UPDATE user_profile SET {field}_cm = %s, updated_at = NOW() WHERE user_id = %s", (value, user_id)) if field == 'height' \
                else cursor.execute(f"UPDATE user_profile SET {field} = %s, updated_at = NOW() WHERE user_id = %s", (value, user_id))
        else:
            cursor.execute("INSERT INTO user_profile (user_id, {0}, created_at, updated_at) VALUES (%s, %s, NOW(), NOW())".format(field), (user_id, value))

    conn.commit()
    cursor.close()
    conn.close()