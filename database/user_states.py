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
    print(result)
    cursor.close()
    conn.close()
    return result
    
def update_user_field(chat_id, field, value):
    allowed_fields = {
        "gender": "gender",
        "fast_hours": "fast_hours",
        "weight": "weight_kgs",
        "height": "height_cms",
        "email": "email",
        "phone": "phone"
    }

    if field not in allowed_fields:
        raise ValueError(f"Field '{field}' is not allowed to be updated.")

    column = allowed_fields[field]

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Fetch user ID from users table
        cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (chat_id,))
        user = cursor.fetchone()

        if not user:
            raise ValueError(f"User with telegram_id {chat_id} not found.")

        user_id = user[0]

        # Check if user_profiles record exists
        cursor.execute("SELECT id FROM user_profiles WHERE user_id = %s", (user_id,))
        profile = cursor.fetchone()

        if profile and column not in ('phone', 'email'):
        # Update existing profile except for phone/email
            sql = f"UPDATE user_profiles SET {column} = %s, updated_at = NOW() WHERE user_id = %s"
            cursor.execute(sql, (value, user_id))
        elif not profile and column not in ('phone', 'email'):
        # Insert new profile record for fields except phone/email
            sql = f"INSERT INTO user_profiles (user_id, {column}, created_at, updated_at) VALUES (%s, %s, NOW(), NOW())"
            cursor.execute(sql, (user_id, value))
        # Always update users table if field is email or phone
        if column in ('phone', 'email'):
            sql_user = f"UPDATE users SET {column} = %s, updated_at = NOW() WHERE telegram_id = %s"
            cursor.execute(sql_user, (value, chat_id))

        conn.commit()

    finally:
        cursor.close()
        conn.close()
    

def clear_user_state(chat_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_update_states WHERE telegram_id = %s", (chat_id,))
    conn.commit()
    cursor.close()
    conn.close()