"use client";

import {formatMilliseconds} from "@/lib/utils";
import {createContext, useContext, useState, ReactNode, use, useEffect} from "react";
import {toast} from "sonner";

export enum GlobalStateEnum {
  NORMAL = 0,
  DEGRADED = 1,
  CRITICAL = 2,
  FAILURE = 3,
}

enum SensorRoleEnum {
  CRITICAL = 0,
  NORMAL = 1,
  UNINPORTANT = 2,
}

enum SensorTypeEnum {
  TEMPERATURE = 0,
}

enum LogTypeEnum {
  UPDATE_BY_PROB = 0,
  UPKEEP = 1,
}

export type OperatingRange = {
  normal: [number, number];
  degraded: [number, number];
  critical: [number, number];
};

type SensorMessage = {
  sensor_id: number;
  sensor_type: number;
  sensor_value: number;
  timestamp: number;
};

export type SensorData = {
  sensor_id: number;
  sensor_label: string;
  sensor_type: [keyof typeof SensorTypeEnum, SensorTypeEnum];
  role: [keyof typeof SensorRoleEnum, SensorRoleEnum];
  operating_range: OperatingRange;
  mean_value: number;
  sampling_interval: number;
  local_state: GlobalStateEnum;
  standard_deviation: number;
  transition_probabilities: Record<GlobalStateEnum, Record<GlobalStateEnum, number>>;
  last_update_by_prob: [number, GlobalStateEnum, GlobalStateEnum] | null;
  last_upkeep: [number, GlobalStateEnum, GlobalStateEnum] | null;
  last_thousand_values: number[];
  last_value: number | null;
  last_message: SensorMessage | null;
  old_state: GlobalStateEnum | null;
  under_maintenance: boolean | keyof typeof GlobalStateEnum;
};

type ActuatorData = {
  last_messages_impact: Record<string, number>;
  sensors_to_analyze: [number, number][];
  sensors_sum_impact_ordered: [number, number][];
  available_teams: number;
  MAX_ACTUATOR_TEAMS: number;
  sensors_sum_impact: Record<string, number>;
  unnecessary_maintenances: number;
  total_maintenances: number;
  correct_inferred_state: number;
  correct_inferred_role: number;
  total_maintenance_time: number;
};

enum BrokerInstruction {
  DO_NOTHING = 0,
  UPKEEP = 1,
}

type BrokerMessage = {
  sensor_id: number;
  inferred_role: SensorRoleEnum;
  inferred_state: GlobalStateEnum;
  sensor_message: SensorMessage;
  instruction: BrokerInstruction;
};

type BrokerData = {
  buffer: BrokerMessage[];
  do_nothing_count: number;
  upkeep_count: number;
  necessary_upkeep_count: number;
};

type ProductionPlantData = {
  state: GlobalStateEnum;
  measured_state: number;
};

type SimulatorData = {
  should_stop: boolean;
  is_running: boolean;
  timers: number;
  passed_time_in_NORMAL: number;
  passed_time_in_DEGRADED: number;
  passed_time_in_CRITICAL: number;
  passed_time_in_FAILURE: number;
  time_with_available_teams: number;
  time_without_available_teams: number;
};

type AllData = {
  time: number;
  mean_reaction_time_degraded: number | null;
  mean_reaction_time_critical: number | null;
  degraded_maintenances: number;
  critical_maintenances: number;
  sensors: SensorData[];
  actuator: ActuatorData;
  broker: BrokerData;
  plant: ProductionPlantData;
  simulator: SimulatorData;
  logs: [number, LogTypeEnum, string][];
};

type SimulationContextType = {
  startSimulation: (steps?: number) => void;
  stopSimulation: () => void;
  resetSimulation: () => void;
  data: AllData | undefined;
  isFetching: boolean;
};

const FETCH_INTERVAL = 500;
const REQUEST_LIMIT = 1;

const SimulationContext = createContext<SimulationContextType | null>(null);

let fetcherRequests = 0;
let showedLogs = 0;

let fetchingInterval: NodeJS.Timeout | null = null;

export function SimulationProvider({children}: {children: ReactNode}) {
  const [data, setData] = useState<AllData>();
  const [isFetching, setIsFetching] = useState<boolean>(false);

  function startSimulation(steps?: number) {
    fetch("http://localhost:8000/start" + (steps ? `?steps=${steps}` : ""), {method: "POST"});
    setTimeout(() => startFetching(), FETCH_INTERVAL * 2);
  }

  function stopSimulation() {
    fetch("http://localhost:8000/stop", {method: "POST"});
    setTimeout(() => stopFetching(), FETCH_INTERVAL * 2);
  }

  async function resetSimulation() {
    await fetch("http://localhost:8000/reset", {method: "POST"});
    toast.dismiss();
    showedLogs = 0;
  }

  function startFetching() {
    if (fetchingInterval) {
      clearInterval(fetchingInterval);
    }
    fetchingInterval = setInterval(() => {
      if (fetcherRequests < REQUEST_LIMIT) {
        fetch(`http://localhost:8000/all`, {method: "GET"})
          .then((res) => res.json())
          .then((data) => {
            setData(data);
            showLogs(data.logs);
            fetcherRequests--;
          });
        fetcherRequests++;
      }
    }, FETCH_INTERVAL);
    setIsFetching(true);
  }

  function showLogs(logs: [number, LogTypeEnum, string][]) {
    for (let i = Math.max(logs.length - 30, showedLogs); i < logs.length; i++) {
      const log = logs[i];
      toast(`${log[0]} (${formatMilliseconds(log[0])})`, {
        description: log[2],
        dismissible: false,
        style: {
          border: "2px solid",
          borderLeft: "8px solid",
          borderColor: log[1] === LogTypeEnum.UPKEEP ? "var(--color-green-600)" : "var(--color-red-600)",
        },
      });
    }
    showedLogs = logs.length;
  }

  function stopFetching() {
    if (fetchingInterval) {
      clearInterval(fetchingInterval);
    }
    setIsFetching(false);
  }

  function removeLogsUntil(time: number) {
    fetch(`http://localhost:8000/remove-logs-until/${time}`, {method: "DELETE"});
  }

  useEffect(() => startFetching(), []);

  return (
    <SimulationContext.Provider value={{data, isFetching, startSimulation, stopSimulation, resetSimulation}}>
      {children}
    </SimulationContext.Provider>
  );
}

export function useSimulationContext() {
  const context = useContext(SimulationContext);

  if (!context) {
    throw new Error("useSimulationContext deve ser usado dentro de SimulationProvider");
  }

  return context;
}
