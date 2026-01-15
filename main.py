import uuid
import random
from simulator import SimulationEngine
from sensors import Sensor, SensorRoleEnum
from broker import Broker
import time

if __name__ == "__main__":
    simulator = SimulationEngine()
    simulator.initialize_transition_probabilities() # Já faz isso na inicialização do "simulator"
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

        for id, sensor in simulator.sensors.items():

            current_sensors_messages = sensor.send_data()
            # publish each generated message to broker
            for message in current_sensors_messages:
                broker.publish(sensor.sensor_id, sensor.role, message)

        messages = broker.flush()
        # this will need to modulate the transition probabilities for the messages to matter
        # to the environment
        simulator.step(messages)
        time.sleep(0.5)