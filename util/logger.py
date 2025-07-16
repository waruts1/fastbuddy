import os
from datetime import datetime

# Set the default log file path
LOG_FILE_PATH = "/home/smiles/public_html/api/fastbuddy/bot-log.txt"

def log(message, level="INFO", feature=None):
    """
    Logs a message with a timestamp, log level, and optional feature name.
    
    :param message: The message to log
    :param level: Log level, e.g., INFO, ERROR
    :param feature: (Optional) Feature/module name for more clarity
    """
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    feature_str = f"[{feature}]" if feature else ""
    log_line = f"[{timestamp}] [{level.upper()}]{feature_str} {message}\n"

    try:
        with open(LOG_FILE_PATH, "a") as f:
            f.write(log_line)
    except Exception as e:
        print(f"[LOGGER ERROR] {str(e)}")

