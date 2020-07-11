import functools
import os
from typing import Callable


def use_tempdir(func: Callable) -> Callable:
    current_dir = os.getcwd()

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        os.chdir(os.environ["TEMP_DIR"])
        return func(*args, **kwargs)

    os.chdir(current_dir)

    return wrapper
