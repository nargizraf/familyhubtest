from sqlalchemy.orm import Session

from app.models import Category

DEFAULT_CATEGORIES = [
    "Food",
    "Rent",
    "Transport",
    "Shopping",
    "Entertainment",
    "Travel",
    "Utilities",
    "Other",
]


def add_default_categories(db: Session, user_id) -> list[Category]:
    categories = [Category(user_id=user_id, name=name) for name in DEFAULT_CATEGORIES]
    db.add_all(categories)
    return categories
