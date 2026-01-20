from typing import TYPE_CHECKING

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