from datetime import datetime, timedelta
from db import save_fasting_session

def start_fast(telegram_id, fast_hours):
    start_time = datetime.utcnow()
    stop_time = start_time + timedelta(hours=fast_hours)

    # Save to DB (you implement save_fasting_session in db.py)
    save_fasting_session(telegram_id, start_time, fast_hours, stop_time)

    return start_time, stop_time , fast_hours