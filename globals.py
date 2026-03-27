from typing import TYPE_CHECKING, Callable
import uuid
from enum import Enum
from collections import defaultdict
import json
import ast


class GlobalStateEnum(Enum):
    NORMAL = 0
    DEGRADED = 1
    CRITICAL = 2
    FAILURE = 3
    
class LogType(Enum):
    UPDATE_BY_PROB = 0
    UPKEEP = 1
    

if TYPE_CHECKING:
    from actuator import Actuator
    from broker import Broker
    from production_plant import ProductionPlant

time: int
plant: 'ProductionPlant'
broker: 'Broker'
actuator: 'Actuator'
last_sensor_id = 0
is_running = False
is_training = False
is_human = False
should_stop = False
DEFAULT_TIME_STEPS = 24 * 60 * 60  # 24 hours
MAX_ACTUATOR_TEAMS = 4
STEP_JUMP = 1000
UPDATE_STATE_INTERVAL_IN_TRAINING = 1000 * 60 * 2 # 2 minutes
SAVE_DATA_INTERVAL = 60 * 1000 # 1 hour
timers: list[tuple[int, uuid.UUID, Callable]] = []
mean_reaction_time_degraded: float | None = None
mean_reaction_time_critical: float | None = None
degraded_maintenances = 0
critical_maintenances = 0
total_maintenance_time = 0
logs: list[tuple[int, LogType, str]] = []
q_table = defaultdict(lambda: [0.0, 0.01])
total_reward = 0
total_positive_reward = 0
total_positive_reward_qty = 0
total_non_positive_reward = 0
total_non_positive_reward_qty = 0

# with open("qtable.json", "r") as f:
#     data = json.load(f)

# for state_str, actions in data.items():
#     state_tuple = ast.literal_eval(state_str) 
#     q_table[state_tuple] = actions

# print("Q-table carregada com sucesso!")

TIME_TO_RECOVER = {
    GlobalStateEnum.NORMAL: 2 * 60000,  # 2 minutes
    GlobalStateEnum.DEGRADED: 90 * 60000,  # 1 hour and 30 minutes
    GlobalStateEnum.CRITICAL: 4 * 3600000,  # 4 hours
}
