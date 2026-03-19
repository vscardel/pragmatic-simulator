import {useSimulationContext} from "@/contexts/SimulationContext";
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from "./ui/table";
import PlantStateCell from "./PlantStateCell";
import PlantMeasuredStateCell from "./PlantMeasuredStateCell";
import {StateBar} from "./StateBar";

export default function PlantInDash() {
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
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow>
            <PlantStateCell />
            <PlantMeasuredStateCell />
          </TableRow>

          <TableRow>
            <TableCell colSpan={2}>
              <StateBar value={data.plant.measured_state} />
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>
  );
}
