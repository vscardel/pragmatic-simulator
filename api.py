from fastapi import FastAPI
from typing import Union
from fastapi.middleware.cors import CORSMiddleware
import globals
from simulator import Simulator
import threading
import config

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

sim = Simulator.get_instance()

@app.get("/all")
def read_all():
    return {
        "time": globals.time,
        "actuator": read_actuator(),
        "broker": read_broker(),
        "plant": read_plant(),
        "sensors": read_sensors(),
    }

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
        "last_load_term": globals.actuator.get_last_load_term(), # Deprecated
        "last_sensors_to_analyze": globals.actuator.get_last_sensors_to_analyze(),
        "last_sensors_sum_impact_ordered": globals.actuator.get_last_sensors_sum_impact_ordered(),
        "last_pondered_state": globals.actuator.get_pondered_state(),
        "available_teams": globals.actuator.get_available_teams(),
        "MAX_ACTUATOR_WORKLOAD": config.MAX_ACTUATOR_WORKLOAD
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

@app.post("/start")
def start(steps: int = globals.DEFAULT_TIME_STEPS):
    threading.Thread(target=sim.run,args=(steps,), daemon=True).start()


@app.post("/reset")
def reset():
    sim.stop()
    sim.reset()
    

@app.post("/stop")
def stop():
    sim.stop()
