import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { formatDate, formatMoney } from "../format";
import type { Dashboard } from "../types";

export function DashboardPage() {
  const [data, setData] = useState<Dashboard | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    api<Dashboard>("/api/dashboard")
      .then((next) => {
        if (active) setData(next);
      })
      .catch((err: unknown) => {
        if (active) setError(err instanceof Error ? err.message : "Could not load dashboard");
      });
    return () => {
      active = false;
    };
  }, []);

  if (error) return <p className="form-error">{error}</p>;
  if (!data) return <p className="muted">Loading dashboard…</p>;

  const maxCategory = Math.max(...data.spending_by_category.map((item) => Number(item.total)), 1);
  const maxMonth = Math.max(Number(data.current_month_spending), Number(data.previous_month_spending), 1);

  return (
    <section>
      <header className="page-header">
        <div>
          <h1>Dashboard</h1>
          <p className="muted">Spending for {data.month}</p>
        </div>
        <Link className="button primary" to="/expenses/new">
          Add expense
        </Link>
      </header>

      {data.over_budget && (
        <div className="banner" role="alert">
          Spending exceeds the monthly budget by{" "}
          {formatMoney(Math.abs(Number(data.remaining_budget)), data.currency)}.
        </div>
      )}

      <div className="stats">
        <article className="card stat">
          <span>Current month</span>
          <strong>{formatMoney(data.current_month_spending, data.currency)}</strong>
        </article>
        <article className="card stat">
          <span>Previous month</span>
          <strong>{formatMoney(data.previous_month_spending, data.currency)}</strong>
        </article>
        <article className="card stat">
          <span>Monthly budget</span>
          <strong>{formatMoney(data.monthly_budget, data.currency)}</strong>
        </article>
        <article className={`card stat ${data.over_budget ? "danger" : ""}`}>
          <span>Remaining</span>
          <strong>{formatMoney(data.remaining_budget, data.currency)}</strong>
        </article>
        <article className="card stat">
          <span>Expenses this month</span>
          <strong>{data.expense_count}</strong>
        </article>
      </div>

      <div className="split">
        <article className="card">
          <h2>Spending by category</h2>
          {data.spending_by_category.length === 0 ? (
            <p className="muted">No expenses in {data.currency} this month.</p>
          ) : (
            <ul className="bars">
              {data.spending_by_category.map((item) => (
                <li key={item.category_id}>
                  <div className="bar-label">
                    <span>{item.category}</span>
                    <span>{formatMoney(item.total, data.currency)}</span>
                  </div>
                  <div className="bar-track">
                    <div className="bar-fill" style={{ width: `${(Number(item.total) / maxCategory) * 100}%` }} />
                  </div>
                </li>
              ))}
            </ul>
          )}
        </article>
        <article className="card">
          <h2>Month comparison</h2>
          <ul className="bars">
            <li>
              <div className="bar-label">
                <span>This month</span>
                <span>{formatMoney(data.current_month_spending, data.currency)}</span>
              </div>
              <div className="bar-track">
                <div
                  className="bar-fill"
                  style={{ width: `${(Number(data.current_month_spending) / maxMonth) * 100}%` }}
                />
              </div>
            </li>
            <li>
              <div className="bar-label">
                <span>Last month</span>
                <span>{formatMoney(data.previous_month_spending, data.currency)}</span>
              </div>
              <div className="bar-track">
                <div
                  className="bar-fill alt"
                  style={{ width: `${(Number(data.previous_month_spending) / maxMonth) * 100}%` }}
                />
              </div>
            </li>
          </ul>
        </article>
      </div>

      <article className="card">
        <h2>Recent expenses</h2>
        {data.recent_expenses.length === 0 ? (
          <p className="muted">No expenses yet.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Description</th>
                  <th>Category</th>
                  <th>Amount</th>
                </tr>
              </thead>
              <tbody>
                {data.recent_expenses.map((expense) => (
                  <tr key={expense.id}>
                    <td>{formatDate(expense.date)}</td>
                    <td>
                      <Link to={`/expenses/${expense.id}`}>{expense.description}</Link>
                    </td>
                    <td>{expense.category}</td>
                    <td>{formatMoney(expense.amount, expense.currency)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </article>
    </section>
  );
}
