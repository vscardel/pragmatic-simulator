"use client";

type FourStateBarProps = {
  green: number;
  yellow: number;
  red: number;
  black: number;
  greenLabel?: string;
  yellowLabel?: string;
  redLabel?: string;
  blackLabel?: string;
};

export function FourStateBar({
  green,
  yellow,
  red,
  black,
  greenLabel = "Green",
  yellowLabel = "Yellow",
  redLabel = "Red",
  blackLabel = "Black",
}: FourStateBarProps) {
  const total = green + yellow + red + black;

  if (total === 0) {
    return <div className="h-4 w-full rounded bg-gray-200" />;
  }

  const greenPct = (green / total) * 100;
  const yellowPct = (yellow / total) * 100;
  const redPct = (red / total) * 100;
  const blackPct = (black / total) * 100;

  return (
    <div className="w-full space-y-1">
      {/* Barra */}
      <div className="flex h-4 w-full overflow-hidden rounded">
        <div className="bg-green-500" style={{width: `${greenPct}%`}} />
        <div className="bg-yellow-400" style={{width: `${yellowPct}%`}} />
        <div className="bg-red-500" style={{width: `${redPct}%`}} />
        <div className="bg-black" style={{width: `${blackPct}%`}} />
      </div>

      {/* Legenda */}
      <div className="flex justify-between text-xs">
        <span className="text-green-600">
          {greenLabel} ({green})
        </span>
        <span className="text-yellow-600">
          {yellowLabel} ({yellow})
        </span>
        <span className="text-red-600">
          {redLabel} ({red})
        </span>
        <span className="text-gray-800">
          {blackLabel} ({black})
        </span>
      </div>
    </div>
  );
}
