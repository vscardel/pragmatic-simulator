import heapq
import itertools


class Broker:
    def __init__(self):
        self.subscribers = []
        self.queue = []
        self.MAX_QUEUE_SIZE = 100
        self.DROPPED_MESSAGES_COUNT = 0
        self._counter = itertools.count()

    def subscribe(self, sensor):
        self.subscribers.append(sensor.sensor_id)

    def publish(self, sensor_id, sensor_role, data):
        if len(self.queue) > self.MAX_QUEUE_SIZE:
            self.DROPPED_MESSAGES_COUNT += 1
            print("Broker queue full. Dropping message.")
            return False
        if sensor_id in self.subscribers:
            # TODO: infer sensor role by context instead of passing it directly
            heapq.heappush(
                self.queue,
                (sensor_role.value, next(self._counter), data)
            )
            print(f"Published data: {data} from sensor ID: {sensor_id}")
            return True
        print("Sensor not subscribed to broker.")
        return False

    def process_messages(self):
        while self.queue:
            message = heapq.heappop(self.queue)
            print(f"Processing message: {message} with priority {message[0]}")
