import {GlobalStateEnum, SensorData} from "@/contexts/SimulationContext";
import {TableCell, TableRow} from "./ui/table";
import clsx from "clsx";
import {OperatingRangeCell} from "./OperatingRangeCell";

export default function Sensor({sensor}: {sensor: SensorData}) {
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
      <TableCell
        className={clsx(
          "relative text-center",
          sensor.old_state === 0 && "bg-green-500 text-white",
          sensor.old_state === 1 && "bg-yellow-400",
          sensor.old_state === 2 && "bg-red-500 text-white",
          sensor.old_state === 3 && "bg-black text-white",
        )}
      >
        {sensor.old_state !== null ? (
          <>
            {GlobalStateEnum[sensor.old_state]}
            <span className="absolute translate-x-1/2 top-1/2 right-0 -translate-y-1/2 ">→</span>
          </>
        ) : (
          "-"
        )}
      </TableCell>
      <TableCell
        className={clsx(
          "text-center",
          sensor.local_state === 0 && "bg-green-500 text-white",
          sensor.local_state === 1 && "bg-yellow-400",
          sensor.local_state === 2 && "bg-red-500 text-white",
          sensor.local_state === 3 && "bg-black text-white",
        )}
      >
        {GlobalStateEnum[sensor.local_state]}
      </TableCell>
      <OperatingRangeCell
        last_thousand_values={sensor.last_thousand_values}
        last_value={sensor.last_value || 0}
        mean_value={sensor.mean_value}
        range={sensor.operating_range}
        standard_deviation={sensor.standard_deviation}
      />
      <TableCell
        className={clsx(
          sensor.under_maintenance === "NORMAL" && "bg-gray-300",
          sensor.under_maintenance === "DEGRADED" && "bg-yellow-400",
          sensor.under_maintenance === "CRITICAL" && "bg-red-500 text-white",
        )}
      >{`${sensor.under_maintenance}`}</TableCell>
    </TableRow>
  );
}
