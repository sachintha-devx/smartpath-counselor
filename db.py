import sqlite3

def connect_db():
    return sqlite3.connect("database.db")


def create_table():
    conn = connect_db()
    cursor = conn.cursor()

    # 🔥 Chat sessions WITH TITLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_sessions (
        chat_id TEXT PRIMARY KEY,
        title TEXT
    )
    """)

    # 💬 Messages table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id TEXT,
        role TEXT,
        content TEXT
    )
    """)

    # 🧠 Knowledge table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS knowledge (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        answer TEXT
    )
    """)

    conn.commit()
    conn.close()


# 🔵 KNOWLEDGE FUNCTIONS
def save_knowledge(question, answer):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO knowledge (question, answer) VALUES (?, ?)",
        (question, answer)
    )

    conn.commit()
    conn.close()


def get_answer(question):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT answer FROM knowledge WHERE question LIKE ?",
        ('%' + question + '%',)
    )

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None


# 🟣 CHAT SESSION FUNCTIONS
def save_chat_session(chat_id, title="New Chat"):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO chat_sessions (chat_id, title)
    VALUES (?, ?)
    """, (chat_id, title))

    conn.commit()
    conn.close()


def update_chat_title(chat_id, title):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE chat_sessions SET title=? WHERE chat_id=?
    """, (title, chat_id))

    conn.commit()
    conn.close()


def get_chat_titles():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT chat_id, title FROM chat_sessions")
    data = cursor.fetchall()

    conn.close()
    return dict(data)


def get_all_chat_ids():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT chat_id FROM chat_sessions")
    ids = [row[0] for row in cursor.fetchall()]

    conn.close()
    return ids


# 💬 CHAT MESSAGE FUNCTIONS
def save_chat(chat_id, role, content):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO chats (chat_id, role, content) VALUES (?, ?, ?)",
        (chat_id, role, content)
    )

    conn.commit()
    conn.close()


def load_chat(chat_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT role, content FROM chats WHERE chat_id=? ORDER BY id ASC",
        (chat_id,)
    )

    data = cursor.fetchall()
    conn.close()
    return data