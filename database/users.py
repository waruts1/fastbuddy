import mysql.connector
from db import get_connection , save_user

def fetch_profile(chat_id):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch profile info
    cursor.execute("""
        SELECT gender, weight_kg, height_cm, fast_hours, phone, email
        FROM user_profiles UP
        LEFT JOIN users U ON UP.user_id = U.id
            WHERE U.telegram_id = %s
        """, (chat_id,))
    return cursor.fetchone()

def fetch_user(chat_id):
    cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (chat_id,))
    return cursor.fetchone()