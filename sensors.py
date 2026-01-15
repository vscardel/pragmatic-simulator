import random
import datetime
import uuid
from enum import Enum
from typing import Literal
from globals import Globals
import time

class SensorStateEnum(Enum):
    NORMAL = 0
    DEGRADED = 1
    CRITICAL = 2
    FAILURE = 3

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
                 sampling_interval: int = 0, # 0 = every time step
                ):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.role = role
        self.operating_range = operating_range
        self.mean_value = mean_value
        self.standard_deviation = (operating_range['normal'][1] - operating_range['normal'][0]) / 2
        self.local_state = SensorStateEnum.NORMAL
        self.sampling_interval = sampling_interval
        self.__initialize_transition_probabilities()


    def __initialize_transition_probabilities(self):
        self.original_transition_probabilities = { # Values when the machine is normal
            SensorStateEnum.NORMAL: {
                SensorStateEnum.DEGRADED: random.uniform(0.008, .012) # 0.8% to 1.2%
            },
            SensorStateEnum.DEGRADED: {
                SensorStateEnum.CRITICAL: random.uniform(0.08, 0.16), # 8% to 16%
                SensorStateEnum.NORMAL: random.uniform(0.001, 0.002) # 0.1% to 0.2%
            },
            SensorStateEnum.CRITICAL: {
                SensorStateEnum.FAILURE: random.uniform(0.15, 0.4), # 15% to 40%
                SensorStateEnum.DEGRADED: random.uniform(0.001, 0.002) # 1% to 2%
            }
        }
        self.transition_probabilities = self.original_transition_probabilities

        
    def adjust_probabilities_by_time_passing(self):
        if (self.local_state == SensorStateEnum.NORMAL):
            self.transition_probabilities[SensorStateEnum.NORMAL][SensorStateEnum.DEGRADED] += 0.0001 # increase by 0.01%
        
        if (self.local_state == SensorStateEnum.DEGRADED):
            self.transition_probabilities[SensorStateEnum.DEGRADED][SensorStateEnum.CRITICAL] += 0.0002 # increase by 0.02%
            self.transition_probabilities[SensorStateEnum.DEGRADED][SensorStateEnum.NORMAL] -= 0.0001 # decrease by 0.01%
        
        if (self.local_state == SensorStateEnum.CRITICAL):
            self.transition_probabilities[SensorStateEnum.CRITICAL][SensorStateEnum.FAILURE] += 0.0004 # increase by 0.04%
            self.transition_probabilities[SensorStateEnum.CRITICAL][SensorStateEnum.DEGRADED] -= 0.0002 # decrease by 0.02%
        
    def update_state_by_probabilities(self):
        rand_value = random.uniform(0, 1)
        
        possibly_states = self.transition_probabilities[self.local_state] if self.local_state != SensorStateEnum.FAILURE else {}
        
        
        for state, probability in possibly_states.items():
            if rand_value < probability:
                self.local_state = state
                print(f"Sensor {self.sensor_id} updated state to {self.local_state}")
                print(self.transition_probabilities)
                time.sleep(1)
                break

    def maintain(self):
        """
        Reset the transition probabilities to their original values.
        """
        self.transition_probabilities = self.original_transition_probabilities

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
        if (Globals.time % self.sampling_interval) != 0:
            return
        
        message = {
            'sensor_id': self.sensor_id,
            'sensor_type': self.sensor_type.value,
            'sensor_value': self.read_value(),
            'timestamp': Globals.time
        }
        return message
