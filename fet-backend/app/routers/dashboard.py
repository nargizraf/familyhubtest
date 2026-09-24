from fastapi import APIRouter
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from app.budgeting import as_money, budget_status, expense_count
from app.deps import CurrentUser, DbSession
from app.models import Category, Expense
from app.routers.expenses import expense_out
from app.schemas import CategorySpend, DashboardOut

router = APIRouter()


@router.get("", response_model=DashboardOut)
def get_dashboard(db: DbSession, current_user: CurrentUser) -> DashboardOut:
    status = budget_status(db, current_user)
    rows = db.execute(
        select(Category.id, Category.name, func.coalesce(func.sum(Expense.amount), 0))
        .join(Expense, Expense.category_id == Category.id)
        .where(
            Expense.user_id == current_user.id,
            Expense.date >= status.current_start,
            Expense.date <= status.current_end,
            Expense.currency == status.currency,
        )
        .group_by(Category.id, Category.name)
        .order_by(func.sum(Expense.amount).desc(), Category.name.asc())
    ).all()
    recent = db.scalars(
        select(Expense)
        .options(joinedload(Expense.category))
        .where(Expense.user_id == current_user.id)
        .order_by(Expense.date.desc(), Expense.created_at.desc())
        .limit(8)
    ).unique().all()
    count = expense_count(db, current_user.id, status.current_start, status.current_end, status.currency)
    return DashboardOut(
        currency=status.currency,
        month=status.month,
        current_month_spending=status.spent,
        previous_month_spending=status.previous_spent,
        monthly_budget=status.amount,
        remaining_budget=status.remaining,
        over_budget=status.over_budget,
        expense_count=count,
        spending_by_category=[
            CategorySpend(category_id=row[0], category=row[1], total=as_money(row[2])) for row in rows
        ],
        recent_expenses=[expense_out(expense) for expense in recent],
    )
