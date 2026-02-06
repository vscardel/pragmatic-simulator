import {useSimulationContext} from "@/contexts/SimulationContext";
import {ButtonGroup} from "./ui/button-group";
import {Button} from "./ui/button";

export default function ControlBar() {
  const {startSimulation, stopSimulation, resetSimulation} = useSimulationContext();

  return (
    <ButtonGroup>
      <Button onClick={() => startSimulation()}>Start</Button>
      <Button onClick={() => startSimulation(1)}>Start 1 s</Button>
      <Button onClick={() => startSimulation(60)}>Start 1 min</Button>
      <Button onClick={() => startSimulation(3600)}>Start 1 h</Button>
      <Button onClick={() => startSimulation(3600 * 24)}>Start 1 day</Button>
      <Button onClick={() => startSimulation(3600 * 24 * 30)}>Start 1 month</Button>
      <Button onClick={resetSimulation}>Reset</Button>
      <Button onClick={stopSimulation}>Stop</Button>
    </ButtonGroup>
  );
}
