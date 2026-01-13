class Broker:
    def __init__(self):
        self.subscribers = []
        self.queue = []
        self.MAX_QUEUE_SIZE = 100
        self.DROPPED_MESSAGES_COUNT = 0

    def subscribe(self, sensor):
        self.subscribers.append(sensor.sensor_id)

    def publish(self, sensor_id, data):
        if len(self.queue) > self.MAX_QUEUE_SIZE:
            self.DROPPED_MESSAGES_COUNT += 1
            print("Broker queue full. Dropping message.")
            return False
        if sensor_id in self.subscribers:
            self.queue.append(data)
            print(f"Published data: {data} from sensor ID: {sensor_id}")
            return True
        print("Sensor not subscribed to broker.")
        return False
