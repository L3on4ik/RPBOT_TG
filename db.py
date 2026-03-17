import sqlite3

def init_db():
    conn = sqlite3.connect("profiles.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS profiles (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT,
        fursona TEXT,
        photo TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_profile(user_id, name, description, fursona, photo):
    conn = sqlite3.connect("profiles.db")
    cur = conn.cursor()

    cur.execute("""
    INSERT OR REPLACE INTO profiles (user_id, name, description, fursona, photo)
    VALUES (?, ?, ?, ?, ?)
    """, (user_id, name, description, fursona, photo))

    conn.commit()
    conn.close()


def get_profile(user_id):
    conn = sqlite3.connect("profiles.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
    data = cur.fetchone()

    conn.close()
    return data