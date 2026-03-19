import {useSimulationContext} from "@/contexts/SimulationContext";
import {Table, TableBody, TableHead, TableHeader, TableRow} from "./ui/table";
import SensorInDash from "./SensorInDash";

export default function SensorsInDash() {
  const {data} = useSimulationContext();

  if (!data) return;

  return (
    <div>
      <h3>Sensors</h3>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>id</TableHead>
            <TableHead>interval</TableHead>
            <TableHead>label</TableHead>
            <TableHead>role</TableHead>
            <TableHead>sensor_data</TableHead>
            <TableHead>maintain</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.sensors.map((sensor) => (
            <SensorInDash sensor={sensor} key={sensor.sensor_id} />
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
