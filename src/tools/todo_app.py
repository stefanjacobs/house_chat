import sqlite3
import uuid
from typing import List, Dict, Optional
from datetime import datetime
import asyncio
import aiosqlite
import logging

# Logging-Konfiguration für Debugging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

class AsyncTodoApp:
    def __init__(self, db_path="database/todo.sqlite"):
        self.db_path = db_path
        self.db = None

    async def connect(self):
        try:
            self.db = await aiosqlite.connect(self.db_path)
            await self._create_tables()
            logger.info("Connected to the database successfully.")
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to the database: {e}")
            raise

    async def _create_tables(self):
        try:
            await self.db.execute('''CREATE TABLE IF NOT EXISTS categories (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    name TEXT UNIQUE NOT NULL)''')
            await self.db.execute('''CREATE TABLE IF NOT EXISTS todos (
                                    id TEXT PRIMARY KEY,
                                    todo TEXT NOT NULL,
                                    completed_date TEXT,
                                    category_id INTEGER,
                                    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE)''')
            await self.db.commit()
            logger.info("Tables created successfully.")
        except sqlite3.Error as e:
            logger.error(f"Failed to create tables: {e}")
            raise

    async def generate_todo_id(self) -> str:
        return str(uuid.uuid4())

    async def get_todos_by_category(self, category: str = "todo") -> str:
        try:
            cursor = await self.db.execute("SELECT todos.id, todos.todo, todos.completed_date "
                                            "FROM todos JOIN categories ON todos.category_id = categories.id "
                                            "WHERE categories.name = ?", (category,))
            rows = await cursor.fetchall()
            return str(rows)
        except sqlite3.Error as e:
            logger.error(f"Failed to fetch todos: {e}")
            return str([])

    async def add_todo(self, todo: str, category: str = "todo", completed_date: Optional[str] = None) -> str:
        try:
            await self.db.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))
            cursor = await self.db.execute("SELECT id FROM categories WHERE name = ?", (category,))
            category_id = (await cursor.fetchone())[0]

            todo_id = await self.generate_todo_id()
            await self.db.execute("INSERT INTO todos (id, todo, completed_date, category_id) VALUES (?, ?, ?, ?)",
                                    (todo_id, todo, completed_date, category_id))
            await self.db.commit()
            logger.info(f"Todo added with ID: {todo_id}")
            return str(todo_id)
        except sqlite3.Error as e:
            logger.error(f"Failed to add todo: {e}")
            return str("")

    async def delete_todo_by_id(self, todo_id: str, category: str = "todo") -> str:
        try:
            cursor = await self.db.execute("SELECT id FROM categories WHERE name = ?", (category,))
            category_result = await cursor.fetchone()
            if category_result:
                category_id = category_result[0]
                result = await self.db.execute("DELETE FROM todos WHERE id = ? AND category_id = ?", (todo_id, category_id))
                rows_deleted = result.rowcount
                await self.db.commit()
                logger.info(f"Deleted {rows_deleted} todos with ID: {todo_id}")
                return str(rows_deleted > 0)
            return str(False)
        except sqlite3.Error as e:
            logger.error(f"Failed to delete todo: {e}")
            return str(False)

    async def get_categories(self) -> str:
        try:
            cursor = await self.db.execute("SELECT name FROM categories")
            rows = await cursor.fetchall()
            categories = [row[0] for row in rows]
            return str(categories)
        except sqlite3.Error as e:
            logger.error(f"Failed to fetch categories: {e}")
            return str([])

    async def delete_category(self, category: str) -> str:
        try:
            result = await self.db.execute("DELETE FROM categories WHERE name = ?", (category,))
            rows_deleted = result.rowcount
            await self.db.commit()
            logger.info(f"Deleted category '{category}' with {rows_deleted} rows affected.")
            return str(rows_deleted > 0)
        except sqlite3.Error as e:
            logger.error(f"Failed to delete category: {e}")
            return str(False)

    async def get_overdue_todos(self) -> str:
        try:
            today = datetime.today().strftime('%Y-%m-%d')
            cursor = await self.db.execute("SELECT todos.id, todos.todo, todos.completed_date, categories.name AS category "
                                            "FROM todos JOIN categories ON todos.category_id = categories.id "
                                            "WHERE todos.completed_date < ?", (today,))
            rows = await cursor.fetchall()
            overdue_todos = [{'id': row[0], 'todo': row[1], 'completed_date': row[2], 'category': row[3]} for row in rows]
            return str(overdue_todos)
        except sqlite3.Error as e:
            logger.error(f"Failed to fetch overdue todos: {e}")
            return str([])

    async def shutdown(self):
        if self.db:
            try:
                await self.db.close()
                logger.info("Database connection closed successfully.")
            except sqlite3.Error as e:
                logger.error(f"Failed to close database connection: {e}")


# import src.tools.todo_app as todo_app
from typing import Annotated, Optional

todo_app = AsyncTodoApp()
# asyncio.run(todo_app.connect())

async def todo_app_api(
    op: Annotated[str, "The operation to perform. One of 'add', 'delete', 'get', 'categories', 'delete_category', 'overdue'."], 
    todo: Annotated[Optional[str], "The todo item description"] = None, 
    category: Annotated[Optional[str], "The category of the todo item"] = None, 
    completed_date: Annotated[Optional[str], "The completed date of the todo item"] = None, 
    todo_id: Annotated[Optional[str], "The ID of the todo item to delete"] = None
    ) -> Annotated[str, "A response message based on the operation."]:
    """
    A simple API for managing todo items. Every item is attached to a category. The operation overdue returns all overdue todo items.
    """
    if op == 'add':
        if todo is None:
            return "Error: 'todo' parameter is required for 'add' operation."
        return await todo_app.add_todo(todo, category, completed_date)
    elif op == 'delete':
        if todo_id is None:
            return "Error: 'todo_id' parameter is required for 'delete' operation."
        return await todo_app.delete_todo_by_id(todo_id, category)
    elif op == 'get':
        return await todo_app.get_todos_by_category(category)
    elif op == 'categories':
        return await todo_app.get_categories()
    elif op == 'delete_category':
        if category is None:
            return "Error: 'category' parameter is required for 'delete_category' operation."
        return await todo_app.delete_category(category)
    elif op == 'overdue':
        return await todo_app.get_overdue_todos()
    else:
        return "Error: Invalid operation. Supported operations: 'add', 'delete', 'get', 'categories', 'delete_category'."

# TODO: Get all todos for listing ordered by category and completed_date