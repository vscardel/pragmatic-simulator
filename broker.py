import heapq
import itertools
import uuid
from typing import Any
from sensors import SensorRoleEnum, Sensor
from typing import List, Tuple
import random

class Broker:
    def __init__(self) -> None:
        self.subscribers: List[uuid.UUID] = [] # lista de ID dos sensores
        self.queue: List[Tuple[int, int, Any]] = []
        self.MAX_QUEUE_SIZE = 10000
        self.DROPPED_MESSAGES_COUNT = 0
        self._counter = itertools.count()

    def subscribe(self, sensor: Sensor):
        self.subscribers.append(sensor.sensor_id)

    def publish(self, sensor_id: uuid.UUID, data: list[dict[str, Any]]) -> bool:
        if len(self.queue) > self.MAX_QUEUE_SIZE:
            self.DROPPED_MESSAGES_COUNT += 1
            print("Broker queue full. Dropping message.")
            return False
        if sensor_id in self.subscribers:
            # TODO: infer sensor role by context instead of passing it randomly
            heapq.heappush(
                self.queue,
                (random.choice(list(SensorRoleEnum)).value, next(self._counter), data)
            )
            return True
        print("Sensor not subscribed to broker.")
        return False

    def flush(self):
        msgs = []
        while self.queue:
            msgs.append(heapq.heappop(self.queue))
        return msgs

