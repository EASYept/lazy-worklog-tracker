import os
import importlib
import sys
from typing import List, Tuple


def load_plugins(plugins_dir: str) -> List[Tuple[str, type]]:
    """
    Dynamically loads all Python modules in the specified directory and collects all classes from them.

    Parameters:
        plugins_dir (str): Absolute or relative path to the plugins directory.

    Returns:
        list: A list of tuples containing the class name and the class itself.
    """
    plugins_dir = os.path.abspath(plugins_dir)
    print(plugins_dir)

    if not os.path.exists(plugins_dir):
        print(f"Error: Plugins directory '{plugins_dir}' does not exist.")
        return []

    # Add the plugins directory to the Python path

    sys.path.append(plugins_dir)

    plugins = []

    try:
        for filename in os.listdir(plugins_dir):
            # Skip directories and non-Python files
            if not filename.endswith(".py") or filename == "__init__.py":
                continue

            # Extract the module name by removing the .py extension
            module_name = filename[:-3]
            print(f"found file {filename}")

            try:
                # Import the module
                module = importlib.import_module(module_name)

                # Collect all classes in the module
                for name, obj in module.__dict__.items():
                    if isinstance(obj, type):
                        plugins.append((name, obj))

            except Exception as e:
                print(f"Error importing module '{module_name}': {e}")

    finally:
        # Remove the plugins directory from sys.path to avoid name collisions
        if plugins_dir in sys.path:
            sys.path.remove(plugins_dir)

    return plugins
