import { FormEvent, useEffect, useState } from "react";
import { api } from "../api";
import { useAuth } from "../auth";
import { CURRENCIES, formatMoney } from "../format";
import type { Budget } from "../types";

export function SettingsPage() {
  const { user } = useAuth();
  const [budget, setBudget] = useState<Budget | null>(null);
  const [amount, setAmount] = useState("");
  const [currency, setCurrency] = useState("PLN");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    let active = true;
    api<Budget>("/api/budget")
      .then((next) => {
        if (!active) return;
        setBudget(next);
        setAmount(next.amount ?? "");
        setCurrency(next.currency || "PLN");
      })
      .catch((err: unknown) => {
        if (active) setError(err instanceof Error ? err.message : "Could not load budget");
      });
    return () => {
      active = false;
    };
  }, []);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setMessage("");
    try {
      const next = await api<Budget>("/api/budget", {
        method: "PUT",
        body: JSON.stringify({ amount, currency }),
      });
      setBudget(next);
      setAmount(next.amount ?? "");
      setCurrency(next.currency);
      setMessage("Monthly budget saved.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save budget");
    }
  }

  return (
    <section>
      <header className="page-header">
        <div>
          <h1>Settings</h1>
          <p className="muted">Account details and the monthly spending limit.</p>
        </div>
      </header>
      {error && <p className="form-error">{error}</p>}
      {budget?.over_budget && (
        <div className="banner" role="alert">
          Spending this month exceeds the budget by{" "}
          {formatMoney(Math.abs(Number(budget.remaining)), budget.currency)}.
        </div>
      )}
      <div className="split">
        <article className="card">
          <h2>Account</h2>
          <p>
            <strong>{user?.full_name}</strong>
          </p>
          <p className="muted">{user?.email}</p>
        </article>
        <form className="card form-grid" onSubmit={onSubmit}>
          <h2>Monthly budget</h2>
          {message && <p className="success">{message}</p>}
          <label>
            Amount
            <input
              type="number"
              min="0.01"
              step="0.01"
              value={amount}
              onChange={(event) => setAmount(event.target.value)}
              required
            />
          </label>
          <label>
            Currency
            <select value={currency} onChange={(event) => setCurrency(event.target.value)}>
              {CURRENCIES.map((code) => (
                <option key={code} value={code}>
                  {code}
                </option>
              ))}
            </select>
          </label>
          {budget && (
            <div className="stats compact">
              <article className="stat">
                <span>Spent in {budget.month}</span>
                <strong>{formatMoney(budget.spent, budget.currency)}</strong>
              </article>
              <article className={`stat ${budget.over_budget ? "danger" : ""}`}>
                <span>Remaining</span>
                <strong>{formatMoney(budget.remaining, budget.currency)}</strong>
              </article>
            </div>
          )}
          <button className="button primary" type="submit">
            Save budget
          </button>
        </form>
      </div>
    </section>
  );
}
