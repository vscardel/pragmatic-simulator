from sensors import SensorRoleEnum, SensorMessage
from typing import List, Tuple
import random
from production_plant import GlobalStateEnum
from enum import Enum
import globals
from collections import defaultdict
import time

class BrokerInstruction(Enum):
    DO_NOTHING = 0
    UPKEEP = 1


class BrokerMessage:
    def __init__(self, sensor_id: int, sensor_message: SensorMessage, instruction: BrokerInstruction) -> None:
        self.sensor_id = sensor_id
        self.sensor_message = sensor_message
        self.instruction = instruction
        


class Broker:
    def __init__(self, alpha=0.01, gamma=0.9, epsilon=1) -> None:
        self.buffer: List[BrokerMessage] = []
        self.do_nothing_count = 0
        self.upkeep_count = 0
        self.necessary_upkeep_count = 0
        self.mean_values: dict[int, float] = {}
        
        self.alpha = alpha     # Taxa de aprendizado
        self.gamma = gamma     # Fator de desconto
        self.epsilon = epsilon  # Taxa de exploração
                
    def _discretize_state(self, sensor_id: int, sensor_role: int, value: float, available_teams: int) -> Tuple[int, int, int, int]:
        # Usa o valor real (arredondado) como "bin" em vez de agrupá-lo por dezenas
        value_bin = int(round(value))
        return (sensor_id, sensor_role, value_bin, available_teams)
    
    def _calculate_reward(self, old_plant_state: float, plant_state: float, instruction: int, sensor_role: SensorRoleEnum) -> float:
        state_reward = (old_plant_state  - plant_state)
        teams_reward = globals.actuator.available_teams / globals.MAX_ACTUATOR_TEAMS
        result = 0
        
        if (instruction == 1 and state_reward <= 0):
            result = -8
            tr = 1-teams_reward
            if (sensor_role == SensorRoleEnum.UNINPORTANT):
                result *= 10
            elif (sensor_role == SensorRoleEnum.NORMAL):
                result *= 5
            elif (sensor_role == SensorRoleEnum.CRITICAL):
                result *= 2
        elif (instruction == 1 and state_reward > 0):
            result = state_reward *150
            tr = max(teams_reward,1/globals.MAX_ACTUATOR_TEAMS)
            if (sensor_role == SensorRoleEnum.UNINPORTANT):
                result *= 2
            elif (sensor_role == SensorRoleEnum.NORMAL):
                result *= 5
            elif (sensor_role == SensorRoleEnum.CRITICAL):
                result *= 10
        elif (instruction == 0 and state_reward <= 0):
            result = 1
            tr = 1- teams_reward /2
            if (sensor_role == SensorRoleEnum.UNINPORTANT):
                result *= 10
            elif (sensor_role == SensorRoleEnum.NORMAL):
                result *= 5
            elif (sensor_role == SensorRoleEnum.CRITICAL):
                result *= 2
        
        
        result *= tr

        return result

    def publish(self, sensor_id: int, data: SensorMessage) -> bool:
        if (not sensor_id in self.mean_values.keys()): 
            self.mean_values[sensor_id] = [data.sensor_value]
        else:
            self.mean_values[sensor_id].append(data.sensor_value)
            self.mean_values[sensor_id] = self.mean_values[sensor_id][-3:]
        
        state = self._discretize_state(
            sensor_id,
            globals.plant.get_sensor(sensor_id).get_true_role().value, 
            sum(self.mean_values[sensor_id])/len(self.mean_values[sensor_id]), 
            globals.actuator.available_teams
        )
        if (globals.is_human):
            sensor = globals.plant.get_sensor(sensor_id)
            if sensor.should_maintain:
                action_idx = 1
                sensor.should_maintain = False
            else:
                action_idx = 0
        else:    
            if random.uniform(0, 1) < self.epsilon:
                action_idx = random.choice([0, 1]) if globals.actuator.available_teams > 0 else 0
            else:
                action_idx = globals.q_table[state].index(max(globals.q_table[state])) if globals.actuator.available_teams > 0 else 0

        instruction = BrokerInstruction.UPKEEP if action_idx == 1 else BrokerInstruction.DO_NOTHING

        if instruction == BrokerInstruction.DO_NOTHING:
            self.do_nothing_count += 1
        elif instruction == BrokerInstruction.UPKEEP:
            self.upkeep_count += 1
            sensor = globals.plant.get_sensor(sensor_id)
            if (sensor.local_state != GlobalStateEnum.NORMAL and sensor.local_state != GlobalStateEnum.FAILURE):
                self.necessary_upkeep_count += 1

        broker_message = BrokerMessage(
            sensor_id=sensor_id,
            sensor_message=data,
            instruction=instruction
        )
        old_plant_state = globals.plant.measured_state
        globals.actuator.message(broker_message)

        reward = self._calculate_reward(old_plant_state, globals.plant.measured_state, action_idx, globals.plant.get_sensor(sensor_id).get_true_role())
        target = reward + self.gamma * max(globals.q_table[state])

        # Atualização Bellman simplificada (assumindo que o próximo estado imediato do broker
        # é independente desta ação específica, o que é comum em roteamento de pacotes IoT)
        # Q(s,a) = Q(s,a) + alpha * (Reward - Q(s,a))
        old_value = globals.q_table[state][action_idx]
        globals.q_table[state][action_idx] = old_value + \
            self.alpha * (target - old_value)

        # if (not globals.is_training):
        #     self.epsilon = 0.0000001  # max(0.000001, self.epsilon * 0.999999)
        if (reward > 0):
            self.epsilon = max(0.000001, self.epsilon * 0.9999999)
        

        return True


    def flush(self) -> List[BrokerMessage]:
        msgs = self.buffer
        self.buffer = []
        return msgs
