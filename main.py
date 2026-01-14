import uuid
import random
from simulator import SimulationEngine
from sensors import Sensor, SensorRoleEnum, SensorTypeEnum
from broker import Broker
import time

NUMBER_OF_SENSORS = 5



def initialize_sensors(simulator: SimulationEngine, broker: Broker):
    for _ in range(NUMBER_OF_SENSORS):
        sensor = Sensor(
            sensor_id=uuid.uuid4(),
            sensor_type=random.choice(list(SensorTypeEnum)),
            role=random.choice(list(SensorRoleEnum)),
            operating_range={ # Valores mockados e estaticos, mudar depois
                "normal": (50, 60),
                "degraded": (40, 70),
                "critical": (30, 95)
            },
            mean_value=55,
        )   
        simulator.add_sensor(sensor)
        broker.subscribe(sensor)
                

if __name__ == "__main__":
    simulator = SimulationEngine()
    broker = Broker()
    initialize_sensors(simulator, broker)

    while True: # Passos de tempo

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