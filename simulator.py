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
        sensorBoiler = Sensor(
            sensor_id=self.next_sensor_id(),
            sensor_type=SensorTypeEnum.TEMPERATURE,
            role=SensorRoleEnum.CRITICAL,
            operating_range={
                "normal": (190, 240),
                "degraded": (160, 290),
                "critical": (150, 310),
            },
            mean_value=210,
            sampling_interval=1000
        )
        

        # 1. Sensor de Mancal de Motor Elétrico de Grande Porte
        # Monitora superaquecimento por atrito. Alta vibração ou falta de lubrificação geram calor rápido.
        sensorMotorBearing = Sensor(
            sensor_id=self.next_sensor_id(),
            sensor_type=SensorTypeEnum.TEMPERATURE,
            role=SensorRoleEnum.CRITICAL,  # Se o mancal travar, a linha para imediatamente
            operating_range={
                "normal": (40, 75),    # Operação segura (aquecido, mas estável)
                # Aviso: Lubrificação necessária ou início de desgaste
                "degraded": (30, 90),
                "critical": (20, 110),  # Perigo: Risco iminente de fusão/travamento
            },
            mean_value=65,
            sampling_interval=1000
        )

        # 2. Sensor de Tanque de Óleo Hidráulico
        # Monitora a temperatura do fluido de prensas ou injetoras.
        sensorHydraulicOil = Sensor(
            sensor_id=self.next_sensor_id(),
            sensor_type=SensorTypeEnum.TEMPERATURE,
            role=SensorRoleEnum.NORMAL,  # Importante para a vida útil, mas falha lenta
            operating_range={
                "normal": (35, 55),    # Viscosidade ideal do óleo
                # Óleo muito frio (cravitação) ou muito quente (oxidação)
                "degraded": (25, 65),
                "critical": (10, 80),  # Perda total de propriedades lubrificantes
            },
            mean_value=48,
            sampling_interval=1000 
        )

        # 3. Sensor de Câmara Fria (Armazenamento de Matéria-Prima)
        # Monitora conservação de químicos ou alimentos.
        sensorColdStorage = Sensor(
            sensor_id=self.next_sensor_id(),
            sensor_type=SensorTypeEnum.TEMPERATURE,
            # Perda de temperatura estraga o insumo (prejuízo financeiro)
            role=SensorRoleEnum.CRITICAL,
            operating_range={
                "normal": (-5, 2),     # Faixa estrita de conservação
                "degraded": (-8, 5),   # Porta aberta ou degelo ineficiente
                "critical": (-15, 10),  # Produto comprometido
            },
            mean_value=-1,
            sampling_interval=1000 
        )

        # 4. Sensor de Ambiente (Escritório/Vestiário)
        # Monitora conforto térmico (HVAC) para a equipe administrativa.
        sensorOfficeHVAC = Sensor(
            sensor_id=self.next_sensor_id(),
            sensor_type=SensorTypeEnum.TEMPERATURE,
            role=SensorRoleEnum.UNINPORTANT,  # Desconforto não para a produção
            operating_range={
                "normal": (21, 24),    # Conforto térmico padrão
                "degraded": (19, 27),  # Um pouco frio ou quente
                "critical": (15, 32),  # Falha do ar condicionado
            },
            mean_value=23,
            sampling_interval=1000  
        )
        
        plant.add_sensor(sensorBoiler)
        plant.add_sensor(sensorMotorBearing)
        plant.add_sensor(sensorHydraulicOil)
        plant.add_sensor(sensorColdStorage)
        plant.add_sensor(sensorOfficeHVAC)
        broker.subscribe(sensorBoiler)
        broker.subscribe(sensorMotorBearing)
        broker.subscribe(sensorHydraulicOil)
        broker.subscribe(sensorColdStorage)
        broker.subscribe(sensorOfficeHVAC)
            
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
        
        

