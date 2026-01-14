import random
import datetime
import uuid
from enum import Enum
from typing import Literal

class SensorStateEnum(Enum):
    NORMAL = 'NORMAL'
    DEGRADED = 'DEGRADED'
    CRITICAL = 'CRITICAL'
    FAILURE = 'FAILURE'

class SensorRoleEnum(Enum):
    CRITICAL = 0
    NORMAL = 1
    UNINPORTANT = 2

class SensorTypeEnum(Enum):
    TEMPERATURE = 0
    HUMIDITY = 1
    PRESSURE = 2
    LIGHT = 3
    MOISTURE = 4
    AIR_QUALITY = 5

class Sensor:
    def __init__(self,
                 sensor_id: uuid.UUID,
                 sensor_type: SensorTypeEnum,
                 role: SensorRoleEnum,  # A relevância do sensor
                 operating_range: dict[Literal["normal", "degraded", "critical"], tuple[int, int]],
                 mean_value: float,
                 
                ):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.role = role
        self.operating_range = operating_range
        self.mean_value = mean_value
        self.standard_deviation = (operating_range['normal'][1] - operating_range['normal'][0]) / 2
        self.local_state = SensorStateEnum.NORMAL
        self.__initialize_transition_probabilities()


    def __initialize_transition_probabilities(self):
        self.transition_probabilities = {
            SensorStateEnum.NORMAL: {
                SensorStateEnum.DEGRADED: 0.1
            },
            SensorStateEnum.DEGRADED: {
                SensorStateEnum.CRITICAL: 0.2,
                SensorStateEnum.NORMAL: 0.4
            },
            SensorStateEnum.CRITICAL: {
                SensorStateEnum.FAILURE: 0.3,
                SensorStateEnum.DEGRADED: 0.5
            },
            SensorStateEnum.FAILURE: {
                SensorStateEnum.CRITICAL: 0.6
            }
        }


    def get_true_role(self):
        return self.role

    def observe(self, state):
        pass

    def read_value(self):
        """
        Returns a random value from a normal distribution with mean
        self.mean_value and standard deviation self.standard_deviation.
        """
        return random.normalvariate(self.mean_value, self.standard_deviation)  # Normal distribution

    def send_data(self):
        num_messages = random.randint(1, 10)
        messages = [
            {
                'sensor_id': self.sensor_id,
                'sensor_type': self.sensor_type.value,
                'sensor_value': self.read_value(),
                'timestamp': datetime.datetime.now().timestamp()
            } for _ in range(num_messages)
        ]
        return messages
