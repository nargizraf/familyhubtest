import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import { CURRENCIES, formatDate, todayInputValue } from "../format";
import type { Category, Expense, ExpenseInput } from "../types";

const emptyForm = (): ExpenseInput => ({
  amount: "",
  currency: "PLN",
  description: "",
  category_id: "",
  date: todayInputValue(),
});

export function ExpenseFormPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isNew = !id;
  const [categories, setCategories] = useState<Category[]>([]);
  const [form, setForm] = useState<ExpenseInput>(emptyForm);
  const [error, setError] = useState("");
  const [savedAt, setSavedAt] = useState("");
  const [loading, setLoading] = useState(!isNew);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    let active = true;
    api<Category[]>("/api/categories")
      .then((next) => {
        if (!active) return;
        setCategories(next);
        if (isNew && next.length > 0) {
          setForm((current) => ({ ...current, category_id: current.category_id || next[0].id }));
        }
      })
      .catch((err: unknown) => {
        if (active) setError(err instanceof Error ? err.message : "Could not load categories");
      });
    return () => {
      active = false;
    };
  }, [isNew]);

  useEffect(() => {
    if (!id) return;
    let active = true;
    api<Expense>(`/api/expenses/${id}`)
      .then((expense) => {
        if (!active) return;
        setForm({
          amount: expense.amount,
          currency: expense.currency,
          description: expense.description,
          category_id: expense.category_id,
          date: expense.date.slice(0, 10),
        });
        setSavedAt(expense.updated_at);
        setLoading(false);
      })
      .catch((err: unknown) => {
        if (!active) return;
        setError(err instanceof Error ? err.message : "Expense not found");
        setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [id]);

  function update<K extends keyof ExpenseInput>(key: K, value: ExpenseInput[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      if (isNew) {
        const created = await api<Expense>("/api/expenses", {
          method: "POST",
          body: JSON.stringify(form),
        });
        navigate(`/expenses/${created.id}`);
      } else {
        const updated = await api<Expense>(`/api/expenses/${id}`, {
          method: "PUT",
          body: JSON.stringify(form),
        });
        setSavedAt(updated.updated_at);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save expense");
    } finally {
      setSubmitting(false);
    }
  }

  async function onDelete() {
    if (!id || !window.confirm("Delete this expense?")) return;
    setSubmitting(true);
    try {
      await api<void>(`/api/expenses/${id}`, { method: "DELETE" });
      navigate("/expenses");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not delete expense");
      setSubmitting(false);
    }
  }

  return (
    <section>
      <header className="page-header">
        <div>
          <h1>{isNew ? "New expense" : "Expense"}</h1>
          <p className="muted">
            <Link to="/expenses">Back to expenses</Link>
          </p>
        </div>
      </header>
      {error && <p className="form-error">{error}</p>}
      {loading ? (
        <p className="muted">Loading expense…</p>
      ) : (
        <form className="card form-grid" onSubmit={onSubmit}>
          <label>
            Description
            <input value={form.description} onChange={(event) => update("description", event.target.value)} required />
          </label>
          <label>
            Amount
            <input
              type="number"
              min="0.01"
              step="0.01"
              value={form.amount}
              onChange={(event) => update("amount", event.target.value)}
              required
            />
          </label>
          <label>
            Currency
            <select value={form.currency} onChange={(event) => update("currency", event.target.value)}>
              {CURRENCIES.map((currency) => (
                <option key={currency} value={currency}>
                  {currency}
                </option>
              ))}
            </select>
          </label>
          <label>
            Category
            <select
              value={form.category_id}
              onChange={(event) => update("category_id", event.target.value)}
              required
            >
              <option value="" disabled>
                Select a category
              </option>
              {categories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Date
            <input type="date" value={form.date} onChange={(event) => update("date", event.target.value)} required />
          </label>
          {categories.length === 0 && (
            <p className="muted">
              Add a category before saving. <Link to="/categories">Manage categories</Link>
            </p>
          )}
          {!isNew && savedAt && <p className="muted">Last updated {formatDate(savedAt)}</p>}
          <div className="form-actions">
            <button className="button primary" type="submit" disabled={submitting || categories.length === 0}>
              {submitting ? "Saving…" : "Save expense"}
            </button>
            {!isNew && (
              <button className="button danger" type="button" onClick={onDelete} disabled={submitting}>
                Delete expense
              </button>
            )}
          </div>
        </form>
      )}
    </section>
  );
}
