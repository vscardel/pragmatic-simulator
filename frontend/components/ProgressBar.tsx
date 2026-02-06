"use client";

type ProgressBarProps = {
  value: number;
  max: number;
};

export function ProgressBar({value, max}: ProgressBarProps) {
  const safeMax = max > 0 ? max : 1;
  const percentage = Math.min(Math.max(value / safeMax, 0), 1) * 100;

  return (
    <div className="w-full">
      <div className="h-3 w-full rounded bg-gray-200 overflow-hidden">
        <div className="h-full bg-green-500 transition-all duration-300" style={{width: `${percentage}%`}} />
      </div>
    </div>
  );
}
