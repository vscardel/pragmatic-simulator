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
            current_sensors_messages = sensor.send_data()
            for message in current_sensors_messages:
                broker.publish(sensor.sensor_id, sensor.role, sensor.send_data())

        messages = broker.flush()
        # this will need to modulate the transition probabilities for the messages to matter
        # to the environment
        simulator.step(messages)
        simulator.update_global_state()
        time.sleep(0.5)