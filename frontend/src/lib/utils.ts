import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { format, addDays, parseISO } from "date-fns";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: Date | string): string {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return format(dateObj, 'MMM dd, yyyy');
}

export function formatShortDate(date: Date | string): string {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return format(dateObj, 'MMM dd');
}

export function formatNumber(num: number): string {
  return new Intl.NumberFormat('en-US').format(Math.round(num));
}

export function formatPercentage(num: number): string {
  return `${num.toFixed(1)}%`;
}

export function getDateRange(startDate: string, days: number): string[] {
  const start = parseISO(startDate);
  const dates = [];
  
  for (let i = 0; i < days; i++) {
    dates.push(format(addDays(start, i), 'yyyy-MM-dd'));
  }
  
  return dates;
}

export function getToday(): string {
  return format(new Date(), 'yyyy-MM-dd');
}

export function addDaysToDate(date: string, days: number): string {
  return format(addDays(parseISO(date), days), 'yyyy-MM-dd');
} 