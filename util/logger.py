import os
from datetime import datetime

# Set the default log file path
LOG_FILE_PATH = "/home/smiles/public_html/api/fastbuddy/bot-log.txt"

def log(message, level="INFO"):
    """Logs a message with a timestamp and log level."""
    timestamp = (datetime.utcnow()).strftime("%Y-%m-%d %H:%M:%S UTC")
    log_line = f"[{timestamp}] [{level.upper()}] {message}\n"

    try:
        with open(LOG_FILE_PATH, "a") as f:
            f.write(log_line)
    except Exception as e:
        print(f"[LOGGER ERROR] {str(e)}")
