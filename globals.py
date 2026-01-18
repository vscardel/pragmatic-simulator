from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from actuator import Actuator

class Globals:
    time = 0
    actuator: Union['Actuator', None] = None
    
    @classmethod
    def reset(cls):
        cls.time = 0   