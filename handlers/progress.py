from PIL import Image, ImageDraw, ImageFont
from util.logger import log
from db import get_fast_start
from datetime import datetime, timedelta
import os
def create_progress_bar(fasted_hours, target_hours=16):
    """
    Create a circular progress bar image for fasting progress.
    
    :param fasted_hours: Hours the user has fasted
    :param target_hours: Target fasting hours (default: 16 for 16:8 fasting)
    :return: Path to the generated image
    """
    try:
        progress = min(fasted_hours / target_hours, 1.0)
        angle = int(360 * progress)

        size = (200, 200)
        image = Image.new('RGBA', size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)

        draw.ellipse((10, 10, 190, 190), outline='grey', width=10)
        if angle > 0:
            draw.arc((10, 10, 190, 190), start=-90, end=-90 + angle, fill='blue', width=10)

        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        text = f"{int(progress * 100)}%"
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        draw.text((100 - text_width // 2, 100 - text_height // 2), text, fill='black', font=font)

        image_path = f"progress_{fasted_hours}_{datetime.now().timestamp()}.png"
        image.save(image_path)
        return image_path
    except Exception as e:
        log(f"Error creating progress bar: {e}", level="ERROR", feature="create_progress_bar")
        raise



def handle_progress(bot, chat_id):
    """
    Handle the /progress command by calculating fasting progress and generating a progress bar.
    
    :param bot: Telebot instance
    :param chat_id: Telegram chat ID
    :param chat_id: Telegram user ID
    :param chat_id: Telegram chat_id or chat_id if chat_id is None
    :return: Dict with status and message for logging
    """
    try:
        start_time, target_hours = get_fast_start(chat_id)
        log(f"[handle_progress start_time, target_hours] {start_time}{target_hours}", level="INFO", feature="progress bar")
        if start_time:
            hours = (datetime.utcnow() + timedelta(hours=3) - start_time).total_seconds() / 3600
            
            image_path = create_progress_bar(hours, target_hours or 16)
            with open(image_path, 'rb') as photo:
                bot.send_photo(chat_id, photo, caption=f"Fasting Progress: {hours:.2f}/{target_hours or 16} hours")
            os.remove(image_path)
            return {'status': 'success', 'message': f"Progress bar sent for {hours:.2f} hours to user {chat_id}"}
        else:
            bot.send_message(chat_id, "No active fast found. Start one with /start_fast.", parse_mode='HTML')
            return {'status': 'warning', 'message': f"No active fast for progress query by user {chat_id}"}
    except Exception as e:
        log(f"Error in handle_progress for user {chat_id}: {e}", level="ERROR", feature="handle_progress")
        bot.send_message(chat_id, "Error generating progress bar. Please try again.", parse_mode='HTML')
        return {'status': 'error', 'message': f"Error in handle_progress for user {chat_id}: {e}"}