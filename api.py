from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import globals
from simulator import Simulator
import threading

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
        "last_messages_impact": globals.actuator.get_last_messages_impact(),
        "last_sensors_to_analyze": globals.actuator.get_last_sensors_to_analyze(),
        "last_sensors_sum_impact_ordered": globals.actuator.get_last_sensors_sum_impact_ordered(),
        "available_teams": globals.actuator.get_available_teams(),
        "MAX_ACTUATOR_TEAMS": globals.MAX_ACTUATOR_TEAMS
    }


@app.get("/broker")
def read_broker():
    return {
        "buffer": globals.broker.buffer,
    }


@app.get("/plant")
def read_plant():
    return {
        "state": globals.plant.state,
        "sensors": globals.plant.get_sensors(),
        "measured_state": globals.plant.measured_state
    }


@app.get("/sensors")
def read_sensors():
    return [{
        "sensor_id": sensor.sensor_id,
        "sensor_label": sensor.sensor_label,
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
        "under_maintenance": sensor.under_maintenance 
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
