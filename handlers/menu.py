from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime
def get_menu_text():
    menu_title = "ðŸ“‹ <b>FastBuddy Menu</b>\n\nHere is what I can do:\n"

    menu_items = [
        "/contactus - Suggest feature or complain",
        "/start - Introduction to the bot",
        "/knowledge_base - Learn about fasting stages and benefits",
        "/menu - Show this menu again",
        "/start_fast - Register a fasting session",
        "/stop_fast - Stop your fasting session",
        "/edit_fast {datetime.now().strftime('%Y-%m-%d %I:%M')} - Edit fasting session",
        "/view_profile - View your profile",
        "/update_profile - Update your data",
        "/support - Give feedback or contact support",
        "/fasting - Fasting menu",
        "/users - User menu",
        "/progress - Get Fasting Progress⏩",
        "/status - Get Fasting Window Status"
    ]

    return menu_title + '\n'.join(menu_items)


def send_main_menu(bot, chat_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    markup.row(KeyboardButton("/fast"), KeyboardButton("/calories"))
    markup.row(KeyboardButton("/knowledge_base"), KeyboardButton("/update_profile"))
    markup.row(KeyboardButton("/users"), KeyboardButton("/support"))

def send_users_submenu(bot, chat_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.row(KeyboardButton("/view_profile"), KeyboardButton("/update_profile"))
    markup.row(KeyboardButton("/menu"))
    bot.send_message(chat_id, "👤 User Options:", reply_markup=markup)

def send_fasting_submenu(bot, chat_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.row(KeyboardButton("/start_fast"), KeyboardButton("/stop_fast"))
    KeyboardButton("/edit_fast"),markup.row(KeyboardButton("/menu"))
    bot.send_message(chat_id, "⏱ Fasting Options:", reply_markup=markup)

def get_feedback_keyboard(bot, chat_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    markup.row(KeyboardButton("Suggest a Feature"), KeyboardButton("File a Complaint"))
    markup.row(KeyboardButton("Report a Bug"), KeyboardButton("/menu"))
    return markup

 
