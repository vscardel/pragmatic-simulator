"use client";

import ActuatorInDash from "@/components/ActuatorInDash";
import PlantInDash from "@/components/PlantInDash";
import SensorsInDash from "@/components/SensorsInDash";
import {Button} from "@/components/ui/button";
import {ButtonGroup} from "@/components/ui/button-group";
import {useSimulationContext} from "@/contexts/SimulationContext";
import {formatMilliseconds} from "@/lib/utils";

export default function Dash() {
  const {data, stopSimulation, resetSimulation, updateSensorsStates, startSimulationForHumans} =
    useSimulationContext();

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex min-h-screen w-full flex-col items-center gap-4 py-8 px-8 bg-white dark:bg-black sm:items-start">
        <div className="flex items-center gap-4">
          <ButtonGroup>
            <Button onClick={() => startSimulationForHumans(Number.MAX_SAFE_INTEGER)}>
              Start indefinitely
            </Button>
            <Button onClick={stopSimulation}>Stop</Button>
            <Button disabled />
            <Button onClick={() => updateSensorsStates()}>Update sensors states</Button>
            <Button disabled />
            <Button onClick={resetSimulation}>Reset</Button>
          </ButtonGroup>
          Time: {data?.time || 0} ({formatMilliseconds(data?.time || 0)})
          <PlantInDash />
          <ActuatorInDash />
        </div>
        <SensorsInDash />
      </main>
    </div>
  );
}
