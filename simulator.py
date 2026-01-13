import random
import time
from sensors import Sensor, SensorRoleEnum

from enum import Enum

class GlobalStateEnum(Enum):
    NORMAL = 'NORMAL'
    DEGRADED = 'DEGRADED'
    CRITICAL = 'CRITICAL'
    FAILURE = 'FAILURE'


class SimulationEngine():

    THRESHOLD_LOAD = 50

    def __init__(self):
        self.state = GlobalStateEnum.NORMAL
        self.load = 0
        self.global_state = (self.state, self.load)
        self.initialize_transition_probabilities()
        self.sensors = []

    def initialize_transition_probabilities(self):
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

    def update_transition_probabilities(self, from_state, to_state, new_probability):
        if from_state in self.transition_probabilities:
            self.transition_probabilities[from_state][to_state] = new_probability

    def update_global_state(self):
        rand_val = random.random()

        if self.load > self.THRESHOLD_LOAD:
            penalty_load = 0.2
            bonus_load = 0.0
        else:
            bonus_load = 0.1
            penalty_load = 0.0

        if self.state == GlobalStateEnum.NORMAL:
            if rand_val < self.transition_probabilities[GlobalStateEnum.NORMAL][GlobalStateEnum.DEGRADED] + penalty_load:
                self.state = GlobalStateEnum.DEGRADED

        elif self.state == GlobalStateEnum.DEGRADED:
            if rand_val <  self.transition_probabilities[GlobalStateEnum.DEGRADED][GlobalStateEnum.CRITICAL] + penalty_load:
                self.state = GlobalStateEnum.CRITICAL
            elif rand_val < self.transition_probabilities[GlobalStateEnum.DEGRADED][GlobalStateEnum.NORMAL] + bonus_load:
                self.state = GlobalStateEnum.NORMAL

        elif self.state == GlobalStateEnum.CRITICAL:
            if rand_val < self.transition_probabilities[GlobalStateEnum.CRITICAL][GlobalStateEnum.FAILURE] + penalty_load:
                self.state = GlobalStateEnum.FAILURE
            elif rand_val < self.transition_probabilities[GlobalStateEnum.CRITICAL][GlobalStateEnum.DEGRADED] + bonus_load:
                self.state = GlobalStateEnum.DEGRADED

        elif self.state == GlobalStateEnum.FAILURE:
            if rand_val < self.transition_probabilities[GlobalStateEnum.FAILURE][GlobalStateEnum.CRITICAL] + bonus_load:
                self.state = GlobalStateEnum.CRITICAL

        self.global_state = (self.state, self.load)

    def add_sensor(self, sensor):
        self.sensors.append(sensor)

    def step(self, messages):
        self.load = len(messages)
        # Process messages to potentially affect the global state
        print(f"Global State: {self.global_state}")
