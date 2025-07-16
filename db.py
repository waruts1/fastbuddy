# db.py
import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
load_dotenv()
from mysql.connector import FieldType


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

def save_user(telegram_id, name):
    conn = get_connection()
    cursor = conn.cursor()
    # Ensure datetime fields come as datetime
    cursor.execute("SET time_zone = '+03:00'")
    cursor.execute(
        "INSERT INTO users (telegram_id, name) VALUES (%s, %s)",
        (telegram_id, name)
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
          AND stop_time > CONVERT_TZ(NOW(), '+00:00', '+03:00')
          AND status = 'active'
        ORDER BY start_time DESC
        LIMIT 1
    """
    cursor.execute(query, (telegram_id,))
    session = cursor.fetchone()

    cursor.close()
    conn.close()
    return session

def get_user_profile(telegram_id):
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

        return user, profile
    finally:
        cursor.close()
        conn.close()



