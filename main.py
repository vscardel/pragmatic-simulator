import uuid
from simulator import SimulationEngine
from sensors import Sensor, SensorRoleEnum
import time

if __name__ == "__main__":
    simulator = SimulationEngine()
    simulator.initialize_transition_probabilities()
    for i in range(5):
        sensor = Sensor(
            sensor_id=uuid.uuid4(),
            sensor_type='Temperature',
            role=SensorRoleEnum.NORMAL
        )
        simulator.add_sensor(sensor)
    while True:
        simulator.update_global_state()
        print(f"Current Global State: {simulator.state}")
        time.sleep(0.5)