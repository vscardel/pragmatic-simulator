"use client";

import React, {useMemo, useEffect, useState} from "react";
import dynamic from "next/dynamic";
import {TableCell} from "./ui/table";
import {useSimulationContext} from "@/contexts/SimulationContext";

// Importação dinâmica para evitar o erro "window is not defined" no Next.js (SSR)
const Plot = dynamic(() => import("react-plotly.js"), {ssr: false});

interface TemperatureChartProps {
  data: number[];
  sampling_interval: number; // Em milissegundos
}

export default function TemperatureChart({data, sampling_interval}: TemperatureChartProps) {
  const [isMounted, setIsMounted] = useState(false);
  const {data: simData} = useSimulationContext();

  // Evita erros de hidratação garantindo que o componente só monte no client-side
  useEffect(() => {
    setIsMounted(true);
  }, []);

  const {xData, yData} = useMemo(() => {
    if (!data || data.length === 0 || sampling_interval <= 0) {
      return {xData: [], yData: []};
    }

    // 10 minutos = 600.000 milissegundos
    const MINUTES_MS = 30 * 60 * 1000;

    // Calcula quantos dados cabem em 10 minutos baseado no intervalo
    const pointsNeeded = Math.ceil(MINUTES_MS / sampling_interval);

    // Pega apenas a fatia final do array (os mais recentes)
    const yData = data.slice(-pointsNeeded);

    // Como os dados vêm sem timestamp, geramos o eixo X (tempo) de trás pra frente
    // Assumimos que o último dado do array acabou de ser lido (agora)
    const now = Date.now();
    const xData = yData.map((_, index) => {
      // Posição reversa: o último item tem índice 0 na contagem de trás pra frente
      const reverseIndex = yData.length - 1 - index;
      return new Date(now - reverseIndex * sampling_interval);
    });

    return {xData, yData};
  }, [data, sampling_interval]);

  const width = 1000;
  const height = 50;

  // Exibe um esqueleto ou container vazio enquanto o componente não é montado no cliente
  if (!isMounted) {
    return <TableCell style={{width, height, backgroundColor: "#f0f0f0"}} />;
  }

  return (
    <TableCell style={{width: `${width}px`, margin: "0 auto"}}>
      <Plot
        data={[
          {
            x: xData,
            y: yData,
            type: "scatter",
            mode: "lines",
            line: {
              color: "#1f77b4",
              width: 2,
            },
            name: "Temperatura",
          },
        ]}
        layout={{
          width,
          height,
          xaxis: {
            type: "date",
            tickformat: "%H:%M:%S",
          },
          yaxis: {},
          margin: {t: 0, l: 50, r: 20, b: 0},
        }}
        config={{
          responsive: false,
          displayModeBar: false,
        }}
      />
    </TableCell>
  );
}
