# db.py
import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
load_dotenv()
from mysql.connector import FieldType
from util.logger import log

# Database connection config from .env
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASSWORD")

# Connect to MySQL
def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )

def user_exists(telegram_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None
    



    conn.commit()
    conn.close()
def set_user_state(chat_id, step, field=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO user_update_states (telegram_id, step, field)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE step = %s, field = %s
    """, (chat_id, step, field, step, field))

    conn.commit()
    cursor.close()
    conn.close()

def get_user_state(chat_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT step, field FROM user_update_states WHERE telegram_id = %s", (chat_id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    return result
    

def clear_user_state(chat_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_update_states WHERE telegram_id = %s", (chat_id,))
    conn.commit()
    cursor.close()
    conn.close()


def save_user(telegram_id, name,username):
    conn = get_connection()
    cursor = conn.cursor()
    # Ensure datetime fields come as datetime
    cursor.execute("SET time_zone = '+03:00'")
    cursor.execute(
        "INSERT INTO users (telegram_id, name, username) VALUES (%s, %s,%s)",
        (telegram_id, name,username)
    )
    conn.commit()
    cursor.close()
    conn.close()

def update_start_time(session_id: int, new_start_time: datetime):
    conn = get_connection()
    cursor = conn.cursor()
    # Assume new_start_time is a string like "2025-07-18 07:30"
    new_start_time_with_micro = new_start_time + ":00.000000"
    cursor.execute(
                "UPDATE fast_records SET start_time = %s WHERE telegram_id = %s AND status='active'",
                (new_start_time_with_micro, session_id)
            )
    conn.commit()
    cursor.close()
    conn.close()
            
def save_fasting_session(telegram_id, start_time, fast_hours, stop_time):
    conn = get_connection()
    cursor = conn.cursor()
    # Ensure datetime fields come as datetime
    cursor.execute("SET time_zone = '+03:00'")
    # Apply timezone offset (+3 hours)
    now_gmt3 = datetime.utcnow() + timedelta(hours=3)
    
    query = """
        INSERT INTO fast_records (telegram_id, start_time, fast_hours, stop_time, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (telegram_id, start_time, fast_hours, stop_time, now_gmt3, now_gmt3))

    conn.commit()
    cursor.close()
    conn.close()
    
def has_active_session(telegram_id):
    conn = get_connection()
    cursor = conn.cursor()
    # Ensure datetime fields come as datetime
    cursor.execute("SET time_zone = '+03:00'")
    now_gmt3 = datetime.utcnow() + timedelta(hours=3)

    query = """
        SELECT COUNT(*) FROM fast_records
        WHERE telegram_id = %s AND stop_time > %s
    """
    cursor.execute(query, (telegram_id, now_gmt3))
    (count,) = cursor.fetchone()

    cursor.close()
    conn.close()
    return count > 0
    
def complete_session(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    # Ensure datetime fields come as datetime
    cursor.execute("SET time_zone = '+03:00'")
    query = "UPDATE fast_records SET status = 'completed', updated_at = NOW() WHERE id = %s"
    cursor.execute(query, (session_id,))
    conn.commit()

    cursor.close()
    conn.close()

def add_star(telegram_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Set timezone to GMT+3
    cursor.execute("SET time_zone = '+03:00'")

    query = """
        UPDATE users 
        SET stars = COALESCE(stars, 0) + 1,
            updated_at = NOW()
        WHERE telegram_id = %s
    """
    cursor.execute(query, (telegram_id,))
    conn.commit()

    cursor.close()
    conn.close()


def get_active_session(telegram_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    # Ensure datetime fields come as datetime
    cursor.execute("SET time_zone = '+03:00'")
    query = """
        SELECT * FROM fast_records
        WHERE telegram_id = %s
          AND stop_time > NOW()
          AND status = 'active'
        ORDER BY start_time DESC
        LIMIT 1
    """
    cursor.execute(query, (telegram_id,))
    session = cursor.fetchone()

    cursor.close()
    conn.close()
    return session
    
def get_user_profile_data(telegram_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get user basic info
        cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (telegram_id,))
        user = cursor.fetchone()

        if not user:
            return None, None

        user_id = user['id']

        # Get user profile info
        cursor.execute("SELECT * FROM user_profiles WHERE user_id = %s", (user_id,))
        profile = cursor.fetchone()

        return user,profile
    finally:
        cursor.close()
        conn.close()
        
def get_user_profile(telegram_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT up.*
            FROM users u
            LEFT JOIN user_profiles up ON u.id = up.user_id
            WHERE u.telegram_id = %s
        """, (telegram_id,))

        profile = cursor.fetchone()

        # If profile is completely missing
        if not profile or all(value is None for value in profile.values()):
            return None

        return profile

    finally:
        cursor.close()
        conn.close()


def get_full_user_profile(telegram_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (telegram_id,))
    user = cursor.fetchone()

    profile = None
    if user:
        cursor.execute("SELECT * FROM user_profiles WHERE user_id = %s", (user['id'],))
        profile = cursor.fetchone()

    cursor.close()
    conn.close()
    return user, profile


def get_completed_fast_hours_this_week(telegram_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SET time_zone = '+03:00'")

    query = """
        SELECT SUM(fast_hours) as total
        FROM fast_records
        WHERE telegram_id = %s AND status != 'cancelled'
        AND start_time >= DATE_SUB(CURDATE(), INTERVAL WEEKDAY(CURDATE()) DAY)
    """
    cursor.execute(query, (telegram_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row['total'] or 0

def update_session_stop_time(session_id, new_stop_time):
    from db_conn import conn
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE fasting_records SET start_time = ? WHERE id = ?",
        (new_stop_time, session_id)
    )
    conn.commit()
def get_recent_sessions(telegram_id, limit=1):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SET time_zone = '+03:00'")
    query = """
        SELECT * FROM fast_records
        WHERE telegram_id = %s
        ORDER BY start_time DESC
        LIMIT %s
    """
    cursor.execute(query, (telegram_id, limit))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

# db.py

def save_pending_confirmation(telegram_id, session_id):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO pending_confirmations (telegram_id, session_id)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE session_id = VALUES(session_id), created_at = NOW()
    """
    cursor.execute(query, (telegram_id, session_id))
    conn.commit()
    cursor.close()
    conn.close()

def get_pending_confirmation(telegram_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT session_id FROM pending_confirmations WHERE telegram_id = %s"
    cursor.execute(query, (telegram_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result['session_id'] if result else None

def delete_pending_confirmation(telegram_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pending_confirmations WHERE telegram_id = %s", (telegram_id,))
    conn.commit()
    cursor.close()
    conn.close()

def cancel_session(session_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE fast_records SET status = 'cancelled', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()

def get_fast_start(user_id):
    """
    Retrieve fasting start time and target hours for a user from the database.
    
    :param user_id: Telegram user ID
    :return: Tuple (start_time: datetime, fast_hours: float) or (None, None) if no record exists
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT start_time, fast_hours FROM fast_records WHERE telegram_id = %s AND status = 'active' ORDER BY id DESC LIMIT 1"
        params = (str(user_id),)
        log(f"Executing query: {query} with params: {params}", level="DEBUG", feature="get_fast_start")
        cursor.execute(query, params)
        result = cursor.fetchone()
        log(f"[get_fast_start..........] Result: {result}", level="INFO", feature="get_fast_start")
        if result:
            try:
                start_time = result[0] if isinstance(result[0], datetime) else datetime.fromisoformat(result[0])
                fast_hours = float(result[1]) if result[1] is not None else 16.0
                log(f"Parsed start_time={result[0]}, fast_hours={fast_hours} for user {user_id}", level="INFO", feature="get_fast_start")
                return (start_time, fast_hours)
            except ValueError as ve:
                log(f"Invalid start_time format for user {user_id}: {ve}", level="ERROR", feature="get_fast_start")
                return (None, None)
        return (None, None)
    except mysql.connector.Error as me:
        log(f"Database error in get_fast_start for user {user_id}: {me}", level="ERROR", feature="get_fast_start")
        return (None, None)
    except Exception as e:
        log(f"Unexpected error in get_fast_start for user {user_id}: {e}", level="ERROR", feature="get_fast_start")
        return (None, None)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()