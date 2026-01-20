from production_plant import PlantStateEnum, ProductionPlant
from sensors import SensorRoleEnum, SensorStateEnum
import random
from utils.colors import *
import globals
import math

# Not used yet
STATE_SEVERITY = {
    PlantStateEnum.NORMAL: 0,
    PlantStateEnum.DEGRADED: 1,
    PlantStateEnum.CRITICAL: 2,
    PlantStateEnum.FAILURE: 3,
}

# Used to calculate the pressure that the messages exert on the actuator
ROLE_IMPACT = {
    SensorRoleEnum.CRITICAL: 1.0,
    SensorRoleEnum.NORMAL: 0.0,
    SensorRoleEnum.UNINPORTANT: -0.3,
}

# Used to calculate the global state
ROLE_WEIGHT = {
    SensorRoleEnum.CRITICAL: 0.7,
    SensorRoleEnum.NORMAL: 0.3,
    SensorRoleEnum.UNINPORTANT: 0.0,
}


class Actuator:
    THRESHOLD_LOAD = 50 # Used to calculate the overload that the actuator is under
    TRUE_ROLE_IMPACT_WEIGHT = 1
    INFERRED_ROLE_IMPACT_WEIGHT = 1
    
    def __init__(self, production_plant: ProductionPlant):
        self.load = 0
        self.production_plant = production_plant
        self.global_state = (production_plant.state, self.load)
        self.sp = False  # "should print" TODO: remove it after debugging
    
    # Not used yet
    # def compute_message_pressure(self, messages: list[tuple[int, int, dict]]):
    #     if not messages:
    #         return 0.0

    #     total = 0.0
        
    #     for role, _, data in messages:
    #         sensor = self.production_plant.get_sensor(data['sensor_id'])
    #         total += ROLE_IMPACT[sensor.get_true_role()] * \
    #             (1.0 / (role + 1))

    #     return total / len(messages)

    # Not used yet
    # def adjusted_probability(self, from_state, to_state, base_prob, load, msg_pressure):
    #     severity_diff = STATE_SEVERITY[to_state] - STATE_SEVERITY[from_state]

    #     load_term = min(0.3, load / self.THRESHOLD_LOAD * 0.3)
    #     msg_term = msg_pressure * 0.2

    #     if severity_diff > 0:      # getting worse
    #         prob = base_prob + load_term + msg_term
    #     elif severity_diff < 0:    # recovering
    #         prob = base_prob - load_term - msg_term
    #     else:
    #         prob = base_prob

    #     return max(0.0, min(1.0, prob))


    # Not used yet
    # def update_transition_probabilities(self, from_state, to_state, new_probability):
    #     if from_state in self.transition_probabilities:
    #         self.transition_probabilities[from_state][to_state] = new_probability
    
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
            sumTop += ROLE_WEIGHT[sensor.get_true_role()] * sensor.local_state.value
            sumWeight += ROLE_WEIGHT[sensor.get_true_role()]
            
        self.pondered_state = sumTop / sumWeight
        aux = self.pondered_state / 0.75
        self.production_plant.set_state(math.floor(aux))
        self.global_state = (self.production_plant.state, self.load)
        
    def get_pondered_state(self):
        if ('pondered_state' in self.__dict__):
            return self.pondered_state
        else:
            return None    
    
    def compute_messages_impact(self, messages: list[tuple[int, int, dict]]) -> dict[int, float]:
        """
        Returns a dict with the keys as the 
        sensors_ids and the values as the sum 
        of impact of the messages
        """ 
        
        messages_impact: dict[int, float] = {}

        for inferred_role, _, data in messages:
            sensor = self.production_plant.get_sensor(data['sensor_id'])
            # Impact is calculated with the true role and the inferred role
            if (data['sensor_id'] not in messages_impact.keys()):
                messages_impact[data['sensor_id']] = 0
            messages_impact[data['sensor_id']] += ROLE_IMPACT[sensor.get_true_role()] * self.TRUE_ROLE_IMPACT_WEIGHT + ROLE_IMPACT[SensorRoleEnum(inferred_role)] * self.INFERRED_ROLE_IMPACT_WEIGHT
            
        self.last_messages_impact = messages_impact
        return messages_impact 
    
    def get_last_messages_impact(self):
        if ('last_messages_impact' in self.__dict__):
            return self.last_messages_impact
        else:
            return None
           
        
    def update_sensors_states(self, all_messages: list[tuple[int, int, dict]]):
        """
        Updates the state of the sensors based on the messages received. The sensors to be updated are
        chosen based on the load term, which is a value between 0 and 1. The load term is calculated as
        the minimum between 1 and the THRESHOLD_LOAD divided by the load of the actuator. The sensors
        are ordered by their sum of impact in descending order, and the first load_term % sensors are 
        chosen to be updated. If the sensor is not in the NORMAL state, its upkeep method is called.
        """
        
        # The load term is a value between 0 and 1
        # thats indicates how much % of the sensors
        # with positive sum of impact by messages will be upkept
        load_term = (min(1, self.THRESHOLD_LOAD / self.load)) # TODO: adjust

        sensors_sum_impact = self.compute_messages_impact(all_messages)
        sensors_sum_impact_ordered = sorted(sensors_sum_impact.items(), key=lambda item: item[1], reverse=True)
        
        # Get the first load_term % of the sensors
        sensors_to_analyze = sensors_sum_impact_ordered[:round(
            len(sensors_sum_impact_ordered) * load_term)]
        
        self.load_term = load_term
        self.sensors_sum_impact_ordered = sensors_sum_impact_ordered
        self.sensors_to_analyze = sensors_to_analyze
        
        if (globals.time % 3600000 == 0):
            print(f'{CYAN}Time: {globals.time / 60000} minutes, Load term: {load_term}, number of sensors to analyze: {len(sensors_to_analyze)} of {len(sensors_sum_impact)}{RESET}')
            print(
                f'{CYAN}Sensors to analyze:\n{"\n".join([f"    Sensor {sensor_id} ({self.production_plant.get_sensor(sensor_id).get_true_role()}), impact: {sum_impact}" for sensor_id, sum_impact in sensors_to_analyze])}{RESET}')
        
        for sensor_id, _ in sensors_to_analyze:
            sensor = self.production_plant.get_sensor(sensor_id)
            if (sensor.local_state != SensorStateEnum.NORMAL):
                sensor.upkeep()
                self.sp = True
                
        if (self.sp):
            print(
                f'{CYAN}Time: {globals.time / 60000} minutes, Load term: {load_term}, number of sensors analyzed: {len(sensors_to_analyze)} of {len(sensors_sum_impact)}{RESET}')
            print(
                f'{CYAN}Sensors analyzed:\n{"\n".join([f"    Sensor {sensor_id} ({self.production_plant.get_sensor(sensor_id).get_true_role()}), impact: {sum_impact}" for sensor_id, sum_impact in sensors_to_analyze])}{RESET}')
            self.sp = False
        
    def get_last_load_term(self):
        if ('load_term' in self.__dict__):
            return self.load_term
        else:
            return None
        
    def get_last_sensors_to_analyze(self):
        if ('sensors_to_analyze' in self.__dict__):
            return self.sensors_to_analyze
        else:
            return None
        
    def get_last_sensors_sum_impact_ordered(self):
        if ('sensors_sum_impact_ordered' in self.__dict__):
            return self.sensors_sum_impact_ordered
        else:
            return None

    def step(self, messages: list[tuple[int, int, dict]]):
        self.load = len(messages)
        
        self.update_sensors_states(messages)
        self.update_global_state()
        
