"use client";

type DualStatusBarProps = {
  green: number;
  red: number;
};

export function DualStatusBar({green, red}: DualStatusBarProps) {
  const total = green + red;

  if (total === 0) {
    return <div className="h-4 w-full rounded bg-gray-200" />;
  }

  const greenPct = (green / total) * 100;
  const redPct = (red / total) * 100;

  return (
    <div className="flex h-4 w-full overflow-hidden rounded">
      <div className="bg-green-500" style={{width: `${greenPct}%`}} />
      <div className="bg-red-500" style={{width: `${redPct}%`}} />
    </div>
  );
}
