import {GlobalStateEnum, useSimulationContext} from "@/contexts/SimulationContext";
import {TableCell} from "./ui/table";

export default function PlantStateCell() {
  const {data} = useSimulationContext();
  if (!data) return;
  return (
    <TableCell
      className={`text-white ${
        data.plant.state === GlobalStateEnum.NORMAL
          ? "bg-green-500"
          : data.plant.state === GlobalStateEnum.DEGRADED
            ? "bg-yellow-400 text-black"
            : data.plant.state === GlobalStateEnum.CRITICAL
              ? "bg-red-500"
              : "bg-black"
      }`}
    >
      {GlobalStateEnum[data.plant.state]}
    </TableCell>
  );
}
