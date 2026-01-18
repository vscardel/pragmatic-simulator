import heapq
import itertools
from typing import Any
from sensors import SensorRoleEnum, Sensor
from typing import List, Tuple
import random
from globals import Globals
from collections import Counter

RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"

class Broker:
    def __init__(self) -> None:
        self.subscribers: List[int] = [] # lista de ID dos sensores
        self.queue: List[Tuple[int, int, dict[str, Any]]] = []
        self.MAX_QUEUE_SIZE = 1000
        self.DROPPED_MESSAGES_COUNT = 0
        self.DROPPED_MESSAGES_BY_FULL_QUEUE = 0
        self.ROUND_DROPPED_MESSAGES_COUNT = 0
        self.ROUND_DROPPED_MESSAGES_BY_FULL_QUEUE = 0
        self._counter = itertools.count()

    # To publish, a sensor should be subscribed
    def subscribe(self, sensor: Sensor):
        self.subscribers.append(sensor.sensor_id)

    def publish(self, sensor_id: int, data: dict[str, Any]) -> bool:
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
        
        # TODO: infer sensor role by context instead of passing it randomly
        heapq.heappush(
            self.queue,
            (random.choice(list(SensorRoleEnum)).value, next(self._counter), data)
        )
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

        enum_counts = Counter(item[0] for item in self.queue)

        print(f"{BLUE}=== Percentage by Sensor Role in Broker Queue ==={RESET}")
        for enum_val, count in enum_counts.items():
            percentage = (count / total_items) * 100
            print(f"{BLUE}Role {SensorRoleEnum(enum_val)}: {percentage:.4f}%{RESET}")

        sensor_counts = Counter(item[2]['sensor_id'] for item in self.queue)

        print(f"{BLUE}=== Percentage by Sensor in Broker Queue ==={RESET}")
        for sensor_id, count in sensor_counts.items():
            percentage = (count / total_items) * 100
            print(f"{BLUE}Sensor '{sensor_id}': {percentage:.4f}%{RESET}")

    def flush(self) -> List[Tuple[int, int, dict[str, Any]]]:
        if (Globals.time % 3600000 == 0):
            self.print_queue_stats()
        
        msgs = []
        while self.queue:
            msgs.append(heapq.heappop(self.queue))
            
        self.ROUND_DROPPED_MESSAGES_BY_FULL_QUEUE = 0
        self.ROUND_DROPPED_MESSAGES_COUNT = 0
        
        return msgs
        
        
        
