import random
from production_plant import ProductionPlant
from sensors import Sensor, SensorRoleEnum, SensorTypeEnum
from broker import Broker
import time
from globals import Globals
from actuator import Actuator
from typing import Any

NUMBER_OF_SENSORS = 5

# We can model it to be milliseconds
TIME_STEPS = 24 * 60 * 60 * 1000 # 24 hours

RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"

def initialize_sensors(plant: ProductionPlant, broker: Broker):
    for _ in range(NUMBER_OF_SENSORS):
        
        sensor = Sensor(
            sensor_id=Sensor.next_id(),
            sensor_type=SensorTypeEnum.TEMPERATURE,
            role=random.choice(list(SensorRoleEnum)),
            operating_range={ # TODO: Mocked and static values, change it 
                "normal": (50, 60),
                "degraded": (40, 70),
                "critical": (30, 95)
            },
            mean_value=55,
            sampling_interval=random.randint(1 , 5000) # Sensors that send data in a interval between 1 ms and 5 seconds
        )  
        print(f'{CYAN}Sensor {sensor.sensor_id} initialized with role {sensor.role} and sampling interval {sensor.sampling_interval} ms{RESET}')
        plant.add_sensor(sensor)
        broker.subscribe(sensor)
                

if __name__ == "__main__":
    plant = ProductionPlant()
    broker = Broker()
    actuator = Actuator(plant)
    Globals.actuator = actuator
    initialize_sensors(plant, broker)

    for lt in range(TIME_STEPS): # Time steps
        for id, sensor in plant.sensors.items():
            if (Globals.time % 60000 == 0): 
                # Update the state of the sensor only every minute
                sensor.update_state_by_probabilities()
            # sensor.adjust_probabilities_by_time_passing() # It will degradate over time (by the use)
            
            current_sensor_message = sensor.send_data()
            
            if current_sensor_message is None:
                continue
            
            broker.publish(sensor.sensor_id, current_sensor_message)
    
        if (Globals.time % 60000 == 0): # We see actuator actions every minute 
            messages = broker.flush()
            # this will need to modulate the transition probabilities for the messages to matter
            # to the environment
            actuator.step(messages)
            if (Globals.time % 3600000 == 0): 
                print(f"Global State state: {actuator.global_state[0]}, Global State load: {actuator.global_state[1]}, Time: {Globals.time / 60000} minutes\n")
                
                input("Press enter to continue...")
            # time.sleep(0.5)
        
        Globals.time += 1  # 1 ms
        
