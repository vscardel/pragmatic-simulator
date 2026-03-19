import {GlobalStateEnum, SensorData, useSimulationContext} from "@/contexts/SimulationContext";
import {TableCell, TableRow} from "./ui/table";
import clsx from "clsx";
import {OperatingRangeCell} from "./OperatingRangeCell";
import TemperatureChart from "./TemperatureChart";
import {Button} from "./ui/button";

export default function SensorInDash({sensor}: {sensor: SensorData}) {
  const {maintainSensor} = useSimulationContext();
  return (
    <TableRow>
      <TableCell>{sensor.sensor_id}</TableCell>
      <TableCell>{sensor.sampling_interval}</TableCell>
      <TableCell>{sensor.sensor_label}</TableCell>
      <TableCell
        className={clsx(
          sensor.role[1] === 2 && "bg-gray-300",
          sensor.role[1] === 1 && "bg-blue-500 text-white",
          sensor.role[1] === 0 && "bg-orange-500 text-white",
        )}
      >
        {sensor.role[0]}
      </TableCell>

      <TemperatureChart data={sensor.last_thousand_values} sampling_interval={sensor.sampling_interval} />
      <TableCell>
        <Button onClick={() => maintainSensor(sensor.sensor_id)}>Manutenir</Button>
      </TableCell>
    </TableRow>
  );
}
