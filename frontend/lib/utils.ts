import {clsx, type ClassValue} from "clsx";
import {twMerge} from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatMilliseconds(ms: number, full = false): string {
  if (ms < 0) throw new Error("O valor não pode ser negativo");

  const units = [
    {label: full ? "year" : "y", ms: 365 * 24 * 60 * 60 * 1000},
    {label: full ? "month" : "m", ms: 30 * 24 * 60 * 60 * 1000},
    {label: full ? "week" : "w", ms: 7 * 24 * 60 * 60 * 1000},
    {label: full ? "day" : "d", ms: 24 * 60 * 60 * 1000},
    {label: full ? "hour" : "h", ms: 60 * 60 * 1000},
    {label: full ? "minute" : "min", ms: 60 * 1000},
    {label: full ? "second" : "s", ms: 1000},
    {label: "ms", ms: 1},
  ];

  let remaining = ms;
  const parts: string[] = [];

  for (const unit of units) {
    const value = Math.floor(remaining / unit.ms);
    if (value > 0) {
      parts.push(`${value} ${unit.label}${value > 1 && unit.label !== "ms" && full ? "s" : ""}`);
      remaining -= value * unit.ms;
    }
  }

  return parts.length ? parts.join(", ") : "0 ms";
}
