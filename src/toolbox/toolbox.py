import logging
from src.toolbox.tool_def_generator import ToolDefGenerator

TOOLBOX = []

def register_tool_decorator(tool):

    def wrapper(func):
        global TOOLBOX

        # Check if the function is already registered in the global toolbox
        already_registered = next((True for (name, _, _) in TOOLBOX if name == func.__name__), False)
        
        if not already_registered:
            logging.info("Putting into toolbox: " + func.__name__)
            generator = ToolDefGenerator()
            TOOLBOX.append((func.__name__, generator.generate(func)[0], func))
        return func
    
    return wrapper(tool)
