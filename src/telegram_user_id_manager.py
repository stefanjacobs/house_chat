
import aiosqlite
import logging
import asyncio

# Logging-Konfiguration für Debugging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

class UserIDManager:

    def __init__(self, db_name='database/telegram-users.sqlite'):
        self.db_name = db_name
        self.conn = None

    async def connect(self):
        try:
            logger.info(f"Connecting to database: {self.db_name}")
            self.conn = await aiosqlite.connect(self.db_name)
            await self._create_table()
        except aiosqlite.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    async def _create_table(self):
        try:
            async with self.conn.execute('''CREATE TABLE IF NOT EXISTS users
                                            (id INTEGER PRIMARY KEY)''') as cursor:
                await self.conn.commit()
            logger.info("User table ensured exists")
        except aiosqlite.Error as e:
            logger.error(f"Failed to create table: {e}")
            raise

    async def add_user(self, user_id):
        try:
            async with self.conn.execute('INSERT OR IGNORE INTO users (id) VALUES (?)', (user_id,)) as cursor:
                await self.conn.commit()
            logger.info(f"User {user_id} added")
        except aiosqlite.Error as e:
            logger.error(f"Failed to add user: {e}")

    async def get_all_users(self):
        try:
            async with self.conn.execute('SELECT id FROM users') as cursor:
                rows = await cursor.fetchall()
                user_ids = [row[0] for row in rows]
            logger.info(f"Fetched {len(user_ids)} users")
            return user_ids
        except aiosqlite.Error as e:
            logger.error(f"Failed to fetch users: {e}")
            return []

    async def shutdown(self):
        try:
            await self.conn.close()
            logger.info("Database connection closed")
        except aiosqlite.Error as e:
            logger.error(f"Failed to close database connection: {e}")

user_id_manager = UserIDManager()