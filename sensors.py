import random
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
        if (not self.__operating_range_is_ok()):
            raise Exception("Operating range is not valid")
        self.mean_value = mean_value
        self.standard_deviation = (operating_range['normal'][1] - operating_range['normal'][0]) / 2
        self.local_state = SensorStateEnum.NORMAL
        self.sampling_interval = sampling_interval
        self.__initialize_transition_probabilities()

    def __operating_range_is_ok(self):
        """
        Checks if the operating range is valid.

        A valid operating range must have 'normal', 'degraded', and 'critical' ranges.
        Every range must be a range of two values (min, max).
        The 'normal' range must be completely inside the 'degraded' range, and the 'degraded'
        range must be completely inside the 'critical' range.

        Returns:
            bool: True if the operating range is valid, False otherwise.
        """
        if (self.operating_range['normal'][0] >= self.operating_range['normal'][1]):
            return False
        if (self.operating_range['degraded'][0] >= self.operating_range['degraded'][1]):
            return False
        if (self.operating_range['critical'][0] >= self.operating_range['critical'][1]):
            return False
        if (self.operating_range['degraded'][0] >= self.operating_range['normal'][0]):
            return False
        if (self.operating_range['degraded'][1] <= self.operating_range['normal'][1]):
            return False
        if (self.operating_range['critical'][0] >= self.operating_range['degraded'][0]):
            return False
        if (self.operating_range['critical'][1] <= self.operating_range['degraded'][1]):
            return False
        
        return True

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
        
    def auto_set_mean_value(self):
        normal_range = self.operating_range['normal'][1] - self.operating_range['normal'][0]
        critical_range = self.operating_range['critical'][1] - self.operating_range['critical'][0]
        
        if self.local_state == SensorStateEnum.NORMAL:
            self.mean_value = random.uniform(self.operating_range['normal'][0], self.operating_range['normal'][1])
        elif self.local_state == SensorStateEnum.DEGRADED:
            
            self.mean_value = random.uniform(self.operating_range['degraded'][0], self.operating_range['degraded'][1] - normal_range)
            if self.mean_value >= self.operating_range['normal'][0] and self.mean_value <= self.operating_range['normal'][1]:
                self.mean_value += normal_range
        elif self.local_state == SensorStateEnum.CRITICAL:
            degraded_to_left = self.mean_value < self.operating_range['normal'][0]
            if (degraded_to_left):
                # Change mean value to the left of the degraded range
                self.mean_value = random.uniform(self.operating_range['critical'][0], self.operating_range['degraded'][0])
            else:
                # Change mean value to the right of the degraded range
                self.mean_value = random.uniform(self.operating_range['degraded'][1], self.operating_range['critical'][1])
            
        elif self.local_state == SensorStateEnum.FAILURE:
            critical_to_left = self.mean_value < self.operating_range['normal'][0]
            if (critical_to_left):
                self.mean_value = random.normalvariate(self.operating_range['critical'][0], critical_range)
                if self.mean_value >= self.operating_range['critical'][0]:
                    self.mean_value = self.operating_range['critical'][0] + (self.operating_range['critical'][0] - self.mean_value)
            else:
                self.mean_value = random.normalvariate(self.operating_range['critical'][1], critical_range)
                if self.mean_value <= self.operating_range['critical'][1]:
                    self.mean_value = self.operating_range['critical'][1] - (self.mean_value - self.operating_range['critical'][1])
                
            
        
    def update_state_by_probabilities(self):
        rand_value = random.uniform(0, 1)
        
        possibly_states = self.transition_probabilities[self.local_state] if self.local_state != SensorStateEnum.FAILURE else {}
        
        
        for state, probability in possibly_states.items():
            if rand_value < probability:
                self.local_state = state
                self.auto_set_mean_value()
                print(f"Sensor {self.sensor_id} updated state to {self.local_state}")
                print(f'NORMAL->DEGRADED: {self.transition_probabilities[SensorStateEnum.NORMAL][SensorStateEnum.DEGRADED]}')
                print(f'DEGRADED->CRITICAL: {self.transition_probabilities[SensorStateEnum.DEGRADED][SensorStateEnum.CRITICAL]}')
                print(f'DEGRADED->NORMAL: {self.transition_probabilities[SensorStateEnum.DEGRADED][SensorStateEnum.NORMAL]}')
                print(f'CRITICAL->FAILURE: {self.transition_probabilities[SensorStateEnum.CRITICAL][SensorStateEnum.FAILURE]}')
                print(f'CRITICAL->DEGRADED: {self.transition_probabilities[SensorStateEnum.CRITICAL][SensorStateEnum.DEGRADED]}')
                time.sleep(1)
                break

    def upkeep(self):
        """
        Reset the transition probabilities to their original values.
        """
        # TODO: increase the probabilities to go back to a better state
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
