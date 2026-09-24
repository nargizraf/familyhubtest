from fastapi import APIRouter
from sqlalchemy import select

from app.budgeting import budget_status
from app.deps import CurrentUser, DbSession
from app.models import Budget
from app.schemas import BudgetOut, BudgetUpdate

router = APIRouter()


def _to_out(status) -> BudgetOut:
    return BudgetOut(
        amount=status.amount,
        currency=status.currency,
        month=status.month,
        spent=status.spent,
        remaining=status.remaining,
        over_budget=status.over_budget,
    )


@router.get("", response_model=BudgetOut)
def get_budget(db: DbSession, current_user: CurrentUser) -> BudgetOut:
    return _to_out(budget_status(db, current_user))


@router.put("", response_model=BudgetOut)
def update_budget(payload: BudgetUpdate, db: DbSession, current_user: CurrentUser) -> BudgetOut:
    budget = db.scalar(select(Budget).where(Budget.user_id == current_user.id))
    if budget is None:
        budget = Budget(user_id=current_user.id, amount=payload.amount, currency=payload.currency)
        db.add(budget)
    else:
        budget.amount = payload.amount
        budget.currency = payload.currency
    db.commit()
    return _to_out(budget_status(db, current_user))
