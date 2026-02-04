from sensors import SensorRoleEnum, SensorMessage
from typing import List
import random
from production_plant import GlobalStateEnum
from enum import Enum
import globals

class BrokerInstruction(Enum):
    DO_NOTHING = 0
    UPKEEP = 1


class BrokerMessage:
    def __init__(self, sensor_id: int, inferred_role: int, inferred_state: int, sensor_message: SensorMessage, instruction: BrokerInstruction) -> None:
        self.sensor_id = sensor_id
        self.inferred_role = inferred_role
        self.inferred_state = inferred_state
        self.sensor_message = sensor_message
        self.instruction = instruction
        


class Broker:
    def __init__(self) -> None:
        self.buffer: List[BrokerMessage] = []
        self.do_nothing_count = 0
        self.upkeep_count = 0
        self.necessary_upkeep_count = 0
        pass

    def publish(self, sensor_id: int, data: SensorMessage) -> bool:

        # TODO: infer sensor role and state by context instead of passing it randomly
        inferred_role = random.choice(list(SensorRoleEnum)).value
        inferred_state = random.choice(list(GlobalStateEnum)).value

        broker_message = BrokerMessage(
            sensor_id=sensor_id,
            inferred_role=inferred_role,
            inferred_state=inferred_state,
            sensor_message=data,
            instruction=random.choice(list(BrokerInstruction))
        )

        if broker_message.instruction == BrokerInstruction.DO_NOTHING:
            self.do_nothing_count += 1
        elif broker_message.instruction == BrokerInstruction.UPKEEP:
            self.upkeep_count += 1
            sensor = globals.plant.get_sensor(sensor_id)
            if (sensor.local_state != GlobalStateEnum.NORMAL and sensor.local_state != GlobalStateEnum.FAILURE):
                self.necessary_upkeep_count += 1

        # TODO: add instruction not to be random
        self.buffer.append(broker_message)
        
        return True


    def flush(self) -> List[BrokerMessage]:
        msgs = self.buffer
        self.buffer = []
        return msgs
