export function formatMoney(amount: string | number | null | undefined, currency = "PLN"): string {
  if (amount === null || amount === undefined || amount === "") {
    return "—";
  }
  const value = typeof amount === "number" ? amount : Number(amount);
  if (Number.isNaN(value)) {
    return "—";
  }
  const locale = currency === "PLN" ? "pl-PL" : "en-GB";
  return new Intl.NumberFormat(locale, { style: "currency", currency }).format(value);
}

export function formatDate(value: string): string {
  const [year, month, day] = value.slice(0, 10).split("-").map(Number);
  if (!year || !month || !day) {
    return value;
  }
  return new Intl.DateTimeFormat("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  }).format(new Date(Date.UTC(year, month - 1, day)));
}

export function todayInputValue(): string {
  const now = new Date();
  const local = new Date(now.getTime() - now.getTimezoneOffset() * 60_000);
  return local.toISOString().slice(0, 10);
}

export const CURRENCIES = ["PLN", "EUR", "USD", "GBP"] as const;
