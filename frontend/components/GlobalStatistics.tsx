import {useSimulationContext} from "@/contexts/SimulationContext";
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from "./ui/table";
import {formatMilliseconds} from "@/lib/utils";

export default function GlobalStatistics() {
  const {data} = useSimulationContext();

  if (!data) return;

  return (
    <div>
      <h3>Global Statistics</h3>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>time</TableHead>
            <TableHead>mean_reaction_time_degraded</TableHead>
            <TableHead>mean_reaction_time_critical</TableHead>
            <TableHead>Number of registered timers</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow>
            <TableCell>
              {data.time} ({formatMilliseconds(data.time, true)})
            </TableCell>
            <TableCell itemType="string">
              {data.mean_reaction_time_degraded} (
              {data.mean_reaction_time_degraded && formatMilliseconds(data.mean_reaction_time_degraded)})
            </TableCell>
            <TableCell>
              {data.mean_reaction_time_critical} (
              {data.mean_reaction_time_critical && formatMilliseconds(data.mean_reaction_time_critical)})
            </TableCell>
            <TableCell>{data.simulator.timers}</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>
  );
}
