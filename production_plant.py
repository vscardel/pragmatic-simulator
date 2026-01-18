
from enum import Enum
from sensors import Sensor

class PlantStateEnum(Enum):
    NORMAL = 'NORMAL'
    DEGRADED = 'DEGRADED'
    CRITICAL = 'CRITICAL'
    FAILURE = 'FAILURE'


class ProductionPlant():

    def __init__(self) -> None:
        self.state: PlantStateEnum = PlantStateEnum.NORMAL
        self.sensors: dict[int, Sensor] = {}
        
    def get_sensor(self, sensor_id):
        return self.sensors.get(sensor_id, None)

    def add_sensor(self, sensor: Sensor):
        self.sensors[sensor.sensor_id] = sensor
        
    def set_state(self, state: PlantStateEnum):
        self.state = state

    