from actuator import Actuator
from broker import Broker
from production_plant import ProductionPlant
from sensors import Sensor, SensorTypeEnum, SensorRoleEnum
import globals
import random
from utils.colors import *
import time
from utils.timers import remove_timer, add_relative_timer

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
    
    def reset(self) -> None:
        globals.should_stop = False
        globals.time = 0
        globals.plant = ProductionPlant()
        globals.actuator = Actuator(globals.plant)
        globals.broker = Broker()
        globals.last_sensor_id = 0
        globals.is_running = False
        globals.timers = []
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
        
        self.initialize_sensors(globals.plant, globals.broker)
        
    def advance_time(self, steps: int = 1) -> None:
        globals.time += steps
        
    def initialize_sensors(self, plant: 'ProductionPlant', broker: 'Broker') -> None:
        sensorBoiler = Sensor(
            sensor_id=self.next_sensor_id(),
            sensor_label="Caldeira",
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
            sensor_label="Mancal_Motor_Eletrico",
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
            sensor_label="Tanque_Oleo_Hidraulico",
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
            sensor_label="Camara_Fria",
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
            sensor_label="Ambiente",
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


        # Lista de configurações para 25 novas máquinas/ambientes
        # Formato: (NomeDescritivo, (MinNorm, MaxNorm), (MinDeg, MaxDeg), (MinCrit, MaxCrit), ValorMedio)
        sensor_configs = [
            # --- Elétrica e Energia ---
            ("Trafo_Enrolamento_AT", (60, 95), (50, 105),
            (40, 130), 80),   # Transformador Alta Tensão
            # Sala de Baterias (Crítico p/ vida útil)
            ("Banco_Baterias_Nobreak", (20, 25), (15, 30), (10, 45), 23),
            ("Gerador_Diesel_Exaustao", (400, 550),
            (350, 600), (300, 700), 480),  # Gás de exaustão
            ("Inversor_Solar_IGBT", (40, 65), (30, 80),
            (10, 95), 55),      # Dissipador de calor
            # Ponto de conexão elétrica (risco de arco)
            ("Barramento_QGBT_Principal", (30, 50), (20, 70), (10, 90), 40),

            # --- Mecânica Pesada ---
            ("Redutor_Turbina_Eolica", (50, 75), (40, 85), (20, 100), 65),  # Óleo do redutor
            # Tambor de freio (pico intermitente)
            ("Freio_Ponte_Rolante", (30, 150), (20, 200), (10, 300), 80),
            ("Cabecote_Compressor_Ar", (70, 90), (60, 105),
            (40, 120), 82),  # Saída de ar comprimido
            ("Mancal_Ventilador_Exaustor", (35, 60),
            (25, 75), (10, 90), 45),  # Vibração gera calor
            # Carcaça da bomba (cavitação aquece)
            ("Bomba_Centrifuga_Housing", (30, 50), (20, 70), (10, 90), 40),

            # --- Processos Industriais (Plástico/Química) ---
            ("Extrusora_Zona_Alimentacao", (180, 200),
            (160, 220), (140, 240), 190),  # Plástico derretido
            ("Molde_Injecao_Refrigeracao", (40, 60), (30, 70),
            (20, 90), 50),        # Água gelada no molde
            ("Reator_Quimico_Exotermico", (120, 130),
            (110, 140), (100, 160), 125),  # Reação perigosa
            ("Tanque_Fermentacao_Cerveja", (18, 22), (15, 25),
            (10, 30), 20),        # Levedura sensível
            ("Coluna_Destilacao_Topo", (78, 82), (75, 85),
            (70, 95), 80),            # Separação de álcool

            # --- Infraestrutura e TI ---
            ("Datacenter_Corredor_Frio", (18, 24), (15, 27),
            (10, 32), 21),  # Entrada de ar nos servidores
            ("Datacenter_Corredor_Quente", (25, 35),
            (20, 40), (15, 50), 30),  # Saída de ar
            ("Sala_UPS_Potencia", (20, 26), (18, 30),
            (15, 40), 24),        # Equipamentos sensíveis
            ("Torre_Resfriamento_Agua", (25, 32),
            (20, 38), (15, 45), 29),  # Água industrial
            # Controle de legionella/qualidade
            ("Caixa_Dagua_Potavel", (15, 25), (10, 30), (5, 40), 22),

            # --- Processos Térmicos Específicos ---
            ("Forno_Ceramica", (980, 1020), (950, 1050),
            (900, 1200), 1000),  # Alta temperatura
            ("Estufa_Secagem_Pintura", (150, 180),
            (130, 200), (100, 250), 165),  # Cura de tinta
            ("Tanque_Nitrogenio_Liq", (-196, -180),
            (-200, -170), (-210, -150), -190),  # Criogenia
            ("Solda_Robo_Ponta", (250, 350), (200, 400),
            (100, 500), 300),   # Processo intermitente
            ("Autoclave_Esterilizacao", (121, 134), (115, 140),
            (100, 150), 127)  # Hospitalar/Laboratório
        ]

        # Lista onde os sensores serão armazenados
        additional_sensors = []

        roles = [SensorRoleEnum.CRITICAL,
                SensorRoleEnum.NORMAL, SensorRoleEnum.UNINPORTANT]

        for name, range_norm, range_deg, range_crit, mean_val in sensor_configs:
            new_sensor = Sensor(
                # Assumindo que este método existe no seu contexto
                sensor_id=self.next_sensor_id(),
                sensor_label=name,
                sensor_type=SensorTypeEnum.TEMPERATURE,
                role=random.choice(roles),  # Role aleatória
                operating_range={
                    "normal": range_norm,
                    "degraded": range_deg,
                    "critical": range_crit,
                },
                mean_value=mean_val,
                sampling_interval=1000
            )


            additional_sensors.append(new_sensor)

        # Lista de configurações para o Lote 2 (foco em críticos)
        # Formato: (NomeDescritivo, (MinNorm, MaxNorm), (MinDeg, MaxDeg), (MinCrit, MaxCrit), ValorMedio, Role)
        sensor_configs_critical_batch = [
            # --- CRÍTICOS (Aprox. 50% - Foco em Segurança e Parada Total) ---
            # 1. Caldeira de alta pressão: Risco de explosão iminente se superaquecer
            ("Caldeira_Vapor_Alta_Pressao", (240, 260),
            (220, 280), (200, 300), 250, SensorRoleEnum.CRITICAL),

            # 2. Reator Nuclear (Circuito Primário Simul.): Falha catastrófica
            ("Reator_Nuclear_Nucleo", (300, 320), (290, 335),
            (280, 350), 310, SensorRoleEnum.CRITICAL),

            # 3. Bomba de Incêndio (Motor Diesel): Se falhar na emergência, a planta queima
            ("Motor_Bomba_Incendio", (85, 95), (80, 105),
            (70, 120), 90, SensorRoleEnum.CRITICAL),

            # 4. Tanque de Amônia (Refrigeração Industrial): Vazamento tóxico por pressão/temp
            ("Tanque_Armazenamento_Amonia", (-25, -15),
            (-30, -10), (-40, 0), -20, SensorRoleEnum.CRITICAL),

            # 5. Turbina a Gás (Eixo Principal): Desbalanceamento térmico quebra as palhetas
            ("Turbina_Gas_Eixo", (450, 500), (400, 550),
            (350, 650), 480, SensorRoleEnum.CRITICAL),

            # 6. Sala de Servidores (Mainframe Financeiro): Perda de dados = prejuízo milionário
            ("DataCenter_Mainframe_CPU", (40, 60), (30, 75),
            (20, 90), 50, SensorRoleEnum.CRITICAL),

            # 7. Forno de Siderurgia (Cúpula): Se esfriar, o metal solidifica e perde o forno
            ("Forno_Siderurgica_Gusa", (1400, 1500), (1350, 1550),
            (1300, 1600), 1450, SensorRoleEnum.CRITICAL),

            # 8. Ventilação de Mina Subterrânea: Falha pode asfixiar trabalhadores
            ("Ventilador_Mina_Subterranea", (30, 50),
            (20, 70), (10, 90), 40, SensorRoleEnum.CRITICAL),

            # 9. Autoclave de Esterilização (Hospitalar/Lab): Risco biológico se falhar
            ("Autoclave_Bio_Seguranca", (121, 135), (115, 140),
            (100, 150), 125, SensorRoleEnum.CRITICAL),

            # 10. Sistema de Freio (Prensa Hidráulica 500T): Falha de segurança operacional
            ("Freio_Prensa_Hidraulica", (40, 70), (30, 90),
            (20, 120), 55, SensorRoleEnum.CRITICAL),


            # --- NORMAIS (Produção e Manutenção) ---
            # 11. Esteira de Embalagem: Parada gera gargalo, mas não perigo
            ("Motor_Esteira_Embalagem", (40, 60), (30, 75),
            (20, 90), 50, SensorRoleEnum.NORMAL),

            # 12. Tanque de Água de Reuso: Usada para limpeza de pátio
            ("Tanque_Agua_Reuso", (20, 30), (10, 40), (5, 50), 25, SensorRoleEnum.NORMAL),

            # 13. Misturador de Tinta Industrial: Afeta qualidade do lote
            ("Misturador_Tanque_Tinta", (35, 45), (30, 55),
            (20, 70), 40, SensorRoleEnum.NORMAL),

            # 14. Compressor da Oficina de Manutenção: Ferramentas param
            ("Compressor_Ar_Oficina", (70, 85), (60, 95),
            (50, 110), 78, SensorRoleEnum.NORMAL),

            # 15. Estufa de Secagem de Madeira: Controle de umidade/temp lento
            ("Estufa_Secagem_Madeira", (50, 70), (40, 80),
            (30, 100), 60, SensorRoleEnum.NORMAL),


            # --- UNIMPORTANT (Conforto e Auxiliares) ---
            # 16. Ar Condicionado da Guarita: Conforto do porteiro
            ("AC_Guarita_Entrada", (22, 25), (20, 28),
            (18, 35), 23, SensorRoleEnum.UNINPORTANT),

            # 17. Bebedouro do Chão de Fábrica: Água gelada para funcionários
            ("Bebedouro_Fabrica_Agua", (8, 12), (5, 15),
            (2, 20), 10, SensorRoleEnum.UNINPORTANT),

            # 18. Aquecedor do Vestiário: Água do chuveiro
            ("Aquecedor_Boiler_Vestiario", (38, 45), (30, 50),
            (20, 60), 42, SensorRoleEnum.UNINPORTANT),

            # 19. Máquina de Café do Lounge: O café sai frio
            ("Maquina_Cafe_Caldeira", (90, 95), (85, 98),
            (70, 105), 92, SensorRoleEnum.UNINPORTANT),

            # 20. Driver de LED do Estacionamento: Iluminação externa
            ("Driver_LED_Poste", (30, 50), (20, 60),
            (10, 80), 40, SensorRoleEnum.UNINPORTANT),
        ]

        random.shuffle(sensor_configs_critical_batch)
        for name, range_norm, range_deg, range_crit, mean_val, role_def in sensor_configs_critical_batch:
            new_sensor = Sensor(
                sensor_id=self.next_sensor_id(),
                sensor_label=name,
                sensor_type=SensorTypeEnum.TEMPERATURE,
                role=role_def,  # Usa a role específica definida acima
                operating_range={
                    "normal": range_norm,
                    "degraded": range_deg,
                    "critical": range_crit,
                },
                mean_value=mean_val,
                sampling_interval=1000
            )

            additional_sensors.append(new_sensor)
                
        plant.add_sensor(sensorBoiler)
        plant.add_sensor(sensorMotorBearing)
        plant.add_sensor(sensorHydraulicOil)
        plant.add_sensor(sensorColdStorage)
        plant.add_sensor(sensorOfficeHVAC)
        
        for sensor in additional_sensors:
            plant.add_sensor(sensor)
            
    def handle_timers(self):
        for time, id, func in sorted(globals.timers, key=lambda x: x[0]):
            if globals.time >= time:
                func()
                remove_timer(id)
            else:
                break
        
    def save_data(self):
        
        total_maintenance_time = sum([sensor.get_total_maintenance_time() for sensor in globals.plant.sensors.values()])
        total_broker_messages = globals.broker.do_nothing_count + globals.broker.upkeep_count
        
        self.file.write(f"{globals.time},{globals.plant.state.name}:{globals.plant.state.value},{globals.plant.measured_state},{self.passed_time_in_NORMAL},{self.passed_time_in_DEGRADED},{self.passed_time_in_CRITICAL},{self.passed_time_in_FAILURE},{globals.mean_reaction_time_degraded},{globals.mean_reaction_time_critical},{globals.actuator.total_maintenances},{total_maintenance_time},{globals.actuator.unnecessary_maintenances},{total_broker_messages},{globals.broker.upkeep_count},{globals.broker.necessary_upkeep_count},{globals.actuator.available_teams},{self.time_with_available_teams},{self.time_without_available_teams},{globals.actuator.correct_inferred_role},{total_broker_messages - globals.actuator.correct_inferred_role},{globals.actuator.correct_inferred_state},{total_broker_messages - globals.actuator.correct_inferred_state}\n")
        
    def stop(self) -> None:
        self.save_data()
        if globals.is_running:
            globals.should_stop = True
            
    def save_data_timer(self):
        self.save_data()
        self.file.flush()
        
        add_relative_timer(globals.SAVE_DATA_INTERVAL, self.save_data_timer)
            
    def run(self, steps: int = globals.DEFAULT_TIME_STEPS) -> None:
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
            
            for sensor_id, sensor in globals.plant.sensors.items():
                if (globals.time % globals.STEP_JUMP == 0):
                    # Update the state of the sensor only every second
                    # It turn the simulation faster
                    sensor.update_state_by_probabilities()
                # sensor.adjust_probabilities_by_time_passing() # It will degradate over time (by the use)

                # Sensor send data only if is it time to send
                current_sensor_message = sensor.send_data()

                if current_sensor_message is None:
                    continue

                globals.broker.publish(sensor_id, current_sensor_message)

            if (globals.time % globals.STEP_JUMP == 0):  # Simulation actuator action only for each minute
                messages = globals.broker.flush()  # Broker has all messages collected by sensors in the last minute (the algorithm should be able to choose the messages to be saved in the queue)
                # this will need to modulate the transition probabilities for the messages to matter
                # to the environment
                
                globals.actuator.step(messages)
            
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
                
            self.advance_time(globals.STEP_JUMP)  # 1 s
                
            # if (globals.time % (globals.STEP_JUMP * 1000) == 0):
            #     last_pause_time = time.time()
            #     time.sleep(1 / 1000 * globals.STEP_JUMP - (time.time() - last_pause_time))

        globals.is_running = False
        
        

