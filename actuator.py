from production_plant import GlobalStateEnum, ProductionPlant
from sensors import SensorRoleEnum, Sensor
from broker import BrokerMessage
import random
from utils.colors import *
import globals
import math
from utils.timers import add_relative_timer

STATE_SEVERITY = {
    GlobalStateEnum.NORMAL: 0,
    GlobalStateEnum.DEGRADED: 1,
    GlobalStateEnum.CRITICAL: 2,
    GlobalStateEnum.FAILURE: 3,
}


# Used to calculate the global state
ROLE_WEIGHT = {
    SensorRoleEnum.CRITICAL: 0.7,
    SensorRoleEnum.NORMAL: 0.3,
    SensorRoleEnum.UNINPORTANT: 0.0,
}

TIME_TO_RECOVER = {
    GlobalStateEnum.NORMAL: 10 * 60000,  # 5 minutes
    GlobalStateEnum.DEGRADED: 90 * 60000,  # 1 hour and 30 minutes
    GlobalStateEnum.CRITICAL: 4 * 3600000,  # 4 hours
}


class Actuator:
    THRESHOLD_LOAD = 50  # Used to calculate the overload that the actuator is under

    def __init__(self, production_plant: ProductionPlant):
        self.available_teams = globals.MAX_ACTUATOR_TEAMS
        self.production_plant = production_plant
        self.unnecessary_maintenances = 0
        self.total_maintenances = 0
        self.total_maintenance_time = 0

    def update_global_state(self):
        """
        Updates the global state of the production plant by calculating a weighted sum of the sensor states.

        The weighted sum is calculated by multiplying the value of each sensor state by the corresponding role weight, 
        and then summing all the values together. The resulting sum is then divided by the sum of all the role weights, 
        and the production plant state is set to the resulting value.

        Finally, the global state of the actuator is updated with the new production plant state and the current load.
        """
        sumTop = 0
        sumWeight = 0

        for sensor in list(self.production_plant.sensors.values()):
            sumTop += ROLE_WEIGHT[sensor.get_true_role()] * \
                sensor.local_state.value
            sumWeight += ROLE_WEIGHT[sensor.get_true_role()]

        measured_state = sumTop / sumWeight
        normalized_state = measured_state / 0.75
        self.production_plant.set_measured_state(measured_state)
        self.production_plant.set_state(math.floor(normalized_state))


    def compute_messages_impact(self, messages: list[BrokerMessage]) -> dict[int, float]:
        """
        Returns a dict with the keys as the 
        sensors_ids and the values as the sum 
        of impact of the messages
        """

        messages_impact: dict[int, float] = {}

        for message in messages:
            sensor_id = message.sensor_id
            inferred_role = message.inferred_role
            inferred_state = message.inferred_state
            # Impact is calculated with the inferred role and the inferred state
            if (sensor_id not in messages_impact.keys()):
                messages_impact[sensor_id] = 0
            messages_impact[sensor_id] += ROLE_WEIGHT[SensorRoleEnum(inferred_role)] * STATE_SEVERITY[GlobalStateEnum(inferred_state)]

        self.last_messages_impact = messages_impact
        return messages_impact

    def get_last_messages_impact(self):
        if ('last_messages_impact' in self.__dict__):
            return self.last_messages_impact
        else:
            return None

    def update_sensors_states(self, all_messages: list[BrokerMessage]):
        """
        Updates the state of the sensors based on the messages received. The sensors to be updated are
        chosen based on the impact of the its messages. The sensors are ordered by their sum of impact 
        in descending order, and the first self.available_teams sensors are
        chosen to be updated. If the sensor is not in the NORMAL state, its upkeep method is called.
        """

        self.sensors_sum_impact = self.compute_messages_impact(all_messages)
        positive_sensors_sum_impact = dict(filter(lambda item: item[1] > 0, self.sensors_sum_impact.items()))
        self.sensors_sum_impact_ordered = sorted(
            positive_sensors_sum_impact.items(), key=lambda item: item[1], reverse=True)

        # Get the first self.available_teams sensors
        self.sensors_to_analyze = self.sensors_sum_impact_ordered[:self.available_teams]


        self.upkeep_sensors([sensor_id for sensor_id, _ in self.sensors_to_analyze])
                
    def upkeep_sensors(self, sensors: list[int]):
        for sensor_id in sensors:
            sensor = self.production_plant.get_sensor(sensor_id)
            if (sensor.local_state == GlobalStateEnum.FAILURE):
                continue
            
            
            sensor.under_maintenance = True
            add_relative_timer(TIME_TO_RECOVER[sensor.local_state], self.make_team_available)
            add_relative_timer(TIME_TO_RECOVER[sensor.local_state], sensor.finish_maintenance)
            
            self.available_teams -= 1
            self.total_maintenances += 1
            self.total_maintenance_time += TIME_TO_RECOVER[sensor.local_state]
            if (sensor.local_state != GlobalStateEnum.NORMAL): sensor.upkeep()
            else: self.unnecessary_maintenances += 1
            
    def make_team_available(self):
        self.available_teams += 1
        
    def get_available_teams(self):
        return self.available_teams


    def get_last_load_term(self):
        """@deprecated"""
        if ('load_term' in self.__dict__):
            return self.load_term
        else:
            return None

    def get_last_sensors_to_analyze(self):
        if ('sensors_to_analyze' in self.__dict__):
            return self.sensors_to_analyze
        else:
            return None
        
    def get_last_sensors_sum_impact(self):
        if ('sensors_sum_impact' in self.__dict__):
            return self.sensors_sum_impact
        else:
            return None

    def get_last_sensors_sum_impact_ordered(self):
        if ('sensors_sum_impact_ordered' in self.__dict__):
            return self.sensors_sum_impact_ordered
        else:
            return None

    def step(self, messages: list[BrokerMessage]):
        self.update_sensors_states(messages)
        self.update_global_state()
