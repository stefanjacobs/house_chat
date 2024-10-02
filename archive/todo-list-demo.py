import uuid
from typing import List, Dict, Optional
from datetime import datetime

# In-memory storage for todos
todos: Dict[str, List[Dict[str, Optional[str]]]] = {}

# Helper function to generate a unique ID for each todo
def generate_todo_id() -> str:
    """
    Generates a unique ID for each todo item.
    
    :return: A string representing a unique ID.
    """
    return str(uuid.uuid4())

def get_todos_by_category(category: str = "todo") -> List[Dict[str, Optional[str]]]:
    """
    Retrieves all todos for a given category.
    :param category: The category of todos to retrieve. Defaults to "todo".
    :return: A list of todos in the given category.
    """
    return todos.get(category, [])

def add_todo(todo: str, category: str = "todo", completed_date: Optional[str] = None) -> str:
    """
    Adds a todo item to a specific category.
    :param todo: The todo item description.
    :param category: The category to which the todo item should be added. Defaults to "todo".
    :param completed_date: The optional completed date of the todo item.
    :return: The ID of the added todo item.
    """
    if category not in todos:
        todos[category] = []
    
    todo_id = generate_todo_id()
    todos[category].append({
        'id': todo_id,
        'todo': todo,
        'completed_date': completed_date
    })
    
    return todo_id

def delete_todo_by_id(todo_id: str, category: str = "todo") -> bool:
    """
    Deletes a todo item from a specific category by its ID.
    :param todo_id: The ID of the todo item to delete.
    :param category: The category from which to delete the todo. Defaults to "todo".
    :return: True if the todo was found and deleted, False otherwise.
    """
    if category in todos:
        original_length = len(todos[category])
        todos[category] = [item for item in todos[category] if item['id'] != todo_id]
        
        return len(todos[category]) < original_length
    return False

def get_categories() -> List[str]:
    """
    Retrieves the list of all categories.
    :return: A list of all category names.
    """
    return list(todos.keys())

def delete_category(category: str) -> bool:
    """
    Deletes a category and all its associated todos.
    :param category: The category to delete.
    :return: True if the category existed and was deleted, False otherwise.
    """
    if category in todos:
        del todos[category]
        return True
    return False

from typing import Annotated, Optional

def todo_app_api(
    op: Annotated[str, "The operation to perform. One of 'add', 'delete', 'get', 'categories', 'delete_category'"], 
    todo: Annotated[Optional[str], "The todo item description"] = None, 
    category: Annotated[Optional[str], "The category of the todo item"] = None, 
    completed_date: Annotated[Optional[str], "The completed date of the todo item"] = None, 
    todo_id: Annotated[Optional[str], "The ID of the todo item to delete"] = None
    ) -> Annotated[Optional[str], "A response message based on the operation."]:
    """
    A simple API for managing todo items.
    """
    if op == 'add':
        if todo is None:
            return "Error: 'todo' parameter is required for 'add' operation."
        return add_todo(todo, category, completed_date)
    elif op == 'delete':
        if todo_id is None:
            return "Error: 'todo_id' parameter is required for 'delete' operation."
        return delete_todo_by_id(todo_id, category)
    elif op == 'get':
        return get_todos_by_category(category)
    elif op == 'categories':
        return get_categories()
    elif op == 'delete_category':
        if category is None:
            return "Error: 'category' parameter is required for 'delete_category' operation."
        return delete_category(category)
    else:
        return "Error: Invalid operation. Supported operations: 'add', 'delete', 'get', 'categories', 'delete_category'."



# Example usage
if __name__ == '__main__':
    # Add some todos
    todo_id1 = add_todo("Buy milk", "shopping", "2024-10-03")
    todo_id2 = add_todo("Buy bread", "shopping")
    todo_id3 = add_todo("Finish report", "work")
    todo_id4 = add_todo("Call mom")  # This will be added to the "todo" category
    
    # Retrieve all categories
    categories = get_categories()
    print("Categories:", categories)
    
    # Retrieve todos in 'shopping' category
    shopping_todos = get_todos_by_category("shopping")
    print("Todos in 'shopping' category:", shopping_todos)
    
    # Retrieve todos in default 'todo' category
    default_todos = get_todos_by_category()
    print("Todos in default 'todo' category:", default_todos)
    
    # Delete a todo by ID from the default category
    is_deleted = delete_todo_by_id(todo_id4)
    print(f"Todo with ID {todo_id4} deleted from default category:", is_deleted)
    
    # Retrieve todos after deletion
    default_todos_after_deletion = get_todos_by_category()
    print("Todos in default 'todo' category after deletion:", default_todos_after_deletion)
    
    # Delete 'shopping' category
    category_deleted = delete_category("shopping")
    print(f"'shopping' category deleted:", category_deleted)
    
    # Retrieve all categories after deletion
    categories_after_deletion = get_categories()
    print("Categories after deletion:", categories_after_deletion)