from actuator import Actuator
from broker import Broker
from production_plant import ProductionPlant
from sensors import Sensor, SensorTypeEnum, SensorRoleEnum
import globals
import random
from utils.colors import *
import time
from utils.timers import remove_timer

class Simulator:
    instance: 'Simulator' = None
    
    # -------------- SIMULATION PARAMETERS --------------
    NUMBER_OF_SENSORS = 5
    
    def __init__(self):
        self.reset()
    
    @classmethod
    def get_instance(cls):
        if not cls.instance:
            cls.instance = Simulator()
        return cls.instance
    
    def next_sensor_id(self) -> int:
        globals.last_sensor_id += 1
        return globals.last_sensor_id
    
    def reset(self) -> None:
        globals.should_stop = False
        globals.time = 0
        globals.plant = ProductionPlant()
        globals.actuator = Actuator(globals.plant)
        globals.broker = Broker()
        globals.last_sensor_id = 0
        globals.is_running = False
        self.initialize_sensors(globals.plant, globals.broker)
        
    def advance_time(self, steps: int = 1) -> None:
        globals.time += steps
        
    def initialize_sensors(self, plant: 'ProductionPlant', broker: 'Broker') -> None:
        for _ in range(self.NUMBER_OF_SENSORS):
            normal_min = random.randint(50, 100)
            normal_max = random.randint(normal_min+1, 120)
            degraded = (random.randint(30, normal_min-1),
                        random.randint(normal_max+1, 140))
            critical = (random.randint(0, degraded[0]-1), 
                        random.randint(degraded[1]+1, 170))
            sensor = Sensor(
                sensor_id=self.next_sensor_id(),
                # We will use the same sensor type to infer pragmatics with the same semantics
                sensor_type=SensorTypeEnum.TEMPERATURE,
                role=random.choice(list(SensorRoleEnum)),
                operating_range={  # TODO: Mocked and static values, change it
                    "normal": (normal_min, normal_max),
                    "degraded": degraded,
                    "critical": critical
                },
                mean_value=random.uniform(normal_min, normal_max),  # This value should be in the normal range
                # Sensors that send data in a interval between 1 ms and 5 seconds
                sampling_interval=random.randint(1, 5000)
            )
            print(f'{CYAN}Sensor {sensor.sensor_id} initialized with role {sensor.role} and sampling interval {sensor.sampling_interval} ms{RESET}')
            plant.add_sensor(sensor)
            broker.subscribe(sensor)
            
    def handle_timers(self):
        for time, func in sorted(globals.timers):
            if globals.time >= time:
                func()
                remove_timer(time, func)
            else:
                break
            
    def stop(self) -> None:
        if globals.is_running:
            globals.should_stop = True
            
    def run(self, steps: int = globals.DEFAULT_TIME_STEPS) -> None:
        if globals.is_running:
            return
        globals.is_running = True
        for _ in range(steps):  # Time steps
            if globals.should_stop: 
                globals.is_running = False
                globals.should_stop = False
                break
            self.handle_timers()
            
            for sensor_id, sensor in globals.plant.sensors.items():
                if (globals.time % 60000 == 0):
                    # Update the state of the sensor only every minute
                    # It turn the simulation faster
                    sensor.update_state_by_probabilities()
                # sensor.adjust_probabilities_by_time_passing() # It will degradate over time (by the use)

                # Sensor send data only if is it time to send
                current_sensor_message = sensor.send_data()

                if current_sensor_message is None:
                    continue

                globals.broker.publish(sensor_id, current_sensor_message)

            if (globals.time % 60000 == 0):  # Simulation actuator action only for each minute
                messages = globals.broker.flush()  # Broker has all messages collected by sensors in the last minute (the algorithm should be able to choose the messages to be saved in the queue)
                # this will need to modulate the transition probabilities for the messages to matter
                # to the environment
                globals.actuator.step(messages)
                if (globals.time % 3600000 == 0):
                    print(
                        f"Global State state: {globals.actuator.global_state[0]}, Global State load: {globals.actuator.global_state[1]}, Time: {globals.time / 60000} minutes\n")

            self.advance_time(1)  # 1 ms
            if (globals.time % 59999 == 0):
                time.sleep(0.00001)   # It enable api thread to respond

        globals.is_running = False
        
        

