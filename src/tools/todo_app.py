import pytz
from datetime import datetime
# from pathlib import Path
from typing import List, Optional, Dict, Annotated
from dataclasses import dataclass
import aiosqlite

@dataclass
class Todo:
    """Data class representing a todo item."""
    id: Optional[int]
    title: str
    category: str
    is_done: bool = False
    due_date: Optional[datetime] = None
    
    def __str__(self) -> str:
        return f"Todo(id={self.id}, title='{self.title}', category='{self.category}', is_done={self.is_done}, due_date={self.due_date})"


class AsyncTodoManager:
    """
    Asynchronous todo manager with SQLite backend storage.
    
    Features:
    - Async todo creation, modification and retrieval
    - Category management
    - Due date tracking
    - Multi-process safe through SQLite
    """
    
    DEFAULT_CATEGORY = "default"
    DB_FILENAME = "todos.db"
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize AsyncTodoManager with optional custom database path.
        
        Args:
            db_path: Optional path to SQLite database. If None, uses default path.
        """
        self.db_path = db_path or self.DB_FILENAME
        self._db: Optional[aiosqlite.Connection] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
        
    async def connect(self) -> None:
        """
        Establish database connection and initialize tables.
        
        Raises:
            DatabaseError: If connection fails
        """
        try:
            self._db = await aiosqlite.connect(self.db_path)
            await self._db.execute("""
                CREATE TABLE IF NOT EXISTS todos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    is_done BOOLEAN NOT NULL DEFAULT 0,
                    due_date TIMESTAMP
                )
            """)
            await self._db.commit()
        except aiosqlite.Error as e:
            raise DatabaseError(f"Failed to initialize database: {str(e)}") from e
            
    async def close(self) -> None:
        """Close database connection if open."""
        if self._db:
            await self._db.close()
            self._db = None
            
    async def _ensure_connected(self) -> None:
        """Ensure database connection is established."""
        if not self._db:
            await self.connect()
    
    async def add_todo(self, title: str, category: Optional[str] = None,
                      due_date: Optional[datetime] = None) -> Todo:
        """
        Add a new todo item.
        
        Args:
            title: Todo title/description
            category: Optional category (uses default if None)
            due_date: Optional due datetime
            
        Returns:
            Todo: Created todo item with assigned ID
            
        Raises:
            DatabaseError: If database operation fails
            ValueError: If title is empty
        """
        if not title.strip():
            raise ValueError("Todo title cannot be empty")
            
        category = category or self.DEFAULT_CATEGORY
        
        await self._ensure_connected()
        try:
            cursor = await self._db.execute(
                """
                INSERT INTO todos (title, category, due_date)
                VALUES (?, ?, ?)
                """,
                (title, category, due_date)
            )
            await self._db.commit()
            
            return Todo(
                id=cursor.lastrowid,
                title=title,
                category=category,
                is_done=False,
                due_date=due_date
            )
        except aiosqlite.Error as e:
            raise DatabaseError(f"Failed to add todo: {str(e)}") from e
    
    async def get_todo(self, todo_id: int) -> Optional[Todo]:
        """
        Retrieve a specific todo by ID.
        
        Args:
            todo_id: ID of todo to retrieve
            
        Returns:
            Todo if found, None otherwise
            
        Raises:
            DatabaseError: If database operation fails
        """
        await self._ensure_connected()
        try:
            async with self._db.execute(
                "SELECT * FROM todos WHERE id = ? AND is_done = 0",
                (todo_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return await self._row_to_todo(row) if row else None
        except aiosqlite.Error as e:
            raise DatabaseError(f"Failed to get todo: {str(e)}") from e


    async def get_todos(self) -> Optional[Todo]:
        """
        Retrieve a specific todo by ID.
        
        Returns:
            Todo if found, None otherwise
            
        Raises:
            DatabaseError: If database operation fails
        """
        await self._ensure_connected()
        try:
            async with self._db.execute(
                "SELECT * FROM todos WHERE is_done = 0",
            ) as cursor:
                rows = await cursor.fetchall()
                return [await self._row_to_todo(row) for row in rows]
        except aiosqlite.Error as e:
            raise DatabaseError(f"Failed to get todo: {str(e)}") from e

    
    async def get_todos_by_category(self, category: str) -> List[Todo]:
        """
        Get all todos in a specific category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List of Todo objects in the specified category
            
        Raises:
            DatabaseError: If database operation fails
        """
        await self._ensure_connected()
        try:
            async with self._db.execute(
                "SELECT * FROM todos WHERE category = ? AND is_done = 0 ORDER BY due_date",
                (category,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [await self._row_to_todo(row) for row in rows]
        except aiosqlite.Error as e:
            raise DatabaseError(f"Failed to get todos by category: {str(e)}") from e


    async def get_overdue_todos(self) -> List[Todo]:
        """
        Get all open todos that are past their due date.
        
        Returns:
            List of overdue Todo objects
            
        Raises:
            DatabaseError: If database operation fails
        """
        tz = pytz.timezone("Europe/Berlin")
        current_time = datetime.now(tz)

        await self._ensure_connected()
        
        try:
            async with self._db.execute(
                """
                SELECT * FROM todos 
                WHERE is_done = 0 
                AND due_date IS NOT NULL 
                AND due_date < ?
                ORDER BY due_date
                """,
                (current_time,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [await self._row_to_todo(row) for row in rows]
        except aiosqlite.Error as e:
            raise DatabaseError(f"Failed to get overdue todos: {str(e)}") from e

    
    async def update_todo(self, todo_id: int, title: Optional[str] = None,
                        category: Optional[str] = None, is_done: Optional[bool] = None,
                        due_date: Optional[datetime] = None) -> Optional[Todo]:
        """
        Update a todo's attributes.
        
        Args:
            todo_id: ID of todo to update
            title: New title (if None, remains unchanged)
            category: New category (if None, remains unchanged)
            is_done: New completion status (if None, remains unchanged)
            due_date: New due date (if None, remains unchanged)
            
        Returns:
            Updated Todo if found, None otherwise
            
        Raises:
            DatabaseError: If database operation fails
            ValueError: If title is empty string
        """
        if title is not None and not title.strip():
            raise ValueError("Todo title cannot be empty")
            
        current_todo = await self.get_todo(todo_id)
        if not current_todo:
            return None
            
        updates = []
        params = []
        
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if category is not None:
            updates.append("category = ?")
            params.append(category)
        if is_done is not None:
            updates.append("is_done = ?")
            params.append(is_done)
        if due_date is not None:
            updates.append("due_date = ?")
            params.append(due_date)
            
        if not updates:
            return current_todo
            
        params.append(todo_id)
        update_query = f"UPDATE todos SET {', '.join(updates)} WHERE id = ?"
        
        await self._ensure_connected()
        try:
            await self._db.execute(update_query, params)
            await self._db.commit()
            return await self.get_todo(todo_id)
        except aiosqlite.Error as e:
            raise DatabaseError(f"Failed to update todo: {str(e)}") from e
    
    @staticmethod
    async def _row_to_todo(row: aiosqlite.Row) -> Todo:
        """Convert a database row to a Todo object."""
        return Todo(
            id=row[0],  # aiosqlite rows are tuples
            title=row[1],
            category=row[2],
            is_done=bool(row[3]),
            due_date=datetime.fromisoformat(row[4]) if row[4] else None
        )


class DatabaseError(Exception):
    """Custom exception for database-related errors."""
    pass



async def get_overdue_todos() -> Annotated[str, "Return a list of overdue todos."]:
    """
    Get a list of overdue todos.
    """
    async with AsyncTodoManager("database/todo.sqlite") as todo_manager:
        overdue = await todo_manager.get_overdue_todos()
    return str(overdue)

async def create_todo(
        title: Annotated[str, "The todo item title"], 
        category: Annotated[Optional[str], "The category of the todo item, 'default' if not specified."], 
        due_date: Annotated[Optional[str], "The due date of the todo item in format 'YYYY-MM-DD HH:MM'"]
    ) -> Annotated[str, "Return the added todo."]:
    """
    Create a new todo. Please note: You can use this to create reminder actions with a given due date.
    """
    due_date_datetime = datetime.strptime(due_date, "%Y-%m-%d %H:%M") if due_date else None
    async with AsyncTodoManager("database/todo.sqlite") as todo_manager:
        todo = await todo_manager.add_todo(title, category, due_date_datetime)
    return str(todo)

async def get_categories(
    ) -> Annotated[str, "Return a list of all categories with open todos."]:
    """
    Get a list of all categories.
    """
    async with AsyncTodoManager("database/todo.sqlite") as todo_manager:
        all_todos = await todo_manager.get_todos()
    categories = set(todo.category for todo in all_todos)
    return str(categories)

async def get_todos_by_category(
        category: Annotated[str, "The given category"],
    ) -> Annotated[str, "Return a list of todos by category."]:
    """
    Get a list of todos by category.
    """
    async with AsyncTodoManager("database/todo.sqlite") as todo_manager:
        todos = await todo_manager.get_todos_by_category(category)
    return str(todos)

async def update_todo(
        todo_id: Annotated[int, "The todo item id"],
        title: Annotated[Optional[str], "The modified title"] = None, 
        category: Annotated[Optional[str], "The modified category"] = None, 
        is_done: Annotated[Optional[str], "'True', if item is done"] = None, 
        due_date: Annotated[Optional[str], "The modified due date of the todo item in format 'YYYY-MM-DD HH:MM'"] = None,
    ) -> Annotated[str, "Return the updated todo."]:
    """
    Update a todo.
    """
    is_done = (is_done == "True" if is_done else None)
    due_date_datetime = datetime.strptime(due_date, "%Y-%m-%d %H:%M") if due_date else None
    async with AsyncTodoManager("database/todo.sqlite") as todo_manager:
        todo = await todo_manager.update_todo(todo_id, title, category, is_done, due_date_datetime)
    return str(todo)


async def get_open_todos(
    ) -> Annotated[str, "Return a list of open todos."]:
    """
    Get a list of all open todos.
    """
    async with AsyncTodoManager("database/todo.sqlite") as todo_manager:
        todos = await todo_manager.get_todos()
    return str(todos)



# if __name__ == "__main__":
#     from datetime import datetime, timedelta
# 
#     async def main():
#         # Using async context manager
#         async with AsyncTodoManager("database/todo.sqlite") as todo_manager:
#             # Add some todos
#             todo1 = await todo_manager.add_todo(
#                 "Buy groceries",
#                 "shopping",
#                 due_date=datetime.now() + timedelta(days=1)
#             )
#         
#             todo2 = await todo_manager.add_todo(
#                 "Write report",
#                 "work",
#                 due_date=datetime.now() - timedelta(hours=1)
#             )
#         
#             # Get overdue todos
#             overdue = await todo_manager.get_overdue_todos()
#         
#             # Update a todo
#             await todo_manager.update_todo(todo1.id, is_done=True)
#         
#             # Get todos by category
#             shopping_todos = await todo_manager.get_todos_by_category("shopping")
# 
#     # Run the async code
#     asyncio.run(main())