from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, budget, categories, dashboard, expenses

app = FastAPI(title="FamilyHub API", version="1.0.0", description="Family expense tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(expenses.router, prefix="/api/expenses", tags=["expenses"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(budget.router, prefix="/api/budget", tags=["budget"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/health", tags=["health"])
def api_health() -> dict[str, str]:
    return {"status": "ok"}
