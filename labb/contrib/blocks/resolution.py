"""Resolving a block's models from inside the block package."""

import importlib
import inspect


class BlockContextError(Exception):
    pass


def lm(name: str):
    """
    Resolve a model class by name from within a blocks collection.

    The caller's module path determines the import location:

    - Collection context (5+ parts): {collection}.{vendor}.{category}.{slug}.{module}
      e.g. blocks.lb.crud.todos.views → imports from blocks.lb.models

    - Renderer context (exactly 4 parts): {vendor}.{category}.{slug}.{module}
      e.g. lb.crud.todos.views → imports from lb.models

    - Outside blocks context (fewer than 4 parts): raises BlockContextError
    """
    frame = inspect.currentframe().f_back
    module_name = frame.f_globals["__name__"]
    parts = module_name.split(".")

    if len(parts) >= 5:
        collection, vendor = parts[0], parts[1]
        models_module = importlib.import_module(f"{collection}.{vendor}.models")
    elif len(parts) == 4:
        vendor = parts[0]
        models_module = importlib.import_module(f"{vendor}.models")
    else:
        raise BlockContextError(
            f"lm('{name}') cannot resolve outside a blocks collection.\n"
            f"Replace with: from {'.'.join(parts[:-1])}.models import {name}\n"
            f"(Detected module: {module_name})"
        )

    return getattr(models_module, name)
