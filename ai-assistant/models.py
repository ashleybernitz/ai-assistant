from db_config import get_connection
import psycopg2

def validate_user(username, password):
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id FROM users
            WHERE username = %s AND password = %s
        """, (username, password))
        result = cur.fetchone()
        if result:
            return (result[0], None)  # ✅ Valid user ID, no error
        else:
            return (None, None)       # ✅ Invalid credentials, no error
    except psycopg2.Error as e:
        print(f"Database error in validate_user: {e}")
        return (None, "⚠️ Unable to connect to the database. Please try again later.")  # ✅ Error message
    finally:
        if cur: cur.close()
        if conn: conn.close()

def save_chat(user_id, model, message, response):
    user_id = int(user_id)
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO chats (user_id, model, message, response)
            VALUES (%s, %s, %s, %s)
        """, (user_id, model, message, response))
        conn.commit()
    except psycopg2.Error as e:
        print(f"Database error in save_chat: {e}")
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_chat_history(user_id):
    user_id = int(user_id)
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT message, response
            FROM chats
            WHERE user_id = %s
            ORDER BY timestamp ASC
        """, (user_id,))
        return cur.fetchall()
    except psycopg2.Error as e:
        print(f"Database error in get_chat_history: {e}")
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()