from typing import TYPE_CHECKING, Callable
import uuid
from enum import Enum

class GlobalStateEnum(Enum):
    NORMAL = 0
    DEGRADED = 1
    CRITICAL = 2
    FAILURE = 3

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
should_stop = False
DEFAULT_TIME_STEPS = 24 * 60 * 60  # 24 hours
MAX_ACTUATOR_TEAMS = 2
STEP_JUMP = 1000
SAVE_DATA_INTERVAL = 60 * 60 * 1000  # 1 hour
timers: list[tuple[int, uuid.UUID, Callable]] = []

TIME_TO_RECOVER = {
    GlobalStateEnum.NORMAL: 10 * 60000,  # 5 minutes
    GlobalStateEnum.DEGRADED: 90 * 60000,  # 1 hour and 30 minutes
    GlobalStateEnum.CRITICAL: 4 * 3600000,  # 4 hours
}
