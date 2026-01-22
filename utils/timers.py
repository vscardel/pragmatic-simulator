import globals
from typing import Callable


def add_timer(time: int, func: Callable) -> None:
    globals.timers.append((time, func))
    
def add_relative_timer(time: int, func: Callable) -> None:
    globals.timers.append((globals.time + time, func))

def remove_timer(time: int, func: Callable) -> None:
    globals.timers.remove((time, func))