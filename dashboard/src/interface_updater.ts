enum SensorStateEnum {
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
  HUMIDITY = 1,
  PRESSURE = 2,
  LIGHT = 3,
  MOISTURE = 4,
  AIR_QUALITY = 5,
}

type OperatingRange = {
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

type SensorData = {
  sensor_id: number;
  sensor_type: [keyof typeof SensorTypeEnum, SensorTypeEnum];
  role: [keyof typeof SensorRoleEnum, SensorRoleEnum];
  operating_range: OperatingRange;
  mean_value: number;
  sampling_interval: number;
  local_state: SensorStateEnum;
  standard_deviation: number;
  transition_probabilities: Record<SensorStateEnum, Record<SensorStateEnum, number>>;
  last_update_by_prob: [number, SensorStateEnum, SensorStateEnum] | null;
  last_upkeep: [number, SensorStateEnum, SensorStateEnum] | null;
  last_thousand_values: number[];
  last_value: number | null;
  last_message: {
    sensor_id: number;
    sensor_type: number;
    sensor_value: number;
    timestamp: number;
  } | null;
  old_state: SensorStateEnum | null;
};

type ActuatorData = {
  load: number;
  global_state: [number, SensorStateEnum];
  THRESHOLD_LOAD: number;
  last_messages_impact: Record<number, number> | null;
  last_load_term: number | null;
  last_sensors_to_analize: [number, number][] | null;
  last_sensors_sum_impact_ordered: [number, number][] | null;
  last_pondered_state: number | null;
};

type BrokerData = {
  subscribers: number[];
  queue: [number, number, SensorMessage][];
  MAX_QUEUE_SIZE: number;
  DROPPED_MESSAGES_COUNT: number;
  DROPPED_MESSAGES_BY_FULL_QUEUE: number;
  ROUND_DROPPED_MESSAGES_COUNT: number;
  ROUND_DROPPED_MESSAGES_BY_FULL_QUEUE: number;
};

enum PlantStateEnum {
  NORMAL = "NORMAL",
  DEGRADED = "DEGRADED",
  CRITICAL = "CRITICAL",
  FAILURE = "FAILURE",
}

type ProductionPlantData = {
  state: PlantStateEnum;
  sensors: Record<`${number}`, string>;
};

type AllData = {
  time: number;
  sensors: SensorData[];
  actuator: ActuatorData;
  broker: BrokerData;
  production_plant: ProductionPlantData;
};

const timeDiv = document.getElementById("time");
const sensorsTableBody = document.getElementById("sensors_table_body");

function updateInterface(data: AllData) {
  updateTime(data.time);
  updateSensorsTable(data.sensors);
}

function updateTime(time: number) {
  timeDiv!.innerText = "Time: " + time.toString();
}

function updateSensorsTable(data: SensorData[]) {
  sensorsTableBody!.innerHTML = "";

  for (const sensor of data) {
    const row = document.createElement("tr");
    row.innerHTML = `
            <td>${sensor.sensor_id}</td>
            <td>${sensor.role[0]}</td>
            <td>${sensor.old_state === null ? "-" : SensorStateEnum[sensor.old_state]}</td>
            <td>${SensorStateEnum[sensor.local_state]}</td>
            <td>${(sensor.last_thousand_values.reduce((a, b) => a + b, 0) / sensor.last_thousand_values.length).toFixed(2) || "NO VALUES"}</td>
            <td>${sensor.mean_value.toFixed(2)}</td>
            <td>${sensor.standard_deviation.toFixed(2)}</td>
            <td>${
              buildOperatingRangeGraph(sensor.operating_range, sensor.mean_value, sensor.local_state)
                .outerHTML +
              createSensorBarChart({
                values: sensor.last_thousand_values,
                barsCount: 60,
                minValue: sensor.operating_range.critical[0],
                maxValue: sensor.operating_range.critical[1],
                width: 300,
                height: 100,
              }).outerHTML
            }</td>
            <td>${sensor.sampling_interval}</td>
            <td>${sensor.last_value}</td>
            
        `;
    sensorsTableBody!.appendChild(row);
  }
}

function buildOperatingRangeGraph(or: OperatingRange, mean: number, state: SensorStateEnum) {
  const container = document.createElement("div");
  container.style.width = "100%";
  container.style.minWidth = "300px";
  container.style.height = "30px";
  container.style.fontWeight = "bold";
  container.style.position = "relative";

  const criticalRange = or.critical[1] - or.critical[0];
  const criticalDiv = document.createElement("div");
  criticalDiv.style.width = `100%`;
  criticalDiv.style.backgroundColor = "red";
  criticalDiv.style.height = "100%";
  if (state === SensorStateEnum.CRITICAL) {
    criticalDiv.style.border = "3px solid blue";
    criticalDiv.style.top = "-3px";
  }

  const criticalDivText = document.createElement("span");
  criticalDivText.style.width = `100%`;
  criticalDivText.style.display = "flex";
  criticalDivText.style.justifyContent = "space-between";
  criticalDivText.innerHTML = `<span style="transform: translateX(-100%);">${or.critical[0]}</span><span style="transform: translateX(100%);">${or.critical[1]}</span>`;
  criticalDiv.appendChild(criticalDivText);

  const degradedRange = or.degraded[1] - or.degraded[0];
  const degradedDiv = document.createElement("div");
  degradedDiv.style.width = `${(degradedRange / criticalRange) * 100}%`;
  degradedDiv.style.backgroundColor = "#fff000";
  degradedDiv.style.marginLeft = `${((or.degraded[0] - or.critical[0]) / criticalRange) * 100}%`;
  degradedDiv.style.position = "absolute";
  degradedDiv.style.top = "0";
  degradedDiv.style.height = "100%";
  if (state === SensorStateEnum.DEGRADED) {
    degradedDiv.style.border = "3px solid blue";
    degradedDiv.style.top = "-3px";
  }
  const degradedDivText = document.createElement("span");
  degradedDivText.style.width = `100%`;
  degradedDivText.style.display = "flex";
  degradedDivText.style.justifyContent = "space-between";
  degradedDivText.innerHTML = `<span style="transform: translateX(-70%);">${or.degraded[0]}</span><span style="transform: translateX(70%);">${or.degraded[1]}</span>`;
  degradedDiv.appendChild(degradedDivText);

  const normalRange = or.normal[1] - or.normal[0];
  const normalDiv = document.createElement("div");
  normalDiv.style.width = `${(normalRange / degradedRange) * 100}%`;
  normalDiv.style.backgroundColor = "#00b300ff";
  normalDiv.style.marginLeft = `${((or.normal[0] - or.degraded[0]) / degradedRange) * 100}%`;
  normalDiv.style.position = "absolute";
  normalDiv.style.top = "0";
  normalDiv.style.height = "100%";
  if (state === SensorStateEnum.NORMAL) {
    normalDiv.style.border = "3px solid blue";
    normalDiv.style.top = "-3px";
  }
  const normalDivText = document.createElement("span");
  normalDivText.style.width = `100%`;
  normalDivText.style.display = "flex";
  normalDivText.style.justifyContent = "space-between";
  normalDivText.innerHTML = `<span style="transform: translateX(-50%);">${or.normal[0]}</span><span style="transform: translateX(50%);">${or.normal[1]}</span>`;
  normalDiv.appendChild(normalDivText);

  degradedDiv.appendChild(normalDiv);
  criticalDiv.appendChild(degradedDiv);

  const meanBar = document.createElement("div");
  meanBar.style.position = "absolute";
  meanBar.style.height = "100%";
  meanBar.style.backgroundColor = "blue";
  meanBar.style.width = `2px`;
  meanBar.style.top = "0";
  meanBar.style.left = `${((mean - or.critical[0]) / criticalRange) * 100}%`;
  container.appendChild(criticalDiv);
  container.appendChild(meanBar);

  return container;
}

function createSensorBarChart({
  values,
  minValue,
  maxValue,
  barsCount,
  width = 600,
  height = 200,
}: {
  values: number[];
  minValue: number;
  maxValue: number;
  barsCount: number;
  width?: number;
  height?: number;
}) {
  const container = document.createElement("div");

  // Container style
  container.style.display = "flex";
  container.style.alignItems = "flex-end";
  container.style.width = `${width}px`;
  container.style.height = `${height}px`;
  container.style.gap = "1px";
  container.style.boxSizing = "border-box";

  if (!values || values.length === 0) return container;

  const data = values;

  const bins = new Array(barsCount).fill(0);
  const range = maxValue - minValue;
  const binSize = range / barsCount;

  // Distribuição dos valores
  for (const v of data) {
    if (v < minValue || v > maxValue) continue;

    let index = Math.floor((v - minValue) / binSize);
    if (index === barsCount) index = barsCount - 1;
    bins[index]++;
  }

  const maxBin = Math.max(...bins, 1);

  // Criação das barras
  for (const count of bins) {
    const bar = document.createElement("div");

    const h = (count / maxBin) * 100;

    bar.style.flex = "1";
    bar.style.height = `${h}%`;
    bar.style.background = "steelblue";

    container.appendChild(bar);
  }

  return container;
}
