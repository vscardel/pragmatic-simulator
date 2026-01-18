from production_plant import PlantStateEnum, ProductionPlant
from globals import Globals
from sensors import SensorRoleEnum, SensorStateEnum
import random

STATE_SEVERITY = {
    PlantStateEnum.NORMAL: 0,
    PlantStateEnum.DEGRADED: 1,
    PlantStateEnum.CRITICAL: 2,
    PlantStateEnum.FAILURE: 3,
}

ROLE_IMPACT = {
    SensorRoleEnum.CRITICAL: 1.0,
    SensorRoleEnum.NORMAL: 0.0,
    SensorRoleEnum.UNINPORTANT: -0.3,
}

ROLE_WEIGHT = {
    SensorRoleEnum.CRITICAL: 0.7,
    SensorRoleEnum.NORMAL: 0.3,
    SensorRoleEnum.UNINPORTANT: 0.0,
}

RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"

class Actuator:
    THRESHOLD_LOAD = 50
    
    def __init__(self, production_plant: ProductionPlant):
        self.load = 0
        self.production_plant = production_plant
        self.global_state = (production_plant.state, self.load)
        self.sp = False  # "should print" TODO: remove it after debugging
    
    def compute_message_pressure(self, messages: list[tuple[int, int, dict]]):
        if not messages:
            return 0.0

        total = 0.0
        
        for role, _, data in messages:
            sensor = self.production_plant.get_sensor(data['sensor_id'])
            total += ROLE_IMPACT[sensor.get_true_role()] * \
                (1.0 / (role + 1))

        return total / len(messages)


    def adjusted_probability(self, from_state, to_state, base_prob, load, msg_pressure):
        severity_diff = STATE_SEVERITY[to_state] - STATE_SEVERITY[from_state]

        load_term = min(0.3, load / self.THRESHOLD_LOAD * 0.3)
        msg_term = msg_pressure * 0.2

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

    """ def update_global_state(self, messages: list[tuple[int, int, dict]]):
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

        self.global_state = (self.state, self.load) """
    
    def update_global_state(self):
        sumTop = 0
        sumWeight = 0
        
        for sensor in list(self.production_plant.sensors.values()):
            sumTop += ROLE_WEIGHT[sensor.get_true_role()] * sensor.local_state.value
            sumWeight += ROLE_WEIGHT[sensor.get_true_role()]
            
        self.production_plant.set_state(round(sumTop / sumWeight))
        self.global_state = (self.production_plant.state, self.load)
        
    def compute_messages_impact(self, messages: list[tuple[int, int, dict]]) -> dict[int, float]:
        """Returns a dict with the keys as the 
        sensors_ids and the values as the sum 
        of impact of the messages
        """ 
        
        messages_impact: dict[int, float] = {}

        for inferred_role, _, data in messages:
            sensor = self.production_plant.get_sensor(data['sensor_id'])
            # Impact is calculated with the true role and the inferred role
            if (data['sensor_id'] not in messages_impact.keys()):
                messages_impact[data['sensor_id']] = 0
            messages_impact[data['sensor_id']] += ROLE_IMPACT[sensor.get_true_role()] + ROLE_IMPACT[SensorRoleEnum(inferred_role)]
            
        return messages_impact 
           
        
    def update_sensors_states(self, all_messages: list[tuple[int, int, dict]]):
        # The load term is a value between 0 and 1 
        # thats indicates how much % of the sensors 
        # with positive sum of impact by messages will be upkept
        load_term = (min(1, self.THRESHOLD_LOAD / self.load)) # TODO: adjust

        sensors_sum_impact = self.compute_messages_impact(all_messages)
        sensors_sum_impact_ordered = sorted(sensors_sum_impact.items(), key=lambda item: item[1], reverse=True)
        
        sensors_to_analyze = sensors_sum_impact_ordered[:round(
            len(sensors_sum_impact_ordered) * load_term)]
        
        if (Globals.time % 3600000 == 0):
            print(f'{CYAN}Time: {Globals.time / 60000} minutes, Load term: {load_term}, number of sensors to analyze: {len(sensors_to_analyze)} of {len(sensors_sum_impact)}{RESET}')
            print(
                f'{CYAN}Sensors to analyze:\n{"\n".join([f"    Sensor {sensor_id} ({self.production_plant.get_sensor(sensor_id).get_true_role()}), impact: {sum_impact}" for sensor_id, sum_impact in sensors_to_analyze])}{RESET}')
        
        for sensor_id, _ in sensors_to_analyze:
            sensor = self.production_plant.get_sensor(sensor_id)
            if (sensor.local_state != SensorStateEnum.NORMAL):
                sensor.upkeep()
                self.sp = True
                
        if (self.sp):
            print(
                f'{CYAN}Time: {Globals.time / 60000} minutes, Load term: {load_term}, number of sensors analyzed: {len(sensors_to_analyze)} of {len(sensors_sum_impact)}{RESET}')
            print(
                f'{CYAN}Sensors analyzed:\n{"\n".join([f"    Sensor {sensor_id} ({self.production_plant.get_sensor(sensor_id).get_true_role()}), impact: {sum_impact}" for sensor_id, sum_impact in sensors_to_analyze])}{RESET}')
            self.sp = False
        
        

    def step(self, messages: list[tuple[int, int, dict]]):
        self.load = len(messages)
        
        self.update_sensors_states(messages)
        self.update_global_state()
        
