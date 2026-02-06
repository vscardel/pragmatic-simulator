import {useSimulationContext} from "@/contexts/SimulationContext";
import {ButtonGroup} from "./ui/button-group";
import {Button} from "./ui/button";
import {Badge} from "./ui/badge";

export default function SimulationState() {
  const {data, isFetching} = useSimulationContext();

  if (!data) return;

  return (
    <ButtonGroup>
      <Badge
        variant="secondary"
        className={`${data.simulator.is_running && "bg-green-500 text-white"} text-sm`}
      >
        {data.simulator.is_running ? "" : "Not"} Running
      </Badge>
      <Badge variant="secondary" className={`${isFetching && "bg-green-500 text-white"} text-sm`}>
        {isFetching ? "" : "Not"} Fetching
      </Badge>
      {data.simulator.should_stop && (
        <Badge
          variant="secondary"
          className={`${data.simulator.should_stop && "bg-red-500 text-white"} text-sm`}
        >
          Should Stop
        </Badge>
      )}
    </ButtonGroup>
  );
}
