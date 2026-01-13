import uuid
import random
from simulator import SimulationEngine
from sensors import Sensor, SensorRoleEnum
from broker import Broker
import time

if __name__ == "__main__":
    simulator = SimulationEngine()
    simulator.initialize_transition_probabilities()
    broker = Broker()

    for i in range(5):
        sensor = Sensor(
            sensor_id=uuid.uuid4(),
            sensor_type='Temperature',
            role=random.choice(list(SensorRoleEnum))
        )
        simulator.add_sensor(sensor)
        broker.subscribe(sensor)

    while True:

        for sensor in simulator.sensors:
            broker.publish(sensor.sensor_id, sensor.role, sensor.send_data())

        broker.process_messages()

        simulator.update_global_state()
        print(f"Current Global State: {simulator.state}")
        time.sleep(0.5)