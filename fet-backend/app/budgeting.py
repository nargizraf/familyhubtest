from calendar import monthrange
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Budget, Expense, User

ZERO = Decimal("0.00")
TWOPLACES = Decimal("0.01")


def as_money(value: Decimal | int | float) -> Decimal:
    return Decimal(str(value)).quantize(TWOPLACES)


def month_bounds(anchor: date) -> tuple[date, date]:
    last_day = monthrange(anchor.year, anchor.month)[1]
    return anchor.replace(day=1), anchor.replace(day=last_day)


def previous_month_bounds(anchor: date) -> tuple[date, date]:
    current_start, _ = month_bounds(anchor)
    previous_day = current_start - timedelta(days=1)
    return month_bounds(previous_day)


def month_key(anchor: date) -> str:
    return f"{anchor.year:04d}-{anchor.month:02d}"


def total_spent(db: Session, user_id, start: date, end: date, currency: str) -> Decimal:
    total = db.scalar(
        select(func.coalesce(func.sum(Expense.amount), 0)).where(
            Expense.user_id == user_id,
            Expense.date >= start,
            Expense.date <= end,
            Expense.currency == currency,
        )
    )
    return as_money(total or 0)


def expense_count(db: Session, user_id, start: date, end: date, currency: str) -> int:
    total = db.scalar(
        select(func.count())
        .select_from(Expense)
        .where(
            Expense.user_id == user_id,
            Expense.date >= start,
            Expense.date <= end,
            Expense.currency == currency,
        )
    )
    return int(total or 0)


@dataclass
class BudgetStatus:
    amount: Decimal | None
    currency: str
    month: str
    spent: Decimal
    remaining: Decimal | None
    over_budget: bool
    current_start: date
    current_end: date
    previous_spent: Decimal


def budget_status(db: Session, user: User, today: date | None = None) -> BudgetStatus:
    today = today or date.today()
    current_start, current_end = month_bounds(today)
    previous_start, previous_end = previous_month_bounds(today)
    budget = db.scalar(select(Budget).where(Budget.user_id == user.id))
    currency = budget.currency if budget else "PLN"
    spent = total_spent(db, user.id, current_start, current_end, currency)
    previous = total_spent(db, user.id, previous_start, previous_end, currency)
    amount = as_money(budget.amount) if budget else None
    remaining = as_money(amount - spent) if amount is not None else None
    over_budget = amount is not None and spent > amount
    return BudgetStatus(
        amount=amount,
        currency=currency,
        month=month_key(today),
        spent=spent,
        remaining=remaining,
        over_budget=over_budget,
        current_start=current_start,
        current_end=current_end,
        previous_spent=previous,
    )
