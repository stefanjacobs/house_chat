import sqlite3, logging, uuid
from typing import List, Dict, Optional
from datetime import datetime


class TodoApp:
    def __init__(self, db_path='database/todos.sqlite'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS categories (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT UNIQUE NOT NULL)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS todos (
                                id TEXT PRIMARY KEY,
                                todo TEXT NOT NULL,
                                completed_date TEXT,
                                category_id INTEGER,
                                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE)''')

        self.conn.commit()

    def generate_todo_id(self) -> str:
        return str(uuid.uuid4())

    def get_todos_by_category(self, category: str = "todo") -> str:
        self.cursor.execute("SELECT todos.id, todos.todo, todos.completed_date "
                            "FROM todos JOIN categories ON todos.category_id = categories.id "
                            "WHERE categories.name = ?", (category,))
        rows = self.cursor.fetchall()
        return str(rows)

    def add_todo(self, todo: str, category: str = "todo", completed_date: Optional[str] = None) -> str:
        self.cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))
        self.cursor.execute("SELECT id FROM categories WHERE name = ?", (category,))
        category_id = self.cursor.fetchone()[0]

        todo_id = self.generate_todo_id()
        self.cursor.execute("INSERT INTO todos (id, todo, completed_date, category_id) VALUES (?, ?, ?, ?)",
                            (todo_id, todo, completed_date, category_id))
        self.conn.commit()
        return str(todo_id)

    def delete_todo_by_id(self, todo_id: str, category: str = "todo") -> str:
        self.cursor.execute("SELECT id FROM categories WHERE name = ?", (category,))
        category_result = self.cursor.fetchone()
        if category_result:
            category_id = category_result[0]
            self.cursor.execute("DELETE FROM todos WHERE id = ? AND category_id = ?", (todo_id, category_id))
            rows_deleted = self.cursor.rowcount
            self.conn.commit()
            return str(rows_deleted > 0)
        return str(False)

    def get_categories(self) -> str:
        self.cursor.execute("SELECT name FROM categories")
        rows = self.cursor.fetchall()
        categories = [row[0] for row in rows]
        return str(categories)

    def delete_category(self, category: str) -> str:
        self.cursor.execute("DELETE FROM categories WHERE name = ?", (category,))
        rows_deleted = self.cursor.rowcount
        self.conn.commit()
        return str(rows_deleted > 0)

    def get_overdue_todos(self) -> str:
        today = datetime.today().strftime('%Y-%m-%d')
        self.cursor.execute("SELECT todos.id, todos.todo, todos.completed_date, categories.name AS category "
                            "FROM todos JOIN categories ON todos.category_id = categories.id "
                            "WHERE todos.completed_date < ?", (today,))
        rows = self.cursor.fetchall()
        overdue_todos = [{'id': row[0], 'todo': row[1], 'completed_date': row[2], 'category': row[3]} for row in rows]
        return str(overdue_todos)

    def shutdown(self):
        try:
            self.conn.close()
            self.logger.info("Database connection closed")
        except sqlite3.Error as e:
            self.logger.error(f"Failed to close database connection: {e}")


# import src.tools.todo_app as todo_app
from typing import Annotated, Optional

todo_app = TodoApp()

def todo_app_api(
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
        return todo_app.add_todo(todo, category, completed_date)
    elif op == 'delete':
        if todo_id is None:
            return "Error: 'todo_id' parameter is required for 'delete' operation."
        return todo_app.delete_todo_by_id(todo_id, category)
    elif op == 'get':
        return todo_app.get_todos_by_category(category)
    elif op == 'categories':
        return todo_app.get_categories()
    elif op == 'delete_category':
        if category is None:
            return "Error: 'category' parameter is required for 'delete_category' operation."
        return todo_app.delete_category(category)
    elif op == 'overdue':
        return todo_app.get_overdue_todos()
    else:
        return "Error: Invalid operation. Supported operations: 'add', 'delete', 'get', 'categories', 'delete_category'."
