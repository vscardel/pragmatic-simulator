from actuator import Actuator
from broker import Broker
from production_plant import ProductionPlant
from sensors import Sensor, SensorTypeEnum, SensorRoleEnum
import globals
import json
from utils.colors import *
import random
import time
from collections import defaultdict
from utils.timers import remove_timer, add_relative_timer, add_timer


class Simulator:
    instance: 'Simulator' = None

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

    def short_reset(self):
        globals.time = 0
        globals.is_running = False
        globals.is_training = False
        globals.is_human = False
        globals.timers = []
        globals.mean_reaction_time_degraded = 0
        globals.mean_reaction_time_critical = 0
        globals.degraded_maintenances = 0
        globals.critical_maintenances = 0
        globals.total_maintenance_time = 0
        globals.logs = []
        self.passed_time_in_NORMAL = 0
        self.passed_time_in_DEGRADED = 0
        self.passed_time_in_CRITICAL = 0
        self.passed_time_in_FAILURE = 0
        self.time_with_available_teams = 0
        self.time_without_available_teams = 0
        self.file = open("results.csv", "w")
        self.file.write("time,state,measured_state,passed_time_in_NORMAL,passed_time_in_DEGRADED,passed_time_in_CRITICAL,passed_time_in_FAILURE,mean_reaction_time_degraded,mean_reaction_time_critical,total_maintenances,total_maintenance_time,unnecessary_maintenances,total_broker_messages,upkeep_broker_messages,necessary_upkeep_broker_messages,available_teams,time_with_available_teams,time_without_available_teams,correct_role_inference,incorrect_role_inference,correct_state_inference,incorrect_state_inference\n")
        self.file.close()
        self.file = open("results.csv", "a")

        globals.last_sensor_id = 0
        globals.plant.sensors = {}
        self.initialize_sensors(globals.plant, globals.broker)

    def reset(self) -> None:
        globals.should_stop = False
        globals.plant = ProductionPlant()
        globals.actuator = Actuator(globals.plant)
        globals.broker = Broker()
        globals.q_table = defaultdict(lambda: [0.0, 0.0])
        
        self.short_reset()
        

    def advance_time(self, steps: int = 1) -> None:
        globals.time += steps

    def initialize_sensors(self, plant: 'ProductionPlant', broker: 'Broker') -> None:
        with open("sensors_config.json", "r", encoding="utf-8") as f:
            sensors_config = json.load(f)

        role_map = {
            "CRITICAL": SensorRoleEnum.CRITICAL,
            "NORMAL": SensorRoleEnum.NORMAL,
            "UNINPORTANT": SensorRoleEnum.UNINPORTANT,
        }

        type_map = {
            "TEMPERATURE": SensorTypeEnum.TEMPERATURE,
        }

        for cfg in sensors_config:
            role = role_map[cfg["role"]]

            operating_range = {
                "normal": tuple(cfg["operating_range"]["normal"]),
                "degraded": tuple(cfg["operating_range"]["degraded"]),
                "critical": tuple(cfg["operating_range"]["critical"]),
            }

            sensor = Sensor(
                sensor_id=self.next_sensor_id(),
                sensor_label=cfg["label"],
                sensor_type=type_map[cfg["type"]],
                role=role,
                operating_range=operating_range,
                mean_value=cfg["mean_value"],
                sampling_interval=cfg["sampling_interval"],
            )

            plant.add_sensor(sensor)

    def handle_timers(self):
        for time, id, func in sorted(globals.timers, key=lambda x: x[0]):
            if globals.time >= time:
                func()
                remove_timer(id)
            else:
                break

    def save_data(self):
        total_broker_messages = globals.broker.do_nothing_count + globals.broker.upkeep_count

        self.file.write(f"{globals.time},{globals.plant.state.name}:{globals.plant.state.value},{globals.plant.measured_state},{self.passed_time_in_NORMAL},{self.passed_time_in_DEGRADED},{self.passed_time_in_CRITICAL},{self.passed_time_in_FAILURE},{globals.mean_reaction_time_degraded},{globals.mean_reaction_time_critical},{globals.actuator.total_maintenances},{globals.total_maintenance_time},{globals.actuator.unnecessary_maintenances},{total_broker_messages},{globals.broker.upkeep_count},{globals.broker.necessary_upkeep_count},{globals.actuator.available_teams},{self.time_with_available_teams},{self.time_without_available_teams},{globals.actuator.correct_inferred_role},{total_broker_messages - globals.actuator.correct_inferred_role},{globals.actuator.correct_inferred_state},{total_broker_messages - globals.actuator.correct_inferred_state}\n")

    def stop(self) -> None:
        self.save_data()
        if globals.is_running:
            globals.should_stop = True

    def stop_training(self) -> None:
        self.stop()
        self.short_reset()
        self.initialize_all_sensors_transition_probabilities()

        globals.is_training = False

    def initialize_all_sensors_transition_probabilities(self, is_training: bool = False):
        for sensor in globals.plant.sensors.values():
            sensor.initialize_transition_probabilities(is_training)

    def update_all_sensors_state_by_probabilities(self):
        for sensor in globals.plant.sensors.values():
            sensor.update_state_by_probabilities()

    def save_data_timer(self):
        self.save_data()
        self.file.flush()

        add_relative_timer(globals.SAVE_DATA_INTERVAL, self.save_data_timer)

    def train(self, steps: int = globals.DEFAULT_TIME_STEPS) -> None:
        if globals.is_running:
            return
        globals.is_training = True
        self.initialize_all_sensors_transition_probabilities(is_training=True)
        self.run(steps, is_training=True)
        
    def run_for_humans(self, steps: int = globals.DEFAULT_TIME_STEPS) -> None:
        globals.is_human = True
        self.run(steps)

    def run(self, steps: int = globals.DEFAULT_TIME_STEPS, is_training: bool = False) -> None:
        if globals.is_running:
            return
        globals.is_running = True
        self.save_data_timer()
        for _ in range(steps):  # Time steps
            if globals.should_stop:
                globals.is_running = False
                globals.should_stop = False
                break

            self.handle_timers()

            sensors = list(globals.plant.sensors.items())
            random.shuffle(sensors)
            for sensor_id, sensor in  sensors:
                if ((globals.time % globals.STEP_JUMP == 0 and not is_training) or 
                    (is_training and globals.time % globals.UPDATE_STATE_INTERVAL_IN_TRAINING == 0)
                    ):
                    # Update the state of the sensor only every second
                    # It turn the simulation faster
                    sensor.update_state_by_probabilities()
                
                # sensor.adjust_probabilities_by_time_passing() # It will degradate over time (by the use)

                # Sensor send data only if is it time to send
                current_sensor_message = sensor.send_data()

                if current_sensor_message is None:
                    continue

                globals.broker.publish(sensor_id, current_sensor_message)

            # Simulation actuator action only for each minute
            if (globals.time % globals.STEP_JUMP == 0):
                #     messages = globals.broker.flush()  # Broker has all messages collected by sensors in the last minute (the algorithm should be able to choose the messages to be saved in the queue)
                #     # this will need to modulate the transition probabilities for the messages to matter
                #     # to the environment

                #     globals.actuator.step(messages)
                globals.actuator.update_global_state()

            if (globals.plant.state.name == 'NORMAL'):
                self.passed_time_in_NORMAL += globals.STEP_JUMP
            elif (globals.plant.state.name == 'DEGRADED'):
                self.passed_time_in_DEGRADED += globals.STEP_JUMP
            elif (globals.plant.state.name == 'CRITICAL'):
                self.passed_time_in_CRITICAL += globals.STEP_JUMP
            elif (globals.plant.state.name == 'FAILURE'):
                self.passed_time_in_FAILURE += globals.STEP_JUMP

            if (globals.actuator.available_teams > 0):
                self.time_with_available_teams += globals.STEP_JUMP
            else:
                self.time_without_available_teams += globals.STEP_JUMP
                if (globals.actuator.available_teams < globals.MAX_ACTUATOR_TEAMS):
                    globals.total_maintenance_time += globals.STEP_JUMP

            self.advance_time(globals.STEP_JUMP)  # 1 s

            if (globals.time % (globals.STEP_JUMP * 5) == 0 and globals.is_human):
                last_pause_time = time.time()
                time.sleep(1 / 1000 * globals.STEP_JUMP - (time.time() - last_pause_time))

        globals.is_running = False
