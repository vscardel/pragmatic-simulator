import {useSimulationContext} from "@/contexts/SimulationContext";
import {Table, TableBody, TableHead, TableHeader, TableRow} from "./ui/table";
import Sensor from "./Sensor";

export default function Sensors() {
  const {data} = useSimulationContext();

  if (!data) return;

  return (
    <div>
      <h3>Sensors</h3>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>id</TableHead>
            <TableHead>label</TableHead>
            <TableHead>role</TableHead>
            <TableHead>old_state</TableHead>
            <TableHead>state</TableHead>
            <TableHead>sensor_data</TableHead>
            <TableHead>under_maintenance</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.sensors.map((sensor) => (
            <Sensor sensor={sensor} key={sensor.sensor_id} />
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
