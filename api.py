from fastapi import FastAPI
from typing import Union
import globals

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.get("/time")
def read_time():
    return {"time": globals.time}


@app.get("/actuator")
def read_actuator():
    return {
        "load": globals.actuator.load,
        "global_state": globals.actuator.global_state,
        "THRESHOLD_LOAD": globals.actuator.THRESHOLD_LOAD,
        "last_messages_impact": globals.actuator.get_last_messages_impact(),
        "last_load_term": globals.actuator.get_last_load_term(),
        "last_sensors_to_analyze": globals.actuator.get_last_sensors_to_analyze(),
        "last_sensors_sum_impact_ordered": globals.actuator.get_last_sensors_sum_impact_ordered()
    }


@app.get("/broker")
def read_broker():
    return {
        "subscribers": globals.broker.subscribers,
        "queue": globals.broker.queue,
        "MAX_QUEUE_SIZE": globals.broker.MAX_QUEUE_SIZE,
        "DROPPED_MESSAGES_COUNT": globals.broker.DROPPED_MESSAGES_COUNT,
        "DROPPED_MESSAGES_BY_FULL_QUEUE": globals.broker.DROPPED_MESSAGES_BY_FULL_QUEUE,
        "ROUND_DROPPED_MESSAGES_COUNT": globals.broker.ROUND_DROPPED_MESSAGES_COUNT,
        "ROUND_DROPPED_MESSAGES_BY_FULL_QUEUE": globals.broker.ROUND_DROPPED_MESSAGES_BY_FULL_QUEUE,
    }


@app.get("/plant")
def read_plant():
    return {
        "state": globals.plant.state,
        "sensors": globals.plant.get_sensors(),
    }


@app.get("/sensors")
def read_sensors():
    return [{
        "sensor_id": sensor.sensor_id,
        "sensor_type": (sensor.sensor_type.name, sensor.sensor_type.value),
        "role": (sensor.role.name, sensor.role.value),
        "operating_range": sensor.operating_range,
        "mean_value": sensor.mean_value,
        "sampling_interval": sensor.sampling_interval,
        "local_state": sensor.local_state,
        "standard_deviation": sensor.standard_deviation,
        "transition_probabilities": sensor.transition_probabilities,
        "last_update_by_prob": sensor.get_last_update_by_prob(),
        "last_upkeep": sensor.get_last_upkeep(),
        "last_thousand_values": sensor.get_last_thousand_values(),
        "last_value": sensor.get_last_value(),
        "last_message": sensor.get_last_message(),
        "old_state": sensor.get_old_state(),
    } for sensor in globals.plant.sensors.values()]
