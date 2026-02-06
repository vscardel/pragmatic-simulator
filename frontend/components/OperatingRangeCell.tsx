"use client";

import {TableCell} from "@/components/ui/table";
import {OperatingRange} from "@/contexts/SimulationContext";

type OperatingCellProps = {
  range: OperatingRange;
  mean_value: number;
  standard_deviation: number;
  last_value: number;
  last_thousand_values: number[];
};

export function OperatingRangeCell({
  range,
  mean_value,
  standard_deviation,
  last_value,
  last_thousand_values,
}: OperatingCellProps) {
  const [cMin, cMax] = range.critical;
  const width = cMax - cMin;

  const toPct01 = (v: number) => (v - cMin) / width;
  const toPct = (v: number) => toPct01(v) * 100;
  const toPx = (v: number) => toPct01(v) * 404;

  /* ---------------- Histogram ---------------- */

  const BINS = 72;
  const bins = Array(BINS).fill(0);

  last_thousand_values.forEach((v) => {
    if (v < cMin || v > cMax) return;
    const idx = Math.min(BINS - 1, Math.floor(((v - cMin) / width) * BINS));
    bins[idx]++;
  });

  const maxBin = Math.max(...bins);

  /* ---------------- State color ---------------- */

  const meanColor =
    mean_value >= range.normal[0] && mean_value <= range.normal[1]
      ? "bg-green-500"
      : mean_value >= range.degraded[0] && mean_value <= range.degraded[1]
        ? "bg-yellow-400"
        : "bg-red-500";

  /* ---------------- Render ---------------- */

  return (
    <TableCell className="w-105">
      <div className="relative h-24 w-full">
        {/* Critical */}
        <div className="absolute inset-0 bg-red-400/30 rounded" />

        {/* Degraded */}
        <div
          className="absolute top-0 bottom-0 bg-yellow-300/40"
          style={{
            left: `${toPct(range.degraded[0])}%`,
            width: `${toPct(range.degraded[1]) - toPct(range.degraded[0])}%`,
          }}
        />

        {/* Normal */}
        <div
          className="absolute top-0 bottom-0 bg-green-400/40"
          style={{
            left: `${toPct(range.normal[0])}%`,
            width: `${toPct(range.normal[1]) - toPct(range.normal[0])}%`,
          }}
        />

        {/* Histogram */}
        <div className="absolute bottom-0 left-0 right-0 h-1/2 flex items-end">
          {bins.map((b, i) => (
            <div
              key={i}
              className="flex-1 mx-px bg-gray-800/50"
              style={{
                height: `${(b / maxBin) * 100}%`,
              }}
            />
          ))}
        </div>

        {/* Mean */}
        <div
          className={`absolute top-0 bottom-0 w-0.5 ${meanColor}`}
          style={{left: `${toPct(mean_value)}%`}}
        />

        {/* Std deviation */}
        <div
          className={`absolute h-1 ${meanColor}`}
          style={{
            top: "50%",
            left: `${toPct(mean_value - standard_deviation)}%`,
            width: `${toPct(mean_value + standard_deviation) - toPct(mean_value - standard_deviation)}%`,
            transform: "translateY(-50%)",
          }}
        />

        {/* Last value */}
        <div className="absolute top-0 bottom-0 w-0.5 bg-blue-600" style={{left: `${toPct(last_value)}%`}} />
      </div>

      {/* Labels */}
      <div className="relative mb-1 flex justify-between text-[10px] text-muted-foreground">
        <span className={`absolute left-0`}>{range.critical[0]}</span>
        <span style={{left: toPx(range.degraded[0]) + "px"}} className={`absolute`}>
          {range.degraded[0]}
        </span>
        <span style={{left: toPx(range.normal[0]) + "px"}} className={`absolute`}>
          {range.normal[0]}
        </span>
        <span style={{left: toPx(range.normal[1]) + "px"}} className={`absolute -translate-x-full`}>
          {range.normal[1]}
        </span>
        <span style={{left: toPx(range.degraded[1]) + "px"}} className={`absolute -translate-x-full`}>
          {range.degraded[1]}
        </span>
        <span className={`absolute right-0`}>{range.critical[1]}</span>
      </div>
    </TableCell>
  );
}
