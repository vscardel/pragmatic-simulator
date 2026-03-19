"use client";

import React, {useState, useMemo} from "react";
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
import clsx from "clsx";

type QTableRawData = {
  [key: string]: [number, number];
};

const ActionLabels = ["DO NOTHING", "UPKEEP"];

interface QEntry {
  sensorId: number;
  sensorRole: number;
  valueBin: number;
  availableTeams: number;
  qValues: [number, number];
  bestAction: number;
}

export default function QTableVisualizer() {
  const {data} = useSimulationContext();
  const [filterSensor, setFilterSensor] = useState<string>("");

  const parsedData = useMemo(() => {
    if (!data?.broker?.q_table) return [];

    const entries: QEntry[] = [];

    Object.entries(data.broker.q_table).forEach(([key, values]) => {
      // Regex captura 4 números: (sensorId, sensorRole, valueBin, availableTeams)
      const match = key.match(/\((\d+),\s*(\d+),\s*(-?\d+),\s*(\d+)\)/);

      if (match) {
        const sensorId = parseInt(match[1]);
        const sensorRole = parseInt(match[2]);
        const valueBin = parseInt(match[3]);
        const availableTeams = parseInt(match[4]);
        const bestAction = values[1] > values[0] ? 1 : 0;

        entries.push({
          sensorId,
          sensorRole,
          valueBin,
          availableTeams,
          qValues: values,
          bestAction,
        });
      }
    });

    // Ordenação: Sensor ID -> Times Disponíveis -> Faixa
    return entries.sort((a, b) => {
      if (a.sensorId !== b.sensorId) return a.sensorId - b.sensorId;
      if (a.availableTeams !== b.availableTeams) return a.availableTeams - b.availableTeams;
      return a.valueBin - b.valueBin;
    });
  }, [data?.broker?.q_table]);

  const filteredData = parsedData.filter(
    (entry) => filterSensor === "" || entry.sensorId.toString() === filterSensor,
  );

  if (!data) return null;

  return (
    <div className="p-6 bg-white rounded-xl border shadow-sm w-full max-w-6xl mx-auto space-y-4">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Cérebro do Agente (Q-Table)</h2>
          <p className="text-sm text-muted-foreground">
            Monitoramento das políticas de decisão aprendidas pelo Broker.
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

      <div className="rounded-md border">
        <Table>
          <TableCaption>Total de {parsedData.length} estados observados no simulador.</TableCaption>
          <TableHeader>
            <TableRow className="bg-muted/50">
              <TableHead className="w-[100px]">Sensor ID</TableHead>
              <TableHead className="w-[100px]">Sensor Role</TableHead>
              <TableHead>Eq. Livres</TableHead>
              <TableHead>Valor (temperatura)</TableHead>
              <TableHead className="text-right border-l">Q: Do Nothing</TableHead>
              <TableHead className="text-right">Q: Upkeep</TableHead>
              <TableHead className="text-center border-l w-[150px]">Decisão</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredData.length > 0 ? (
              filteredData.map((row, index) => {
                const sensorOpRange = data.sensors.find(
                  (sensor) => sensor.sensor_id === row.sensorId,
                )!.operating_range;

                return (
                  <TableRow
                    key={index}
                    className={clsx(
                      row.valueBin >= sensorOpRange.normal[0] && row.valueBin <= sensorOpRange.normal[1]
                        ? "bg-green-50/80"
                        : row.valueBin >= sensorOpRange.degraded[0] &&
                            row.valueBin <= sensorOpRange.degraded[1]
                          ? "bg-orange-50/80"
                          : row.valueBin >= sensorOpRange.critical[0] &&
                              row.valueBin <= sensorOpRange.critical[1]
                            ? "bg-red-50/80"
                            : "bg-gray-400/80",
                    )}
                  >
                    <TableCell className="font-medium">#{row.sensorId}</TableCell>
                    <TableCell className="font-medium">#{row.sensorRole}</TableCell>
                    <TableCell>
                      <span className="bg-blue-50 text-blue-700 px-2 py-1 rounded-md text-xs font-bold">
                        {row.availableTeams}
                      </span>
                    </TableCell>
                    <TableCell>{row.valueBin}</TableCell>

                    <TableCell
                      className={`text-right font-mono border-l ${row.bestAction === 0 ? "bg-green-50/50 font-bold text-green-600 dark:text-green-500" : "text-muted-foreground"}`}
                    >
                      {row.qValues[0].toFixed(2)}
                    </TableCell>

                    <TableCell
                      className={`text-right font-mono ${row.bestAction === 1 ? "bg-orange-50/50 font-bold text-orange-600 dark:text-orange-500" : "text-muted-foreground"}`}
                    >
                      {row.qValues[1].toFixed(2)}
                    </TableCell>

                    <TableCell className="text-center border-l">
                      <span
                        className={`text-xs font-bold uppercase tracking-wider ${row.bestAction === 1 ? "text-orange-600" : "text-muted-foreground"}`}
                      >
                        {ActionLabels[row.bestAction]}
                      </span>
                    </TableCell>
                  </TableRow>
                );
              })
            ) : (
              <TableRow>
                <TableCell colSpan={6} className="h-24 text-center">
                  Nenhum dado encontrado.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
