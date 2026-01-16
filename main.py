import random
from production_plant import ProductionPlant
from sensors import Sensor, SensorRoleEnum, SensorTypeEnum
from broker import Broker
import time
from globals import Globals
from actuator import Actuator

NUMBER_OF_SENSORS = 5
TIME_STEPS = 1000 # We can model it to be milliseconds


def initialize_sensors(plant: ProductionPlant, broker: Broker):
    for _ in range(NUMBER_OF_SENSORS):
        
        sensor = Sensor(
            sensor_id=Sensor.next_id(),
            sensor_type=SensorTypeEnum.TEMPERATURE,
            role=random.choice(list(SensorRoleEnum)),
            operating_range={ # Valores mockados e estaticos, mudar depois
                "normal": (50, 60),
                "degraded": (40, 70),
                "critical": (30, 95)
            },
            mean_value=55,
            sampling_interval=random.randint(1, 5000) # Sensors that send data in a interval between 1 ms and 5 seconds
        )  
        plant.add_sensor(sensor)
        broker.subscribe(sensor)
                

if __name__ == "__main__":
    plant = ProductionPlant()
    broker = Broker()
    actuator = Actuator(plant)
    initialize_sensors(plant, broker)

    for lt in range(TIME_STEPS): # Passos de tempo
        Globals.time += 1

        for id, sensor in plant.sensors.items():
            sensor.update_state_by_probabilities()
            # sensor.adjust_probabilities_by_time_passing() # It will degradate over time (by the use)
            
            current_sensors_message = sensor.send_data()
            if current_sensors_message is None:
                continue
            broker.publish(sensor.sensor_id, current_sensors_message)

    
        messages = broker.flush()
        # this will need to modulate the transition probabilities for the messages to matter
        # to the environment
        actuator.step(messages)
        print(f"Global State: {actuator.global_state}")
        # time.sleep(0.5)
