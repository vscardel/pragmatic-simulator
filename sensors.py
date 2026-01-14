import random
import datetime

from enum import Enum


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
    def __init__(self, sensor_id, sensor_type, role):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.role = role

    def get_true_role(self):
        return self.role

    def observe(self, state):
        pass

    def read_value(self):
        return random.uniform(0, 100)

    def send_data(self):
        num_messages = random.randint(1, 10)
        messages = [{'sensor_id': self.sensor_id,
                'sensor_type': self.sensor_type,
                'sensor_value': self.read_value(),
                'timestamp': datetime.datetime.now().timestamp()} for _ in range(num_messages)]
        return messages