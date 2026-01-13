import random
import time
from sensors import Sensor, SensorRoleEnum

from enum import Enum

class GlobalStateEnum(Enum):
    NORMAL = 'NORMAL'
    DEGRADED = 'DEGRADED'
    CRITICAL = 'CRITICAL'
    FAILURE = 'FAILURE'

STATE_SEVERITY = {
    GlobalStateEnum.NORMAL: 0,
    GlobalStateEnum.DEGRADED: 1,
    GlobalStateEnum.CRITICAL: 2,
    GlobalStateEnum.FAILURE: 3,
}

ROLE_IMPACT = {
    SensorRoleEnum.CRITICAL: 1.0,
    SensorRoleEnum.NORMAL: 0.0,
    SensorRoleEnum.UNINPORTANT: -0.3,
}

class SimulationEngine():

    THRESHOLD_LOAD = 50

    def __init__(self):
        self.state = GlobalStateEnum.NORMAL
        self.load = 0
        self.global_state = (self.state, self.load)
        self.initialize_transition_probabilities()
        self.sensors = {}

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

    def compute_message_pressure(self, messages):
        if not messages:
            return 0.0

        total = 0.0

        for priority, _, data in messages:
            sensor = self.sensors.get(data['sensor_id'])
            total += ROLE_IMPACT[sensor.get_true_role()] * (1.0 / (priority + 1))

        return total / len(messages)

    def adjusted_probability(self, from_state, to_state, base_prob, load, msg_pressure):
        severity_diff = STATE_SEVERITY[to_state] - STATE_SEVERITY[from_state]

        load_term = min(0.3, load / self.THRESHOLD_LOAD * 0.3)
        msg_term  = msg_pressure * 0.2

        if severity_diff > 0:      # getting worse
            prob = base_prob + load_term + msg_term
        elif severity_diff < 0:    # recovering
            prob = base_prob - load_term - msg_term
        else:
            prob = base_prob

        return max(0.0, min(1.0, prob))


    def update_transition_probabilities(self, from_state, to_state, new_probability):
        if from_state in self.transition_probabilities:
            self.transition_probabilities[from_state][to_state] = new_probability

    def update_global_state(self, messages):
        rand_val = random.random()
        msg_pressure = self.compute_message_pressure(messages)

        transitions = self.transition_probabilities.get(self.state, {})
        cumulative = 0.0

        for to_state, base_prob in transitions.items():
            p = self.adjusted_probability(
                self.state,
                to_state,
                base_prob,
                self.load,
                msg_pressure
            )
            cumulative += p
            if rand_val < cumulative:
                self.state = to_state
                break

        self.global_state = (self.state, self.load)

    def add_sensor(self, sensor):
        self.sensors[sensor.sensor_id] = sensor

    def step(self, messages):
        self.load = len(messages)
        self.update_global_state(messages)
        print(f"Global State: {self.global_state}")
