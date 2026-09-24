import uuid
from datetime import date

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import asc, desc, select
from sqlalchemy.orm import contains_eager, joinedload

from app.deps import CurrentUser, DbSession
from app.models import Category, Expense
from app.schemas import ExpenseCreate, ExpenseOut, ExpenseUpdate, SortField, SortOrder

router = APIRouter()


def expense_out(expense: Expense) -> ExpenseOut:
    return ExpenseOut(
        id=expense.id,
        amount=expense.amount,
        currency=expense.currency,
        description=expense.description,
        category_id=expense.category_id,
        category=expense.category.name,
        date=expense.date,
        created_at=expense.created_at,
        updated_at=expense.updated_at,
        user_id=expense.user_id,
    )


def get_owned_category(db: DbSession, user: CurrentUser, category_id: uuid.UUID) -> Category:
    category = db.scalar(select(Category).where(Category.id == category_id, Category.user_id == user.id))
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


def get_owned_expense(db: DbSession, user: CurrentUser, expense_id: uuid.UUID) -> Expense:
    expense = db.scalar(
        select(Expense)
        .options(joinedload(Expense.category))
        .where(Expense.id == expense_id, Expense.user_id == user.id)
    )
    if expense is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    return expense


@router.get("", response_model=list[ExpenseOut])
def list_expenses(
    db: DbSession,
    current_user: CurrentUser,
    category_id: uuid.UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    q: str | None = None,
    sort: SortField = SortField.date,
    order: SortOrder = SortOrder.desc,
) -> list[ExpenseOut]:
    stmt = (
        select(Expense)
        .join(Expense.category)
        .options(contains_eager(Expense.category))
        .where(Expense.user_id == current_user.id)
    )
    if category_id is not None:
        stmt = stmt.where(Expense.category_id == category_id)
    if date_from is not None:
        stmt = stmt.where(Expense.date >= date_from)
    if date_to is not None:
        stmt = stmt.where(Expense.date <= date_to)
    if q and q.strip():
        escaped = q.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        stmt = stmt.where(Expense.description.ilike(f"%{escaped}%", escape="\\"))

    sort_column = {
        SortField.date: Expense.date,
        SortField.amount: Expense.amount,
        SortField.description: Expense.description,
        SortField.created_at: Expense.created_at,
        SortField.category: Category.name,
    }[sort]
    direction = asc if order == SortOrder.asc else desc
    stmt = stmt.order_by(direction(sort_column), direction(Expense.created_at))
    expenses = db.scalars(stmt).unique().all()
    return [expense_out(expense) for expense in expenses]


@router.post("", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
def create_expense(payload: ExpenseCreate, db: DbSession, current_user: CurrentUser) -> ExpenseOut:
    get_owned_category(db, current_user, payload.category_id)
    expense = Expense(
        user_id=current_user.id,
        category_id=payload.category_id,
        amount=payload.amount,
        currency=payload.currency,
        description=payload.description,
        date=payload.date,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    expense = get_owned_expense(db, current_user, expense.id)
    return expense_out(expense)


@router.get("/{expense_id}", response_model=ExpenseOut)
def get_expense(expense_id: uuid.UUID, db: DbSession, current_user: CurrentUser) -> ExpenseOut:
    return expense_out(get_owned_expense(db, current_user, expense_id))


@router.put("/{expense_id}", response_model=ExpenseOut)
def update_expense(
    expense_id: uuid.UUID,
    payload: ExpenseUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> ExpenseOut:
    expense = get_owned_expense(db, current_user, expense_id)
    get_owned_category(db, current_user, payload.category_id)
    expense.category_id = payload.category_id
    expense.amount = payload.amount
    expense.currency = payload.currency
    expense.description = payload.description
    expense.date = payload.date
    db.commit()
    db.refresh(expense)
    expense = get_owned_expense(db, current_user, expense.id)
    return expense_out(expense)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: uuid.UUID, db: DbSession, current_user: CurrentUser) -> None:
    expense = get_owned_expense(db, current_user, expense_id)
    db.delete(expense)
    db.commit()
