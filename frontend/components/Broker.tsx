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
            <TableHead>Epsilon</TableHead>
            <TableHead>Buffer Size</TableHead>
            <TableHead>DO_NOTHING msgs</TableHead>
            <TableHead>UPKEEP msgs</TableHead>
            <TableHead>NECESSARY UPKEEP msgs</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow>
            <TableCell>{data.broker.epsilon}</TableCell>
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
          </TableRow>

          <TableRow>
            <TableCell colSpan={2}></TableCell>
            <TableCell colSpan={3}>
              <DualNestedBar
                grayValue={data.broker.do_nothing_count}
                yellowValue={data.broker.upkeep_count}
                innerYellowValue={data.broker.necessary_upkeep_count}
              />
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>
  );
}
