import random
import datetime

from enum import Enum


class SensorRoleEnum(Enum):
    CRITICAL = 0
    NORMAL = 1
    UNINPORTANT = 2

class Sensor:
    def __init__(self, sensor_id, sensor_type, role):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.role = role

    def get_true_role(self):
        return self.role

    def read_value(self):
        return random.uniform(0, 100)

    def send_data(self):
        return {'sensor_id': self.sensor_id,
                'sensor_type': self.sensor_type,
                'sensor_value': self.read_value(),
                'timestamp': datetime.datetime.now().timestamp()}