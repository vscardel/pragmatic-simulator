import random
import time
from sensors import Sensor, SensorRoleEnum

class GlobalStateEnum:
    NORMAL = 'NORMAL'
    DEGRADED = 'DEGRADED'
    CRITICAL = 'CRITICAL'
    FAILURE = 'FAILURE'


class SimulationEngine():
    def __init__(self):
        self.state = GlobalStateEnum.NORMAL
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

        if self.state == GlobalStateEnum.NORMAL:
            if rand_val < self.transition_probabilities[GlobalStateEnum.NORMAL][GlobalStateEnum.DEGRADED]:
                self.state = GlobalStateEnum.DEGRADED

        elif self.state == GlobalStateEnum.DEGRADED:
            if rand_val <  self.transition_probabilities[GlobalStateEnum.DEGRADED][GlobalStateEnum.CRITICAL]:
                self.state = GlobalStateEnum.CRITICAL
            elif rand_val < self.transition_probabilities[GlobalStateEnum.DEGRADED][GlobalStateEnum.NORMAL]:
                self.state = GlobalStateEnum.NORMAL

        elif self.state == GlobalStateEnum.CRITICAL:
            if rand_val < self.transition_probabilities[GlobalStateEnum.CRITICAL][GlobalStateEnum.FAILURE]:
                self.state = GlobalStateEnum.FAILURE
            elif rand_val < self.transition_probabilities[GlobalStateEnum.CRITICAL][GlobalStateEnum.DEGRADED]:
                self.state = GlobalStateEnum.DEGRADED

        elif self.state == GlobalStateEnum.FAILURE:
            if rand_val < self.transition_probabilities[GlobalStateEnum.FAILURE][GlobalStateEnum.CRITICAL]:
                self.state = GlobalStateEnum.CRITICAL

    def add_sensor(self, sensor):
        self.sensors.append(sensor)

    def step(self, messages):
        # for now, just print and ignore the messages
        for priority, count, data in messages:
            print(f"Processing message with priority {priority}: {data}")
