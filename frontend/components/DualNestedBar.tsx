"use client";

type DualNestedBarProps = {
  grayValue: number;
  yellowValue: number;
  innerYellowValue: number;
};

export function DualNestedBar({grayValue, yellowValue, innerYellowValue}: DualNestedBarProps) {
  const total = grayValue + yellowValue;

  if (total === 0) {
    return <div className="h-5 w-full rounded bg-gray-200" />;
  }

  const grayPct = (grayValue / total) * 100;
  const yellowPct = (yellowValue / total) * 100;

  const safeInner = Math.min(Math.max(innerYellowValue, 0), yellowValue);
  const innerYellowPct = yellowValue > 0 ? (safeInner / yellowValue) * 100 : 0;

  return (
    <div className="flex h-5 w-full overflow-hidden rounded">
      {/* Parte cinza */}
      <div className="bg-gray-300" style={{width: `${grayPct}%`}} />

      {/* Parte amarela */}
      <div className="relative bg-yellow-400" style={{width: `${yellowPct}%`}}>
        {/* Barrinha interna */}
        <div
          className="absolute right-0 top-1/2 h-3 -translate-y-1/2 bg-yellow-600 rounded"
          style={{width: `${innerYellowPct}%`}}
        />
      </div>
    </div>
  );
}
