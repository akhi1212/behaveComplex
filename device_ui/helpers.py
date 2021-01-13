import os
import importlib
from typing import Set

import env


def get_classes_from_dir(class_type: type, path: str) -> Set[type]:
    root_dir = env.PROJ_ROOT
    classes: Set[type] = set()

    for dir_path, dir_names, file_names in os.walk(path):
        for fn in file_names:
            if not fn.endswith(".py"):
                continue
            fp = os.path.join(dir_path, fn)
            import_str = ".".join(fp.replace(root_dir, "")[:-3].lstrip(os.sep).split(os.sep))
            module = importlib.import_module(import_str)
            for obj in module.__dict__.values():
                if isinstance(obj, type) and issubclass(obj, class_type):
                    classes.add(obj)
        break
    return classes
