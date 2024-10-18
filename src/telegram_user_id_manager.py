import sqlite3
import logging

class UserIDManager:

    def __init__(self, db_name='database/telegram-users.sqlite'):
        self.db_name = db_name
        self._setup_logging()
        self.conn = self._connect()
        self.create_table()

    def _setup_logging(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        if not self.logger.handlers:
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def _connect(self):
        try:
            self.logger.info(f"Connecting to database: {self.db_name}")
            return sqlite3.connect(self.db_name)
        except sqlite3.Error as e:
            self.logger.error(f"Failed to connect to database: {e}")
            raise

    def create_table(self):
        try:
            with self.conn:
                self.conn.execute('''CREATE TABLE IF NOT EXISTS users
                                    (id INTEGER PRIMARY KEY)''')
            self.logger.info("User table ensured exists")
        except sqlite3.Error as e:
            self.logger.error(f"Failed to create table: {e}")
            raise

    def add_user(self, user_id):
        try:
            with self.conn:
                self.conn.execute('INSERT OR IGNORE INTO users (id) VALUES (?)', (user_id,))
            self.logger.info(f"User {user_id} added")
        except sqlite3.Error as e:
            self.logger.error(f"Failed to add user: {e}")

    def get_all_users(self):
        try:
            cursor = self.conn.execute('SELECT id FROM users')
            user_ids = [row[0] for row in cursor.fetchall()]
            self.logger.info(f"Fetched {len(user_ids)} users")
            return user_ids
        except sqlite3.Error as e:
            self.logger.error(f"Failed to fetch users: {e}")
            return []

    def shutdown(self):
        try:
            self.conn.close()
            self.logger.info("Database connection closed")
        except sqlite3.Error as e:
            self.logger.error(f"Failed to close database connection: {e}")

user_id_manager = UserIDManager()