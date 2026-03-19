import {useSimulationContext} from "@/contexts/SimulationContext";
import {ButtonGroup} from "./ui/button-group";
import {Button} from "./ui/button";
import {Input} from "./ui/input";
import {useState} from "react";

export default function ControlBar() {
  const {
    startSimulation,
    stopSimulation,
    resetSimulation,
    startTraining,
    stopTraining,
    saveQTable,
    updateSensorsStates,
    loadQTable,
  } = useSimulationContext();

  const [qTableFilename, setQTableFilename] = useState<string>("qtable");

  return (
    <>
      <ButtonGroup>
        <Button onClick={() => startSimulation(3600)}>Start 1 h</Button>
        <Button onClick={() => startSimulation(3600 * 24)}>Start 1 day</Button>
        <Button onClick={() => startSimulation(3600 * 24 * 30)}>Start 1 month</Button>
        <Button onClick={() => startSimulation(3600 * 24 * 30 * 12)}>Start 1 year</Button>
        <Button onClick={() => startSimulation(Number.MAX_SAFE_INTEGER)}>Start indefinitely</Button>
        <Button onClick={stopSimulation}>Stop</Button>
        <Button disabled />
        <Button onClick={() => startTraining(3600 * 24)}>Train 1 day</Button>
        <Button onClick={() => startTraining(3600 * 24 * 30)}>Train 1 month</Button>
        <Button onClick={() => startTraining(Number.MAX_SAFE_INTEGER)}>Train indefinitely</Button>
        <Button onClick={() => stopTraining()}>Stop training</Button>
        <Button disabled />
        <Button onClick={() => updateSensorsStates()}>Update sensors states</Button>
        <Button disabled />
        <Button onClick={resetSimulation}>Reset</Button>
      </ButtonGroup>

      <ButtonGroup>
        <Input
          value={qTableFilename}
          onChange={(e) => setQTableFilename(e.target.value)}
          placeholder="Nome do arquivo da Q-table"
        />
        <Button onClick={() => saveQTable(qTableFilename)}>Salvar Q-table</Button>
        <Button onClick={() => loadQTable(qTableFilename)}>Carregar Q-table</Button>
      </ButtonGroup>
    </>
  );
}
