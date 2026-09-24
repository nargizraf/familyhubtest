import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { formatDate, formatMoney } from "../format";
import type { Category, Expense } from "../types";

interface Filters {
  categoryId: string;
  dateFrom: string;
  dateTo: string;
  q: string;
  sort: string;
  order: string;
}

const initialFilters: Filters = {
  categoryId: "",
  dateFrom: "",
  dateTo: "",
  q: "",
  sort: "date",
  order: "desc",
};

export function ExpensesPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [draft, setDraft] = useState<Filters>(initialFilters);
  const [filters, setFilters] = useState<Filters>(initialFilters);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api<Category[]>("/api/categories")
      .then(setCategories)
      .catch((err: unknown) => setError(err instanceof Error ? err.message : "Could not load categories"));
  }, []);

  useEffect(() => {
    const params = new URLSearchParams();
    if (filters.categoryId) params.set("category_id", filters.categoryId);
    if (filters.dateFrom) params.set("date_from", filters.dateFrom);
    if (filters.dateTo) params.set("date_to", filters.dateTo);
    if (filters.q.trim()) params.set("q", filters.q.trim());
    params.set("sort", filters.sort);
    params.set("order", filters.order);
    let active = true;
    setLoading(true);
    api<Expense[]>(`/api/expenses?${params.toString()}`)
      .then((next) => {
        if (active) setExpenses(next);
      })
      .catch((err: unknown) => {
        if (active) setError(err instanceof Error ? err.message : "Could not load expenses");
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [filters]);

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    setFilters(draft);
  }

  return (
    <section>
      <header className="page-header">
        <div>
          <h1>Expenses</h1>
          <p className="muted">Filter, sort, and open an expense to edit it.</p>
        </div>
        <Link className="button primary" to="/expenses/new">
          New expense
        </Link>
      </header>
      {error && <p className="form-error">{error}</p>}
      <form className="card filters" onSubmit={onSubmit}>
        <label>
          Search
          <input
            value={draft.q}
            onChange={(event) => setDraft({ ...draft, q: event.target.value })}
            placeholder="Description"
          />
        </label>
        <label>
          Category
          <select
            value={draft.categoryId}
            onChange={(event) => setDraft({ ...draft, categoryId: event.target.value })}
          >
            <option value="">All</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          From
          <input
            type="date"
            value={draft.dateFrom}
            onChange={(event) => setDraft({ ...draft, dateFrom: event.target.value })}
          />
        </label>
        <label>
          To
          <input
            type="date"
            value={draft.dateTo}
            onChange={(event) => setDraft({ ...draft, dateTo: event.target.value })}
          />
        </label>
        <label>
          Sort
          <select value={draft.sort} onChange={(event) => setDraft({ ...draft, sort: event.target.value })}>
            <option value="date">Date</option>
            <option value="amount">Amount</option>
            <option value="description">Description</option>
            <option value="category">Category</option>
            <option value="created_at">Created</option>
          </select>
        </label>
        <label>
          Order
          <select value={draft.order} onChange={(event) => setDraft({ ...draft, order: event.target.value })}>
            <option value="desc">Descending</option>
            <option value="asc">Ascending</option>
          </select>
        </label>
        <div className="filter-actions">
          <button className="button primary" type="submit">
            Apply
          </button>
          <button
            className="button ghost"
            type="button"
            onClick={() => {
              setDraft(initialFilters);
              setFilters(initialFilters);
            }}
          >
            Reset
          </button>
        </div>
      </form>

      <article className="card">
        {loading ? (
          <p className="muted">Loading expenses…</p>
        ) : expenses.length === 0 ? (
          <p className="muted">No expenses match these filters.</p>
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
                {expenses.map((expense) => (
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
