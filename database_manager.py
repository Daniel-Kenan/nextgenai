import sqlite3

class DatabaseManager:
    def __init__(self, db_file='conversations.db'):
        self.db_file = db_file
        self._create_tables()

    def _create_tables(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
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

    def get_conversation_history(self, websocket_id):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('SELECT message FROM messages WHERE websocket_id = ? ORDER BY timestamp', (websocket_id,))
        messages = [row[0] for row in c.fetchall()]
        conn.close()
        return messages

    def store_message(self, websocket_id, message):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('INSERT INTO messages (websocket_id, message) VALUES (?, ?)', (websocket_id, message))
        conn.commit()
        conn.close()
