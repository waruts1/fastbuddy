from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def get_menu_text():
    menu_title = "📋 <b>FastBuddy Menu</b>\n\nHere’s what I can do:\n"

    menu_items = [
        "/register - Register yourself",
        "/start - Introduction to the bot",
        "/knowledge_base - Learn about fasting stages and benefits",
        "/menu - Show this menu again",
        "/start_fast - Register a fasting session",
        "/stop_fast - Stop your fasting session",
        "/view_profile - View profile",
        "/update_profile - Update your data"
    ]

    return menu_title + '\n'.join(menu_items)


def send_main_menu(bot, chat_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("/start_fast"), KeyboardButton("/stop_fast"))
    markup.row(KeyboardButton("/knowledge_base"), KeyboardButton("/update_profile"))
    markup.row(KeyboardButton("/view_profile"), KeyboardButton("/menu"))
    
    bot.send_message(
        chat_id,
        get_menu_text(),
        reply_markup=markup,
        parse_mode='HTML'
    )
