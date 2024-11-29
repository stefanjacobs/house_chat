
from src.toolbox.tool_def_generator import ToolDefGenerator

TOOLBOX = []

def register_tool_decorator(tool):

    def wrapper(func):
        generator = ToolDefGenerator()
        global TOOLBOX

        already_registered = False
        for (name, _, _) in TOOLBOX:
            if name == func.__name__:
                already_registered = True
                break
        if not already_registered:
            print("Putting into toolbox: ", func.__name__)
            TOOLBOX.append((func.__name__, generator.generate(func)[0], func))
        return func
    
    return wrapper(tool)
