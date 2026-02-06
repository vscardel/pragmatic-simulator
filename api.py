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
        "simulator": read_simulator(),
        "mean_reaction_time_degraded": globals.mean_reaction_time_degraded,
        "mean_reaction_time_critical": globals.mean_reaction_time_critical,
        "degraded_maintenances": globals.degraded_maintenances,
        "critical_maintenances": globals.critical_maintenances,
        "logs": globals.logs
    }
    
@app.delete("/remove-logs-until/{time}")
def remove_logs_until(time: int):
    globals.logs = [log for log in globals.logs if log[0] > time]

@app.get("/time")
def read_time():
    return {"time": globals.time}


@app.get("/actuator")
def read_actuator():
    return {
        "last_messages_impact": globals.actuator.last_messages_impact,
        "sensors_to_analyze": globals.actuator.sensors_to_analyze,
        "sensors_sum_impact_ordered": globals.actuator.sensors_sum_impact_ordered,
        "available_teams": globals.actuator.available_teams,
        "MAX_ACTUATOR_TEAMS": globals.MAX_ACTUATOR_TEAMS,
        "sensors_sum_impact": globals.actuator.sensors_sum_impact,
        "unnecessary_maintenances": globals.actuator.unnecessary_maintenances,
        "total_maintenances": globals.actuator.total_maintenances,
        "correct_inferred_state": globals.actuator.correct_inferred_state,
        "correct_inferred_role": globals.actuator.correct_inferred_role,
        "total_maintenance_time": globals.total_maintenance_time
    }

@app.get("/simulator")
def read_simulator():
    return {
        "should_stop": globals.should_stop,
        "is_running": globals.is_running,
        "timers": len(globals.timers),
        "passed_time_in_NORMAL": sim.passed_time_in_NORMAL,
        "passed_time_in_DEGRADED": sim.passed_time_in_DEGRADED,
        "passed_time_in_CRITICAL": sim.passed_time_in_CRITICAL,
        "passed_time_in_FAILURE": sim.passed_time_in_FAILURE,
        "time_with_available_teams": sim.time_with_available_teams,
        "time_without_available_teams": sim.time_without_available_teams,
    }

@app.get("/broker")
def read_broker():
    return {
        "buffer": globals.broker.buffer,
        "do_nothing_count": globals.broker.do_nothing_count,
        "upkeep_count": globals.broker.upkeep_count,
        "necessary_upkeep_count": globals.broker.necessary_upkeep_count
    }


@app.get("/plant")
def read_plant():
    return {
        "state": globals.plant.state,
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
        "last_update_by_prob": sensor.last_update_by_prob,
        "last_upkeep": sensor.last_upkeep,
        "last_thousand_values": sensor.last_thousand_values,
        "last_value": sensor.last_value,
        "last_message": sensor.last_message.__dict__ if sensor.last_message else sensor.last_message,
        "old_state": sensor.old_state,
        "under_maintenance": sensor.under_maintenance if type(sensor.under_maintenance) == bool else sensor.under_maintenance.name
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
