import random
import datetime
import uuid
from enum import Enum
from typing import Literal
from simulator import GlobalStateEnum

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
                 sensor_type: str,
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
        self.local_state = GlobalStateEnum.NORMAL
        self.__initialize_transition_probabilities()


    def __initialize_transition_probabilities(self):
        self.transition_probabilities = {
            GlobalStateEnum.NORMAL: {
                GlobalStateEnum.DEGRADED: 0.1
            },
            GlobalStateEnum.DEGRADED: {
                GlobalStateEnum.CRITICAL: 0.2,
                GlobalStateEnum.NORMAL: 0.4
            },
            GlobalStateEnum.CRITICAL: {
                GlobalStateEnum.FAILURE: 0.3,
                GlobalStateEnum.DEGRADED: 0.5
            },
            GlobalStateEnum.FAILURE: {
                GlobalStateEnum.CRITICAL: 0.6
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
                'sensor_type': self.sensor_type,
                'sensor_value': self.read_value(),
                'timestamp': datetime.datetime.now().timestamp()
            } for _ in range(num_messages)
        ]
        return messages
