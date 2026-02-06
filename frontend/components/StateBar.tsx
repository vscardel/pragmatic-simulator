"use client";

type StateBarProps = {
  value: number; // 0 a 3
};

export function StateBar({value}: StateBarProps) {
  const clampedValue = Math.min(Math.max(value, 0), 3);

  // posição percentual da barrinha (0–100%)
  const positionPct = (clampedValue / 3) * 100;

  return (
    <div className="relative w-full">
      {/* Barra colorida */}
      <div className="flex h-4 w-full overflow-hidden rounded">
        <div className="w-1/4 bg-green-500" />
        <div className="w-1/4 bg-yellow-400" />
        <div className="w-1/4 bg-red-500" />
        <div className="w-1/4 bg-black" />
      </div>

      {/* Indicador vertical */}
      <div
        className="absolute top-0 h-4 w-0.5 bg-white shadow"
        style={{
          left: `calc(${positionPct}% - 1px)`,
        }}
      />
    </div>
  );
}
