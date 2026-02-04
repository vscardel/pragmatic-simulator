
from enum import Enum
from typing import TYPE_CHECKING
from globals import GlobalStateEnum

if TYPE_CHECKING:
    from sensors import Sensor


class ProductionPlant():

    def __init__(self) -> None:
        self.state: GlobalStateEnum = GlobalStateEnum.NORMAL
        self.measured_state: float = 0 # float between 0 and 3
        self.sensors: dict[int, 'Sensor'] = {}
        
    def get_sensor(self, sensor_id):
        return self.sensors.get(sensor_id, None)
    
    def get_sensors(self):
        return dict([(sensor_id, sensor.__str__()) for sensor_id, sensor in self.sensors.items()])

    def add_sensor(self, sensor: 'Sensor'):
        self.sensors[sensor.sensor_id] = sensor
        
    def set_state(self, state: GlobalStateEnum):
        self.state = state
        
    def set_measured_state(self, state: float):
        self.measured_state = state

    