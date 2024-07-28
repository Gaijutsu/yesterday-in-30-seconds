import sqlite3

from _types import Entry, Feed

class DatabaseManager:
    """
    DatabaseManager class is used to save and retrieve entries from the database.
    """

    def __init__(self, db_path: str = "database/sql.db") -> None:
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.create_table()
    
    def create_table(self) -> None:
        """
        Create the table if it does not exist.
        """
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            text TEXT,
            image TEXT,
            url TEXT,
            summary TEXT,
            video TEXT
        );
        """)
        self.conn.commit()

    def save_entry(self, entry: Entry) -> None:
        """
        Save an entry to the database.

        Args:
            entry (Entry): The entry to save.
        """
        self.cursor.execute("""
        INSERT INTO entries (title, text, image, url, summary, video)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (entry.title, entry.text, entry.image, entry.url, entry.summary, entry.video))
        self.conn.commit()

    def save_feed(self, feed: Feed) -> None:
        """
        Save a feed to the database.

        Args:
            feed (Feed): The feed to save.
        """
        for entry in feed.entries:
            self.save_entry(entry)
    
    def get_entries(self) -> list[Entry]:
        """
        Get all entries from the database.

        Returns:
            list[Entry]: A list of entries.
        """
        self.cursor.execute("SELECT * FROM entries")
        entries = self.cursor.fetchall()
        return [Entry(*entry) for entry in entries]
    
    def get_entry(self, id: int) -> Entry:
        """
        Get an entry from the database by ID.

        Args:
            id (int): The ID of the entry.

        Returns:
            Entry: The entry.
        """
        self.cursor.execute("SELECT * FROM entries WHERE id=?", (id,))
        entry = self.cursor.fetchone()
        return Entry(*entry)
    
    def delete_entry(self, id: int) -> None:
        """
        Delete an entry from the database by ID.

        Args:
            id (int): The ID of the entry.
        """
        self.cursor.execute("DELETE FROM entries WHERE id=?", (id,))
        self.conn.commit()