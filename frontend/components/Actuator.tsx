import {useSimulationContext} from "@/contexts/SimulationContext";
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from "./ui/table";
import {MaintenanceBar} from "./MaintenanceBar";
import {ProgressBar} from "./ProgressBar";
import {DualStatusBar} from "./DualStatusBar";
import {formatMilliseconds, getAvailabilityColor} from "@/lib/utils";

export default function Actuator() {
  const {data} = useSimulationContext();

  if (!data) return;

  return (
    <div>
      <h3>Actuator</h3>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>total_maintenance_time</TableHead>
            <TableHead>degraded_maintenances</TableHead>
            <TableHead>critical_maintenances</TableHead>
            <TableHead>unnecessary_maintenances</TableHead>
            <TableHead>available_teams</TableHead>
            <TableHead>time_with_available_teams</TableHead>
            <TableHead>time_without_available_teams</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow>
            <TableCell>
              {data.actuator.total_maintenance_time} (
              {formatMilliseconds(data.actuator.total_maintenance_time)}) (
              {data.time && ((data.actuator.total_maintenance_time / data.time) * 100).toFixed(2)}%)
            </TableCell>
            <TableCell className="bg-yellow-400">
              {data.degraded_maintenances}/{data.actuator.total_maintenances} (
              {data.actuator.total_maintenances &&
                ((data.degraded_maintenances / data.actuator.total_maintenances) * 100).toFixed(2)}
              %)
            </TableCell>
            <TableCell className="bg-red-500 text-white">
              {data.critical_maintenances}/{data.actuator.total_maintenances} (
              {data.actuator.total_maintenances &&
                ((data.critical_maintenances / data.actuator.total_maintenances) * 100).toFixed(2)}
              %)
            </TableCell>
            <TableCell className="bg-gray-300">
              {data.actuator.unnecessary_maintenances}/{data.actuator.total_maintenances} (
              {data.actuator.total_maintenances &&
                ((data.actuator.unnecessary_maintenances / data.actuator.total_maintenances) * 100).toFixed(
                  2,
                )}
              %)
            </TableCell>
            <TableCell
              className="text-center text-white"
              style={{
                backgroundColor: getAvailabilityColor(
                  data.actuator.available_teams,
                  data.actuator.MAX_ACTUATOR_TEAMS,
                ),
              }}
            >
              {data.actuator.available_teams}/{data.actuator.MAX_ACTUATOR_TEAMS}
            </TableCell>
            <TableCell>
              {data.simulator.time_with_available_teams} (
              {formatMilliseconds(data.simulator.time_with_available_teams)}) (
              {data.time && ((data.simulator.time_with_available_teams / data.time) * 100).toFixed(2)}% )
            </TableCell>
            <TableCell>
              {data.simulator.time_without_available_teams} (
              {formatMilliseconds(data.simulator.time_without_available_teams)}) (
              {data.time && ((data.simulator.time_without_available_teams / data.time) * 100).toFixed(2)}% )
            </TableCell>
          </TableRow>

          <TableRow>
            <TableCell colSpan={4}>
              <MaintenanceBar
                critical_maintenances={data.critical_maintenances}
                degraded_maintenances={data.degraded_maintenances}
                unnecessary_maintenances={data.actuator.unnecessary_maintenances}
              />
            </TableCell>
            <TableCell>
              <ProgressBar value={data.actuator.available_teams} max={data.actuator.MAX_ACTUATOR_TEAMS} />
            </TableCell>
            <TableCell colSpan={2}>
              <DualStatusBar
                green={data.simulator.time_with_available_teams}
                red={data.simulator.time_without_available_teams}
              />
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>
  );
}
