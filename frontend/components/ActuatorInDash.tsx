import {useSimulationContext} from "@/contexts/SimulationContext";
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from "./ui/table";
import {getAvailabilityColor} from "@/lib/utils";
import {ProgressBar} from "./ProgressBar";

export default function ActuatorInDash() {
  const {data} = useSimulationContext();

  if (!data) return;

  return (
    <div>
      <h3>Actuator</h3>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>available_teams</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow>
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
          </TableRow>

          <TableRow>
            <TableCell>
              <ProgressBar value={data.actuator.available_teams} max={data.actuator.MAX_ACTUATOR_TEAMS} />
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>
  );
}
