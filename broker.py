import heapq
import itertools
from typing import Any
from sensors import SensorRoleEnum, Sensor, SensorMessage
from typing import List, Tuple
import random
from collections import Counter
from utils.colors import *
import globals
from production_plant import GlobalStateEnum


class BrokerMessage:
    def __init__(self, sensor_id: int, inferred_role: int, inferred_state: int, sensor_message: SensorMessage) -> None:
        self.sensor_id = sensor_id
        self.inferred_role = inferred_role
        self.inferred_state = inferred_state
        self.sensor_message = sensor_message


class Broker:
    def __init__(self) -> None:
        self.subscribers: List[int] = []  # lista de ID dos sensores
        self.queue: List[Tuple[int, int, BrokerMessage]] = []
        self.MAX_QUEUE_SIZE = 1000
        self.DROPPED_MESSAGES_COUNT = 0
        self.DROPPED_MESSAGES_BY_FULL_QUEUE = 0
        self.ROUND_DROPPED_MESSAGES_COUNT = 0
        self.ROUND_DROPPED_MESSAGES_BY_FULL_QUEUE = 0
        self._counter = itertools.count()

    # To publish, a sensor should be subscribed
    def subscribe(self, sensor: Sensor):
        self.subscribers.append(sensor.sensor_id)

    def publish(self, sensor_id: int, data: SensorMessage) -> bool:
        if (sensor_id not in self.subscribers):
            print(f"{RED}Sensor not subscribed to broker.{RESET}")
            return False

        if len(self.queue) >= self.MAX_QUEUE_SIZE:
            self.DROPPED_MESSAGES_COUNT += 1
            self.DROPPED_MESSAGES_BY_FULL_QUEUE += 1
            self.ROUND_DROPPED_MESSAGES_COUNT += 1
            self.ROUND_DROPPED_MESSAGES_BY_FULL_QUEUE += 1
            print(f"{YELLOW}Broker queue full. Dropping message.{RESET}")
            return False

        # TODO: infer sensor role and state by context instead of passing it randomly
        inferred_role = random.choice(list(SensorRoleEnum)).value
        inferred_state = random.choice(list(GlobalStateEnum)).value

        # TODO: the algorithm should define this number (this calcule is just a placeholder)
        priority_number = inferred_role * inferred_state

        heapq.heappush(
            self.queue,
            (priority_number, next(self._counter), BrokerMessage(sensor_id=sensor_id,
                                                                 inferred_role=inferred_role,
                                                                 inferred_state=inferred_state,
                                                                 sensor_message=data)))

        return True

    def print_queue_stats(self):
        """
        Prints the percentage of each sensor role and sensor in the broker queue.

        Prints two tables: one with the percentage of messages of each sensor role in the broker queue
        and another with the percentage of messages of each sensor in the broker queue.

        :return: None
        """
        total_items = len(self.queue)

        if total_items == 0:
            print("Broker queue is empty.")
            return

        enum_counts = Counter(item.inferred_role for _,_,item in self.queue)

        print(f"{BLUE}=== Percentage by Sensor Role in Broker Queue ==={RESET}")
        for enum_val, count in enum_counts.items():
            percentage = (count / total_items) * 100
            print(f"{BLUE}Role {SensorRoleEnum(enum_val)}: {percentage:.4f}%{RESET}")

        sensor_counts = Counter(item.sensor_id for _,_,item in self.queue)

        print(f"{BLUE}=== Percentage by Sensor in Broker Queue ==={RESET}")
        for sensor_id, count in sensor_counts.items():
            percentage = (count / total_items) * 100
            print(f"{BLUE}Sensor '{sensor_id}': {percentage:.4f}%{RESET}")

    def flush(self) -> List[BrokerMessage]:
        if (globals.time % 3600000 == 0):
            self.print_queue_stats()

        msgs: List[BrokerMessage] = []
        while self.queue:
            msgs.append(heapq.heappop(self.queue)[2])

        self.ROUND_DROPPED_MESSAGES_BY_FULL_QUEUE = 0
        self.ROUND_DROPPED_MESSAGES_COUNT = 0

        return msgs
