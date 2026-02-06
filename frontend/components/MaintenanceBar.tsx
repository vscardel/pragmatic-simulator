"use client";

type MaintenanceBarProps = {
  critical_maintenances: number;
  degraded_maintenances: number;
  unnecessary_maintenances: number;
};

export function MaintenanceBar({
  critical_maintenances,
  degraded_maintenances,
  unnecessary_maintenances,
}: MaintenanceBarProps) {
  const total = critical_maintenances + degraded_maintenances + unnecessary_maintenances;

  if (total === 0) {
    return <div className="h-4 w-full rounded bg-gray-200" />;
  }

  const criticalPct = (critical_maintenances / total) * 100;
  const degradedPct = (degraded_maintenances / total) * 100;
  const unnecessaryPct = (unnecessary_maintenances / total) * 100;

  return (
    <div className="flex h-4 w-full overflow-hidden rounded">
      <div className="bg-yellow-400" style={{width: `${degradedPct}%`}} />
      <div className="bg-red-500" style={{width: `${criticalPct}%`}} />
      <div className="bg-gray-300" style={{width: `${unnecessaryPct}%`}} />
    </div>
  );
}
