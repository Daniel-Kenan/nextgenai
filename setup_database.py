# setup_database.py

import sqlite3

def create_database():
    conn = sqlite3.connect('conversations.db')
    c = conn.cursor()

    # Create table to store messages
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            websocket_id TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
