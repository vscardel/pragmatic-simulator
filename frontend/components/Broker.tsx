import {useSimulationContext} from "@/contexts/SimulationContext";
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from "./ui/table";
import {DualNestedBar} from "./DualNestedBar";
import {DualStatusBar} from "./DualStatusBar";

export default function Broker() {
  const {data} = useSimulationContext();

  if (!data) return;

  const totalMsgs = data.broker.do_nothing_count + data.broker.upkeep_count;

  return (
    <div>
      <h3>Broker</h3>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Buffer Size</TableHead>
            <TableHead>DO_NOTHING msgs</TableHead>
            <TableHead>UPKEEP msgs</TableHead>
            <TableHead>NECESSARY UPKEEP msgs</TableHead>
            <TableHead>correct_inferred_role</TableHead>
            <TableHead>correct_inferred_state</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow>
            <TableCell>{data.broker.buffer.length}</TableCell>
            <TableCell className="bg-gray-300">
              {data.broker.do_nothing_count}/{totalMsgs} (
              {totalMsgs && ((data.broker.do_nothing_count / totalMsgs) * 100).toFixed(2)}%)
            </TableCell>
            <TableCell className="bg-yellow-400">
              {data.broker.upkeep_count}/{totalMsgs} (
              {totalMsgs && ((data.broker.upkeep_count / totalMsgs) * 100).toFixed(2)}%)
            </TableCell>
            <TableCell className="text-white bg-yellow-600">
              {data.broker.necessary_upkeep_count}/{data.broker.upkeep_count} (
              {data.broker.upkeep_count &&
                ((data.broker.necessary_upkeep_count / data.broker.upkeep_count) * 100).toFixed(2)}
              % UK) ({totalMsgs && ((data.broker.necessary_upkeep_count / totalMsgs) * 100).toFixed(2)}% Tot)
            </TableCell>
            <TableCell>
              {data.actuator.correct_inferred_role}/{totalMsgs} (
              {totalMsgs && ((data.actuator.correct_inferred_role / totalMsgs) * 100).toFixed(2)}% )
            </TableCell>
            <TableCell>
              {data.actuator.correct_inferred_state}/{totalMsgs} (
              {totalMsgs && ((data.actuator.correct_inferred_state / totalMsgs) * 100).toFixed(2)}% )
            </TableCell>
          </TableRow>

          <TableRow>
            <TableCell></TableCell>
            <TableCell colSpan={3}>
              <DualNestedBar
                grayValue={data.broker.do_nothing_count}
                yellowValue={data.broker.upkeep_count}
                innerYellowValue={data.broker.necessary_upkeep_count}
              />
            </TableCell>
            <TableCell>
              <DualStatusBar
                green={data.actuator.correct_inferred_role}
                red={totalMsgs - data.actuator.correct_inferred_role}
              />
            </TableCell>
            <TableCell>
              <DualStatusBar
                green={data.actuator.correct_inferred_state}
                red={totalMsgs - data.actuator.correct_inferred_state}
              />
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>
  );
}
