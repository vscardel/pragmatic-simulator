from typing import TYPE_CHECKING, Callable
import uuid

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
DEFAULT_TIME_STEPS = 24 * 60 * 60 * 1000  # 24 hours
MAX_ACTUATOR_TEAMS = 2
timers: list[tuple[int, uuid.UUID, Callable]] = []
