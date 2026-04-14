import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional

from .config import StarliteConfig

class ConversationDB:
    """
    The Akashic Records of the AGI, a database chronicling every dialogue
    and revelation. It provides the ground truth for memory and learning.
    """
    def __init__(self, db_path: str = StarliteConfig.DB_NAME):
        """Connects to the eternal database, forging tables if they are but myth."""
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_tables()

    def _create_tables(self):
        """Carves the schema for storing conversations into the database's stone."""
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    user_input TEXT NOT NULL,
                    response TEXT NOT NULL,
                    context TEXT,
                    feedback INTEGER
                )
            ''')

    def log_interaction(self, user_input: str, response: str, context: str) -> int:
        """
        Scribes a new entry into the chronicles: a user's query and the AGI's wisdom.
        Returns the unique star-sign (ID) of this sacred exchange.
        """
        timestamp = datetime.now().isoformat()
        with self.conn:
            cursor = self.conn.execute(
                'INSERT INTO conversations (timestamp, user_input, response, context) VALUES (?, ?, ?, ?)',
                (timestamp, user_input, response, context)
            )
            return cursor.lastrowid

    def get_all_interactions(self) -> List[Tuple[int, str]]:
        """
        Reads the entire chronicle, returning the ID and text of every recorded
        user input for the purpose of building semantic memory.
        """
        with self.conn:
            cursor = self.conn.execute('SELECT id, user_input FROM conversations')
            return cursor.fetchall()

    def close(self):
        """Closes the gateway to the records, ensuring their peace."""
        self.conn.close()
