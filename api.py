from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import globals
from simulator import Simulator
import threading
import json
import ast

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
        "is_training": globals.is_training,
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
        "necessary_upkeep_count": globals.broker.necessary_upkeep_count,
        "q_table": export_q_table_to_json(globals.q_table),
        "epsilon": globals.broker.epsilon
    }


def export_q_table_to_json(q_table):
    # 1. Converte o defaultdict para um dicionário normal e as chaves (tuplas) para strings
    # O resultado será algo como: {"(1, 4, 0)": [12.5, -3.2], "(2, 8, 1)": [-1.0, 45.8]}
    q_table_serializavel = {
        str(estado): valores_q
        for estado, valores_q in q_table.items()
    }

    # 2. Converte para a string JSON (que pode ser retornada na sua API/Response)
    payload_json = json.dumps(q_table_serializavel)

    return q_table_serializavel


@app.post("/save_qtable")
def save_qtable(filename: str):
    """
    Salva o estado atual da q_table em um arquivo JSON.

    Parâmetros:
        filename: nome do arquivo (query param). Se não terminar com .json, será adicionado.
    """
    if not filename.endswith(".json"):
        filename = f"{filename}.json"

    q_table_json = export_q_table_to_json(globals.q_table)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(q_table_json, f, ensure_ascii=False, indent=2)

    return {
        "status": "ok",
        "message": "Q-table salva com sucesso.",
        "filename": filename,
        "states": len(q_table_json),
    }


@app.post("/load_qtable")
def load_qtable(filename: str):
    """
    Carrega uma q_table de um arquivo JSON e substitui a q_table atual em globals.

    Parâmetros:
        filename: nome do arquivo (query param). Se não terminar com .json, será adicionado.
    """
    if not filename.endswith(".json"):
        filename = f"{filename}.json"

    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Arquivo '{filename}' não encontrado.")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail=f"Arquivo '{filename}' não é um JSON válido.")

    # Limpa a q_table atual e popula com os dados do arquivo
    globals.q_table.clear()
    for state_str, actions in data.items():
        try:
            state_tuple = ast.literal_eval(state_str)
        except (SyntaxError, ValueError):
            continue
        globals.q_table[state_tuple] = actions

    return {
        "status": "ok",
        "message": "Q-table carregada com sucesso.",
        "filename": filename,
        "states": len(globals.q_table),
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
    
@app.post("/train")
def train(steps: int = globals.DEFAULT_TIME_STEPS):
    threading.Thread(target=sim.train,args=(steps,), daemon=True).start()

@app.post("/reset")
def reset():
    sim.stop()
    sim.reset()
    

@app.post("/update-sensors-states")
def update_sensors_states():
    sim.update_all_sensors_state_by_probabilities()
    

@app.post("/stop")
def stop():
    sim.stop()

@app.post("/stop-training")
def stop_training():
    sim.stop_training()
    
@app.post("/start-for-humans")
def start_for_humans(steps: int = globals.DEFAULT_TIME_STEPS):
    threading.Thread(target=sim.run_for_humans,args=(steps,), daemon=True).start()    

@app.post('/maintainance')
def maintainance(sensor_id: int):
    globals.plant.get_sensor(sensor_id).should_maintain = True