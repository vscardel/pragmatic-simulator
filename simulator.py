from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from actuator import Actuator

class Simulator:
    def __init__(self):
        self.reset()
    
    def reset(self) -> None:
        self.time: int = 0
        self.actuator: Union['Actuator', None] = None
        
    def advance_time(self, steps: int = 1) -> None:
        self.time += steps
        
    def set_actuator(self, actuator: 'Actuator') -> None: 
        self.actuator = actuator
        
        
sim = Simulator()