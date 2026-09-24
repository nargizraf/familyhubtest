import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.deps import CurrentUser, DbSession
from app.models import Category, Expense, User
from app.schemas import CategoryCreate, CategoryOut, CategoryUpdate

router = APIRouter()


def _get_category(db: DbSession, user: User, category_id: uuid.UUID) -> Category:
    category = db.scalar(select(Category).where(Category.id == category_id, Category.user_id == user.id))
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.get("", response_model=list[CategoryOut])
def list_categories(db: DbSession, current_user: CurrentUser) -> list[Category]:
    return list(
        db.scalars(select(Category).where(Category.user_id == current_user.id).order_by(Category.name.asc())).all()
    )


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: DbSession, current_user: CurrentUser) -> Category:
    existing = db.scalar(
        select(Category).where(
            Category.user_id == current_user.id,
            func.lower(Category.name) == payload.name.lower(),
        )
    )
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists")
    category = Category(user_id=current_user.id, name=payload.name)
    db.add(category)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists") from None
    db.refresh(category)
    return category


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: uuid.UUID,
    payload: CategoryUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> Category:
    category = _get_category(db, current_user, category_id)
    duplicate = db.scalar(
        select(Category).where(
            Category.user_id == current_user.id,
            func.lower(Category.name) == payload.name.lower(),
            Category.id != category.id,
        )
    )
    if duplicate is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists")
    category.name = payload.name
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists") from None
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: uuid.UUID, db: DbSession, current_user: CurrentUser) -> None:
    category = _get_category(db, current_user, category_id)
    in_use = db.scalar(select(Expense.id).where(Expense.category_id == category.id).limit(1))
    if in_use is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category is used by expenses and cannot be deleted",
        )
    db.delete(category)
    db.commit()
