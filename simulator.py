from actuator import Actuator
from broker import Broker
from production_plant import ProductionPlant
from sensors import Sensor, SensorTypeEnum, SensorRoleEnum
import globals
import random
from utils.colors import *



class Simulator:
    instance: 'Simulator' = None
    
    # -------------- SIMULATION PARAMETERS --------------
    NUMBER_OF_SENSORS = 5
    # We can model it to be milliseconds
    TIME_STEPS = 24 * 60 * 60 * 1000  # 24 hours

    
    def __init__(self):
        self.reset()
    
    @classmethod
    def get_instance(cls):
        if not cls.instance:
            cls.instance = Simulator()
        return cls.instance
    
    def reset(self) -> None:
        globals.time = 0
        globals.plant = ProductionPlant()
        globals.actuator = Actuator(globals.plant)
        globals.broker = Broker()
        self.initialize_sensors(globals.plant, globals.broker)
        
    def advance_time(self, steps: int = 1) -> None:
        globals.time += steps
        
    def initialize_sensors(self, plant: 'ProductionPlant', broker: 'Broker') -> None:
        
        for _ in range(self.NUMBER_OF_SENSORS):
            sensor = Sensor(
                sensor_id=Sensor.next_id(),
                # We will use the same sensor type to infer pragmatics with the same semantics
                sensor_type=SensorTypeEnum.TEMPERATURE,
                role=random.choice(list(SensorRoleEnum)),
                operating_range={  # TODO: Mocked and static values, change it
                    "normal": (50, 60),
                    "degraded": (40, 70),
                    "critical": (30, 95)
                },
                mean_value=55,  # This value should be in the normal range
                # Sensors that send data in a interval between 1 ms and 5 seconds
                sampling_interval=random.randint(1, 5000)
            )
            print(f'{CYAN}Sensor {sensor.sensor_id} initialized with role {sensor.role} and sampling interval {sensor.sampling_interval} ms{RESET}')
            plant.add_sensor(sensor)
            broker.subscribe(sensor)
            
    def run(self) -> None:
        for _ in range(self.TIME_STEPS):  # Time steps
            for id, sensor in globals.plant.sensors.items():
                if (globals.time % 60000 == 0):
                    # Update the state of the sensor only every minute
                    # It turn the simulation faster
                    sensor.update_state_by_probabilities()
                # sensor.adjust_probabilities_by_time_passing() # It will degradate over time (by the use)

                # Sensor send data only if is it time to send
                current_sensor_message = sensor.send_data()

                if current_sensor_message is None:
                    continue

                globals.broker.publish(sensor.sensor_id, current_sensor_message)

            if (globals.time % 60000 == 0):  # Simulation actuator action only for each minute
                messages = globals.broker.flush()  # Broker has all messages collected by sensors in the last minute (the algorithm should be able to choose the messages to be saved in the queue)
                # this will need to modulate the transition probabilities for the messages to matter
                # to the environment
                globals.actuator.step(messages)
                if (globals.time % 3600000 == 0):
                    print(
                        f"Global State state: {globals.actuator.global_state[0]}, Global State load: {globals.actuator.global_state[1]}, Time: {globals.time / 60000} minutes\n")

                    # It can be removed after debugging
                    input("Press enter to continue...")

            self.advance_time(1)  # 1 ms
        
        

