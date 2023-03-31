import sqlite3
from datetime import datetime

def check_daily_limit(user_ip):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = f"SELECT COUNT(*) FROM chat_details WHERE openai_response >= date('now', 'start of day') AND user_ip='{user_ip}';"
    cursor.execute(query)
    count = cursor.fetchone()[0]
    conn.close()
    return {"count": count}

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def insert_to_db(chat_uuid, user_input, chatbot_reply, previous_chat, openai_response, user_ip, user_location ):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO chat_details (chat_uuid, user_input, chatbot_reply, previous_chat, openai_response, user_ip, user_location) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (chat_uuid, user_input, chatbot_reply, previous_chat, openai_response, user_ip, user_location) )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("error while inserting to the db in insert db function ERROR => ", e)
        return False

