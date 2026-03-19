"use client";

import React, {useMemo, useState} from "react";
import dynamic from "next/dynamic";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {Input} from "@/components/ui/input";
import {useSimulationContext} from "@/contexts/SimulationContext";

type QTableRawData = {
  [key: string]: [number, number];
};

interface BinData {
  qValues: [number, number];
  bestAction: number;
  isExplored: boolean;
}

interface SensorPolicy {
  sensorId: number;
  availableTeams: number;
  bins: Record<number, BinData>;
  minBin: number;
  maxBin: number;
}

const Plot = dynamic(() => import("react-plotly.js"), {ssr: false});

export default function PolicyMapVisualizer() {
  const {data} = useSimulationContext();
  const [filterSensor, setFilterSensor] = useState<string>("");

  // Novo estado para rastrear quais gráficos estão visíveis. Por padrão, vazio (nenhum renderizado).
  const [visibleCharts, setVisibleCharts] = useState<Record<string, boolean>>({});

  // Função para alternar a visibilidade do gráfico de uma linha específica
  const toggleChartVisibility = (policyKey: string) => {
    setVisibleCharts((prev) => ({
      ...prev,
      [policyKey]: !prev[policyKey],
    }));
  };

  const sensorsById = useMemo(() => {
    const map: Record<number, any> = {};
    if (data?.sensors) {
      data.sensors.forEach((s) => {
        map[s.sensor_id] = s;
      });
    }
    return map;
  }, [data?.sensors]);

  const {policies, maxBin} = useMemo(() => {
    if (!data?.broker?.q_table) return {policies: [], maxBin: 0};

    const sensorMap: Record<string, SensorPolicy> = {};
    let globalMaxBin = 0;

    // Mapeia o range de operação crítico (em bins) por sensor
    const sensorRangeMap: Record<
      number,
      {
        minBin: number;
        maxBin: number;
      }
    > = {};

    data.sensors.forEach((sensor) => {
      const criticalMin = sensor.operating_range.critical[0];
      const criticalMax = sensor.operating_range.critical[1];

      const minBin = Math.floor(criticalMin);
      const maxBin = Math.floor(criticalMax);

      sensorRangeMap[sensor.sensor_id] = {minBin, maxBin};
    });

    Object.entries(data.broker.q_table).forEach(([key, values]) => {
      // Formato antigo: (sensorId, valueBin, availableTeams)
      const matchLegacy = key.match(/\((\d+),\s*(-?\d+),\s*(\d+)\)/);
      // Formato atual: (sensorId, sensorRole, valueBin, availableTeams)
      const matchCurrent = key.match(/\((\d+),\s*(\d+),\s*(-?\d+),\s*(\d+)\)/);

      let sensorId: number | null = null;
      let valueBin: number | null = null;
      let availableTeams: number | null = null;

      if (matchCurrent) {
        sensorId = parseInt(matchCurrent[1]);
        valueBin = parseInt(matchCurrent[3]);
        availableTeams = parseInt(matchCurrent[4]);
      } else if (matchLegacy) {
        sensorId = parseInt(matchLegacy[1]);
        valueBin = parseInt(matchLegacy[2]);
        availableTeams = parseInt(matchLegacy[3]);
      }

      if (
        sensorId === null ||
        valueBin === null ||
        availableTeams === null ||
        Number.isNaN(sensorId) ||
        Number.isNaN(valueBin) ||
        Number.isNaN(availableTeams)
      ) {
        return;
      }

      const range = sensorRangeMap[sensorId];
      if (!range) {
        return;
      }

      const bestAction = values[1] > values[0] ? 1 : 0;

      if (valueBin > globalMaxBin) {
        globalMaxBin = valueBin;
      }

      // A chave de agrupamento é uma combinação do ID e os Times Disponíveis
      const policyKey = `${sensorId}-${availableTeams}`;

      if (!sensorMap[policyKey]) {
        sensorMap[policyKey] = {
          sensorId,
          availableTeams,
          bins: {},
          minBin: range.minBin,
          maxBin: range.maxBin,
        };
      }

      sensorMap[policyKey].bins[valueBin] = {
        qValues: values,
        bestAction,
        isExplored: true,
      };
    });

    // Ordenação: Sensor ID -> Times Disponíveis
    const sortedPolicies = Object.values(sensorMap).sort((a, b) => {
      if (a.sensorId !== b.sensorId) return a.sensorId - b.sensorId;
      return a.availableTeams - b.availableTeams;
    });

    return {policies: sortedPolicies, maxBin: globalMaxBin};
  }, [data?.broker?.q_table, data?.sensors]);

  if (!data) return null;

  const filteredPolicies = policies.filter(
    (p) => filterSensor === "" || p.sensorId.toString() === filterSensor,
  );

  return (
    <div className="p-6 bg-white rounded-xl border shadow-sm w-full max-w-360 mx-auto space-y-4">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Mapa de Políticas (Policy Map)</h2>
          <p className="text-sm text-muted-foreground">
            Visualização das faixas de operação. <span className="text-orange-500 font-bold">Laranja</span>{" "}
            indica manutenção (Upkeep) e <span className="text-gray-500 font-bold">Cinza</span> indica
            ignorar.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-foreground whitespace-nowrap">Filtrar Sensor ID:</label>
          <Input
            type="number"
            value={filterSensor}
            onChange={(e) => setFilterSensor(e.target.value)}
            placeholder="Todos"
            className="w-24"
          />
        </div>
      </div>

      <div className="rounded-md border overflow-hidden max-w-360">
        <Table className="min-w-150 overflow-hidden">
          <TableCaption>
            Visualizando limiares para {filteredPolicies.length} cenários (Sensor + Times Disp.).
          </TableCaption>
          <TableHeader>
            <TableRow className="bg-muted/50">
              <TableHead className="w-50">Ativo / Estado</TableHead>
              <TableHead>Espectro de Faixas (bins no range crítico do sensor)</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredPolicies.length > 0 ? (
              filteredPolicies.map((policy) => {
                const policyKey = `${policy.sensorId}-${policy.availableTeams}`;
                const isChartVisible = !!visibleCharts[policyKey];

                return (
                  <TableRow key={policyKey}>
                    <TableCell className="font-medium whitespace-nowrap align-top pt-4">
                      <div className="flex items-start gap-3">
                        {/* Checkbox adicionado aqui */}
                        <div className="flex items-center h-5 mt-0.5">
                          <input
                            type="checkbox"
                            checked={isChartVisible}
                            onChange={() => toggleChartVisibility(policyKey)}
                            className="w-4 h-4 cursor-pointer accent-orange-500 border-gray-300 rounded focus:ring-orange-500"
                            title="Mostrar Gráfico Q-Table"
                          />
                        </div>
                        <div>
                          Sensor #{policy.sensorId} <br />
                          <span className="text-xs text-muted-foreground font-normal">
                            Eq. Livres:{" "}
                            <span className="font-bold text-foreground">{policy.availableTeams}</span>
                          </span>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="max-w-7xl pt-4">
                      <div className="flex flex-col gap-1">
                        {/* Bins de política */}
                        <div className="flex w-full h-6 rounded-md overflow-hidden border border-gray-200 bg-gray-50/50">
                          {Array.from({length: policy.maxBin - policy.minBin + 1}).map((_, idx) => {
                            const binIndex = policy.minBin + idx;
                            const binData = policy.bins[binIndex];

                            if (!binData) {
                              return (
                                <div
                                  key={binIndex}
                                  className="flex-1 min-w-0 overflow-hidden whitespace-nowrap border-r last:border-r-0 border-dashed border-gray-300 flex items-center justify-center"
                                  title={`Faixa ${binIndex}: Não explorada`}
                                >
                                  <span className="text-[10px] text-gray-300">{binIndex}</span>
                                </div>
                              );
                            }

                            const isUpkeep = binData.bestAction === 1;

                            return (
                              <div
                                key={binIndex}
                                className={`flex-1 min-w-0 overflow-hidden border-r whitespace-nowrap last:border-r-0 border-white/20 flex items-center justify-center transition-colors hover:opacity-80 cursor-help
                                  ${isUpkeep ? "bg-orange-400 text-orange-50" : "bg-gray-400 text-gray-100"}`}
                                title={`Faixa ${binIndex}\nQ(Do Nothing): ${binData.qValues[0].toFixed(2)}\nQ(Upkeep): ${binData.qValues[1].toFixed(2)}`}
                              >
                                <span className="text-xs font-bold">{binIndex}</span>
                              </div>
                            );
                          })}
                        </div>

                        {/* Linha fininha com range real de operação */}
                        <div className="flex w-full h-1 rounded-md overflow-hidden">
                          {Array.from({length: policy.maxBin - policy.minBin + 1}).map((_, idx) => {
                            const binIndex = policy.minBin + idx;
                            const sensor = sensorsById[policy.sensorId];
                            if (!sensor) {
                              return <div key={`range-${binIndex}`} className="flex-1 bg-transparent" />;
                            }

                            const binValue = binIndex;
                            const [nMin, nMax] = sensor.operating_range.normal;
                            const [dMin, dMax] = sensor.operating_range.degraded;
                            const [cMin, cMax] = sensor.operating_range.critical;

                            let colorClass = "bg-transparent";
                            if (binValue >= nMin && binValue <= nMax) {
                              colorClass = "bg-emerald-400"; // normal
                            } else if (binValue >= dMin && binValue <= dMax) {
                              colorClass = "bg-yellow-400"; // degraded
                            } else if (binValue >= cMin && binValue <= cMax) {
                              colorClass = "bg-red-400"; // critical
                            }

                            return <div key={`range-${binIndex}`} className={`flex-1 ${colorClass}`} />;
                          })}
                        </div>

                        {/* Gráfico de linhas - Renderizado condicionalmente */}
                        {isChartVisible && (
                          <div className="w-full h-12.5 mt-2 transition-all duration-300 animate-in fade-in slide-in-from-top-2">
                            {(() => {
                              const binsEntries = Object.entries(policy.bins)
                                .map(([bin, binData]) => ({bin: Number(bin), binData}))
                                .sort((a, b) => a.bin - b.bin);

                              if (binsEntries.length < 2) return null;

                              const x = binsEntries.map((e) => e.bin);
                              const yDoNothing = binsEntries.map((e) => e.binData.qValues[0]);
                              const yUpkeep = binsEntries.map((e) => e.binData.qValues[1]);

                              return (
                                <Plot
                                  data={[
                                    {
                                      x,
                                      y: yDoNothing,
                                      type: "scatter",
                                      mode: "lines",
                                      line: {color: "#9ca3af", width: 1},
                                      name: "Do Nothing",
                                    },
                                    {
                                      x,
                                      y: yUpkeep,
                                      type: "scatter",
                                      mode: "lines",
                                      line: {color: "#fb923c", width: 1},
                                      name: "Upkeep",
                                    },
                                  ]}
                                  layout={{
                                    autosize: true,
                                    height: 50,
                                    margin: {l: 4, r: 4, t: 2, b: 8},
                                    showlegend: false,
                                    xaxis: {
                                      showgrid: false,
                                      zeroline: false,
                                      tickfont: {size: 6},
                                      range: [policy.minBin - 0.5, policy.maxBin + 0.5],
                                      dtick: 1,
                                      fixedrange: true,
                                    },
                                    yaxis: {
                                      showgrid: false,
                                      zeroline: false,
                                      tickfont: {size: 6},
                                      fixedrange: true,
                                    },
                                  }}
                                  config={{
                                    displayModeBar: false,
                                    responsive: true,
                                  }}
                                  style={{width: "100%", height: "100%"}}
                                />
                              );
                            })()}
                          </div>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })
            ) : (
              <TableRow>
                <TableCell colSpan={2} className="h-24 text-center">
                  Nenhum sensor encontrado.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
