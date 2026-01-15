from production_plant import PlantStateEnum, ProductionPlant
from globals import     Globals
from sensors import SensorRoleEnum
import random
import uuid
from collections import defaultdict

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

class Actuator:
    THRESHOLD_LOAD = 50
    
    def __init__(self, production_plant: ProductionPlant):
        self.load = 0
        self.production_plant = production_plant
        self.global_state = (production_plant.state, self.load)
    
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
        
    def divide_messages_by_sensors(self, all_messages: list[tuple[int, int, dict]]):
        divided_messages_by_sensor: list[tuple[uuid.UUID,
                                               list[tuple[int, int, dict]]]] = []

        grouped_dict = defaultdict(list)

        for msg in all_messages:
            # Desempacota a mensagem para pegar o data (índice 2)
            _, _, data = msg
            sensor_id = data.get('sensor_id')

            if sensor_id:
                grouped_dict[sensor_id].append(msg)

        divided_messages_by_sensor = list(grouped_dict.items())
        
        return divided_messages_by_sensor
        
    def update_sensors_transition_probabilities(self, all_messages: list[tuple[int, int, dict]]):
        rand_val = random.random()
        divided_messages_by_sensor = self.divide_messages_by_sensors(all_messages)
        
        print(Globals.time, end="\n-------")
        print(len(all_messages), end="\n-------")
        print(len(divided_messages_by_sensor))
        
        load_term = min(1, self.load / self.THRESHOLD_LOAD * 0.5) # TODO: adjust
                
        t = False
                
        for sensor_id, messages in divided_messages_by_sensor:
            msg_pressure = self.compute_message_pressure(messages)
            msg_term = msg_pressure * 0.3 # TODO: adjust
            
            prob_to_take_an_action = 1.0 - load_term + msg_term # TODO: adjust
            
            if (not t):
                print(load_term, msg_pressure, msg_term, prob_to_take_an_action)
                t = True
            
            if rand_val < prob_to_take_an_action:
                sensor = self.production_plant.get_sensor(sensor_id)
                sensor.upkeep()

    def step(self, messages: list[tuple[int, int, dict]]):
        self.load = len(messages)
        
        self.update_sensors_transition_probabilities(messages)
        self.update_global_state()
        
