"use client";
import Actuator from "@/components/Actuator";
import Broker from "@/components/Broker";
import ControlBar from "@/components/ControlBar";
import GlobalStatistics from "@/components/GlobalStatistics";
import Plant from "@/components/Plant";
import PolicyMapVisualizer from "@/components/PlicyMapVisualizer";
import QTableVisualizer from "@/components/QTable";
import Sensors from "@/components/Sensors";
import SimulationState from "@/components/SimulationState";
import {Toaster} from "sonner";

export default function Home() {
  return (
    <>
      <Toaster position="top-right" visibleToasts={20} duration={5000} />
      <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
        <main className="flex min-h-screen w-full flex-col items-center gap-4 py-8 px-8 bg-white dark:bg-black sm:items-start">
          <div className="flex items-center gap-8">
            <ControlBar />
            <SimulationState />
          </div>
          <GlobalStatistics />
          <Plant />
          <Actuator />
          <Broker />
          {/* <QTableVisualizer /> */}
          <PolicyMapVisualizer />
          <Sensors />
        </main>
      </div>
    </>
  );
}
