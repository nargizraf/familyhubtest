import { FormEvent, useEffect, useState } from "react";
import { api } from "../api";
import type { Category } from "../types";

export function CategoriesPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [name, setName] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingName, setEditingName] = useState("");
  const [error, setError] = useState("");

  async function load() {
    const next = await api<Category[]>("/api/categories");
    setCategories(next);
  }

  useEffect(() => {
    load().catch((err: unknown) => setError(err instanceof Error ? err.message : "Could not load categories"));
  }, []);

  async function onCreate(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await api("/api/categories", { method: "POST", body: JSON.stringify({ name }) });
      setName("");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create category");
    }
  }

  async function onSave(id: string) {
    setError("");
    try {
      await api(`/api/categories/${id}`, { method: "PUT", body: JSON.stringify({ name: editingName }) });
      setEditingId(null);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not update category");
    }
  }

  async function onDelete(id: string) {
    if (!window.confirm("Delete this category?")) return;
    setError("");
    try {
      await api(`/api/categories/${id}`, { method: "DELETE" });
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not delete category");
    }
  }

  return (
    <section>
      <header className="page-header">
        <div>
          <h1>Categories</h1>
          <p className="muted">Defaults are created with each account. Add, rename, or delete your own.</p>
        </div>
      </header>
      {error && <p className="form-error">{error}</p>}
      <form className="card inline-form" onSubmit={onCreate}>
        <label>
          New category
          <input value={name} onChange={(event) => setName(event.target.value)} required />
        </label>
        <button className="button primary" type="submit">
          Add category
        </button>
      </form>
      <ul className="card list">
        {categories.map((category) => (
          <li key={category.id}>
            {editingId === category.id ? (
              <input value={editingName} onChange={(event) => setEditingName(event.target.value)} />
            ) : (
              <span>{category.name}</span>
            )}
            <div className="row-actions">
              {editingId === category.id ? (
                <>
                  <button className="button primary" type="button" onClick={() => onSave(category.id)}>
                    Save
                  </button>
                  <button className="button ghost" type="button" onClick={() => setEditingId(null)}>
                    Cancel
                  </button>
                </>
              ) : (
                <>
                  <button
                    className="button ghost"
                    type="button"
                    onClick={() => {
                      setEditingId(category.id);
                      setEditingName(category.name);
                    }}
                  >
                    Edit
                  </button>
                  <button className="button danger" type="button" onClick={() => onDelete(category.id)}>
                    Delete
                  </button>
                </>
              )}
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
