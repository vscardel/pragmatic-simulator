import globals
from typing import Callable


def add_timer(time: int, func: Callable) -> None:
    globals.timers.append((time, func))
    
def remove_timer(time: int, func: Callable) -> None:
    globals.timers.remove((time, func))