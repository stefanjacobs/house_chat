import inspect
import importlib
import os
import glob
import sys


# Aktuellen Verzeichnis-Pfad zur sys.path hinzufügen
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Alle Python-Dateien im aktuellen Verzeichnis finden
modules = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))

# Alle Module importieren und dekorierte Funktionen in __all__ aufnehmen
__all__ = []
for module in modules:
    if os.path.isfile(module) and not module.endswith('__init__.py'):
        module_name = os.path.basename(module)[:-3]
        try:
            module_obj = importlib.import_module(module_name)
            for name, obj in inspect.getmembers(module_obj):
                if inspect.isfunction(obj) and obj.__qualname__ == "register_tool_decorator.<locals>.wrapper":
                    __all__.append(name)
                    globals()[name] = obj
        except ImportError as e:
            print(f"Fehler beim Importieren von {module_name}: {e}")
