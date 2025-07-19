from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from html import escape
from util.logger import log
from database.user_states import set_user_state, get_user_state, update_user_field

def start_profile_update(bot, name, chat_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("Gender", callback_data="update_gender"),
        InlineKeyboardButton("Fast Hours", callback_data="update_fast_hours"),
        InlineKeyboardButton("Weight", callback_data="update_weight"),
        InlineKeyboardButton("Height", callback_data="update_height"),
        InlineKeyboardButton("Email", callback_data="update_email"),
        InlineKeyboardButton("Phone", callback_data="update_phone")
    )

    bot.send_message(
        chat_id,
        f"📝 Hi {name}, what would you like to update?\n\nTap one of the options below:",
        reply_markup=markup
    )

    set_user_state(chat_id, 'choose_field', None)

def handle_update_callback(bot, call):
    chat_id = call.message.chat.id
    field = call.data.replace("update_", "")
    log(f"handle_update_callback called - chat_id: {chat_id}, field: {field}", level="INFO")

    # Set state: awaiting input for this field
    set_user_state(chat_id, 'awaiting_input', field)

    bot.answer_callback_query(call.id)
    bot.send_message(
        chat_id,
        f"✏️ Please enter your new {field.replace('_', ' ').title()}:",
        reply_markup=ReplyKeyboardRemove()
    )
    return "ok", 200

def handle_input_value(bot, message):
    chat_id = message.chat.id
    new_value = message.text.strip()
    state = get_user_state(chat_id)

    log(f"handle_input_value - chat_id: {chat_id}, state: {state}", level="INFO")

    if not state or 'field' not in state or state['step'] != 'awaiting_input':
        bot.send_message(chat_id, "❌ Sorry, I wasn't expecting that. Use /update_profile to start again.")
        return "ok", 200

    field = state['field']

    # Update DB
    try:
        update_user_field(chat_id, field, new_value)
    except Exception as e:
        log(f"Failed to update user field: {str(e)}", level="ERROR")
        bot.send_message(chat_id, "❌ Failed to update your data. Please try again.")
        return "ok", 200

    bot.send_message(chat_id, f"✅ Your {field.replace('_', ' ')} has been updated to: {new_value}")

    # Clear user state after success
    set_user_state(chat_id, None, None)

    return "ok", 200
