import {GlobalStateEnum, useSimulationContext} from "@/contexts/SimulationContext";
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from "./ui/table";
import {StateBar} from "./StateBar";
import {FourStateBar} from "./FourStateBar";
import {formatMilliseconds} from "@/lib/utils";
import PlantStateCell from "./PlantStateCell";
import PlantMeasuredStateCell from "./PlantMeasuredStateCell";

export default function Plant() {
  const {data} = useSimulationContext();

  if (!data) return;

  return (
    <div>
      <h3>Plant</h3>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>State</TableHead>
            <TableHead>Measured State</TableHead>
            <TableHead>
              Time in <span className="bg-green-500 text-white">NORMAL</span>
            </TableHead>
            <TableHead>
              Time in <span className="bg-yellow-400">DEGRADED</span>
            </TableHead>
            <TableHead>
              Time in <span className="bg-red-500 text-white">CRITICAL</span>
            </TableHead>
            <TableHead>
              Time in <span className="bg-black text-white">FAILURE</span>
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow>
            <PlantStateCell />
            <PlantMeasuredStateCell />
            <TableCell>
              {data.simulator.passed_time_in_NORMAL} (
              {formatMilliseconds(data.simulator.passed_time_in_NORMAL)}) (
              {data.time && ((data.simulator.passed_time_in_NORMAL / data.time) * 100).toFixed(2)}%)
            </TableCell>
            <TableCell>
              {data.simulator.passed_time_in_DEGRADED} (
              {formatMilliseconds(data.simulator.passed_time_in_DEGRADED)}) (
              {data.time && ((data.simulator.passed_time_in_DEGRADED / data.time) * 100).toFixed(2)}%)
            </TableCell>
            <TableCell>
              {data.simulator.passed_time_in_CRITICAL} (
              {formatMilliseconds(data.simulator.passed_time_in_CRITICAL)}) (
              {data.time && ((data.simulator.passed_time_in_CRITICAL / data.time) * 100).toFixed(2)}%)
            </TableCell>
            <TableCell>
              {data.simulator.passed_time_in_FAILURE} (
              {formatMilliseconds(data.simulator.passed_time_in_FAILURE)}) (
              {data.time && ((data.simulator.passed_time_in_FAILURE / data.time) * 100).toFixed(2)}%)
            </TableCell>
          </TableRow>

          <TableRow>
            <TableCell colSpan={2}>
              <StateBar value={data.plant.measured_state} />
            </TableCell>
            <TableCell colSpan={4}>
              <FourStateBar
                green={data.simulator.passed_time_in_NORMAL}
                yellow={data.simulator.passed_time_in_DEGRADED}
                red={data.simulator.passed_time_in_CRITICAL}
                black={data.simulator.passed_time_in_FAILURE}
                greenLabel="NORMAL"
                yellowLabel="DEGRADED"
                redLabel="CRITICAL"
                blackLabel="FAILURE"
              />
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>
  );
}
