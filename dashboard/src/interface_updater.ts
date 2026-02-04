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
  sensor_label: string;
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
  under_maintenance: boolean | keyof typeof SensorStateEnum;
};

type ActuatorData = {
  last_messages_impact: Record<string, number> | null;
  last_sensors_to_analyze: [number, number][] | null;
  last_sensors_sum_impact_ordered: [number, number][] | null;
  available_teams: number;
  MAX_ACTUATOR_TEAMS: number;
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
  measured_state: number;
};

type AllData = {
  time: number;
  sensors: SensorData[];
  actuator: ActuatorData;
  broker: BrokerData;
  plant: ProductionPlantData;
};

const timeDiv = document.getElementById("time");
const sensorsTableBody = document.getElementById("sensors_table_body");
const actuatorTableBodyRow = document.getElementById("actuator_table_body_row");
const plantTableBodyRow = document.getElementById("plant_table_body_row");

function updateInterface(data: AllData) {
  updateTime(data.time);
  updateSensorsTable(data.sensors, data.actuator);
  updateActuatorTable(data.actuator);
  updatePlantTable(data.plant);
}

function updateTime(time: number) {
  timeDiv!.innerText = "Time: " + time.toString() + ` (${formatMilliseconds(time)})`;
}

function updateSensorsTable(sensors: SensorData[], actuator: ActuatorData) {
  sensorsTableBody!.innerHTML = "";

  for (const sensor of sensors) {
    const row = document.createElement("tr");
    row.innerHTML = `
            <td>${sensor.sensor_id}</td>
            <td>${sensor.sensor_label}</td>
            <td style="background-color: ${sensor.role[1] === SensorRoleEnum.CRITICAL ? "#ff00005a" : sensor.role[1] === SensorRoleEnum.NORMAL ? "#5d5dff5a" : "#a9a9a95a"}">${sensor.role[0]}</td>
            <td style="background-color: ${sensor.old_state === null ? "transparent" : sensor.old_state === SensorStateEnum.NORMAL ? "#00b30037" : sensor.old_state === SensorStateEnum.DEGRADED ? "#fff00037" : sensor.old_state === SensorStateEnum.CRITICAL ? "#ff000037" : "#00000037"}">${sensor.old_state === null ? "-" : SensorStateEnum[sensor.old_state]}</td>
            <td style="background-color: ${sensor.local_state === null ? "transparent" : sensor.local_state === SensorStateEnum.NORMAL ? "#00b3005a" : sensor.local_state === SensorStateEnum.DEGRADED ? "#fff0005a" : sensor.local_state === SensorStateEnum.CRITICAL ? "#ff00005a" : "#0000005a"}">${SensorStateEnum[sensor.local_state]}</td>
            <td>${(sensor.last_thousand_values.reduce((a, b) => a + b, 0) / sensor.last_thousand_values.length).toFixed(2)}</td>
            <td>${sensor.last_value?.toFixed(4)}</td>
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
            <td>${actuator.last_messages_impact?.[sensor.sensor_id.toString()].toFixed(4)}</td>
            <td style="background-color: ${!sensor.under_maintenance ? "#ff00005a" : "#00ff005a"}">${sensor.under_maintenance}</td>
            <td style="background-color: ${actuator.last_sensors_to_analyze?.find((s) => s[0] === sensor.sensor_id) ? "#00ff005a" : "#ff00005a"}">${actuator.last_sensors_to_analyze?.find((s) => s[0] === sensor.sensor_id) ? "Yes" : "No"}</td>
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
  criticalDiv.style.backgroundColor = "#ff0000";
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
  normalDiv.style.backgroundColor = "#00b300";
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

function updateActuatorTable(data: ActuatorData) {
  actuatorTableBodyRow!.innerHTML = `
    <td><div>${data.available_teams}/${data.MAX_ACTUATOR_TEAMS}</div>${buildAvailableTeamsBar(data.available_teams, data.MAX_ACTUATOR_TEAMS).outerHTML}</td>
  `;
}

function updatePlantTable(data: ProductionPlantData) {
  plantTableBodyRow!.innerHTML = `
    <td><div style="width: 300px;">${data.measured_state}</div>${buildMeasuredStateBar(data.measured_state).outerHTML}</td>
  `;
}

function buildLoadTermBar(last_sensors_sum_impact_ordered: [number, number][], loadTerm: number) {
  const container = document.createElement("div");
  container.style.display = "grid";
  container.style.border = "1px solid black";
  container.style.position = "relative";
  container.style.height = "30px";
  container.style.gridTemplateColumns = `repeat(${last_sensors_sum_impact_ordered.length}, 1fr)`;

  for (const [sensor_id] of last_sensors_sum_impact_ordered) {
    const block = document.createElement("div");
    block.style.height = "100%";
    block.style.display = "flex";
    if (sensor_id !== last_sensors_sum_impact_ordered[last_sensors_sum_impact_ordered.length - 1][0])
      block.style.borderRight = "1px solid black";
    block.style.justifyContent = "center";
    block.style.alignItems = "center";
    block.innerText = sensor_id.toString();
    container.appendChild(block);
  }

  const loadTermBar = document.createElement("div");
  loadTermBar.style.position = "absolute";
  loadTermBar.style.height = "100%";
  loadTermBar.style.backgroundColor = "blue";
  loadTermBar.style.width = `2px`;
  loadTermBar.style.left = `${loadTerm * 100}%`;
  container.appendChild(loadTermBar);
  return container;
}

function buildMeasuredStateBar(ponderedState: number) {
  const container = document.createElement("div");
  container.style.display = "grid";
  container.style.position = "relative";
  container.style.height = "30px";
  container.style.gridTemplateColumns = `repeat(4, 1fr)`;

  const normalBlock = document.createElement("div");
  normalBlock.style.height = "100%";
  normalBlock.style.backgroundColor = "#00b300";
  container.appendChild(normalBlock);

  const degradedBlock = document.createElement("div");
  degradedBlock.style.height = "100%";
  degradedBlock.style.backgroundColor = "#fff000";
  container.appendChild(degradedBlock);

  const criticalBlock = document.createElement("div");
  criticalBlock.style.height = "100%";
  criticalBlock.style.backgroundColor = "#ff0000";
  container.appendChild(criticalBlock);

  const failureBlock = document.createElement("div");
  failureBlock.style.height = "100%";
  failureBlock.style.backgroundColor = "#000000";
  container.appendChild(failureBlock);

  const stateBar = document.createElement("div");
  stateBar.style.position = "absolute";
  stateBar.style.height = "100%";
  stateBar.style.backgroundColor = "blue";
  stateBar.style.width = `2px`;
  stateBar.style.left = `${(ponderedState / 3) * 100}%`;
  container.appendChild(stateBar);
  return container;
}

type TimeParts = {
  years: number;
  months: number;
  weeks: number;
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
  milliseconds: number;
};

function formatMilliseconds(ms: number): string {
  if (ms < 0) throw new Error("O valor não pode ser negativo");

  const units = [
    {label: "year", ms: 365 * 24 * 60 * 60 * 1000},
    {label: "minute", ms: 30 * 24 * 60 * 60 * 1000},
    {label: "week", ms: 7 * 24 * 60 * 60 * 1000},
    {label: "day", ms: 24 * 60 * 60 * 1000},
    {label: "hour", ms: 60 * 60 * 1000},
    {label: "minute", ms: 60 * 1000},
    {label: "second", ms: 1000},
    {label: "ms", ms: 1},
  ];

  let remaining = ms;
  const parts: string[] = [];

  for (const unit of units) {
    const value = Math.floor(remaining / unit.ms);
    if (value > 0) {
      parts.push(`${value} ${unit.label}${value > 1 && unit.label !== "ms" ? "s" : ""}`);
      remaining -= value * unit.ms;
    }
  }

  return parts.length ? parts.join(", ") : "0 ms";
}

function buildAvailableTeamsBar(available_teams: number, max_teams: number) {
  const container = document.createElement("div");
  container.style.display = "grid";
  container.style.border = "1px solid black";
  container.style.position = "relative";
  container.style.height = "30px";
  container.style.gridTemplateColumns = `repeat(${max_teams}, 1fr)`;

  for (let i = 0; i < max_teams; i++) {
    const block = document.createElement("div");
    block.style.height = "100%";
    block.style.display = "flex";
    if (i !== max_teams - 1) block.style.borderRight = "1px solid black";
    if (i < available_teams) block.style.backgroundColor = "#00b300";
    container.appendChild(block);
  }

  return container;
}
