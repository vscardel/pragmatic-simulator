import globals
from typing import Callable
import uuid

def add_timer(time: int, func: Callable) -> None:
    globals.timers.append((time, uuid.uuid4(), func))
    
def add_relative_timer(time: int, func: Callable) -> None:
    globals.timers.append((globals.time + time, uuid.uuid4(), func))

def remove_timer(id: uuid.UUID) -> None:
    globals.timers = [timer for timer in globals.timers if timer[1] != id]