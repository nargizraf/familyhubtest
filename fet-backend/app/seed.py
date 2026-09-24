"""Create the demo user, categories, expenses, and monthly budget.

The seed is idempotent: if the demo user already exists, it leaves the database unchanged.
"""

from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.budgeting import month_bounds
from app.config import settings
from app.database import SessionLocal
from app.defaults import DEFAULT_CATEGORIES, add_default_categories
from app.models import Budget, Expense, User
from app.security import hash_password


def _day(month_start: date, day_number: int) -> date:
    last_day = monthrange(month_start.year, month_start.month)[1]
    return month_start.replace(day=min(day_number, last_day))


def seed_demo(db: Session) -> bool:
    """Insert demo data. Returns False when the demo user already exists."""
    email = settings.demo_user_email.lower()
    existing = db.scalar(select(User).where(func.lower(User.email) == email))
    if existing is not None:
        return False

    user = User(
        email=email,
        full_name=settings.demo_user_name,
        password_hash=hash_password(settings.demo_user_password),
    )
    db.add(user)
    db.flush()
    categories = {category.name: category for category in add_default_categories(db, user.id)}
    db.flush()

    today = date.today()
    current_start, _ = month_bounds(today)
    previous_end = current_start - timedelta(days=1)
    previous_start, _ = month_bounds(previous_end)

    samples = [
        (current_start, 2, "Groceries", "Food", "54.20"),
        (current_start, 3, "Bakery", "Food", "12.40"),
        (current_start, 5, "Monthly metro card", "Transport", "49.00"),
        (current_start, 6, "Household supplies", "Shopping", "28.40"),
        (current_start, 8, "Cinema", "Entertainment", "18.00"),
        (current_start, 11, "Electricity", "Utilities", "76.30"),
        (current_start, 14, "Pharmacy", "Other", "15.90"),
        (current_start, 18, "Dinner out", "Food", "42.50"),
        (current_start, 20, "Weekend train", "Travel", "37.00"),
        (previous_start, 1, "Rent", "Rent", "980.00"),
        (previous_start, 4, "Groceries", "Food", "120.15"),
        (previous_start, 9, "Bus tickets", "Transport", "32.00"),
        (previous_start, 16, "New shoes", "Shopping", "75.00"),
        (previous_start, 22, "Museum tickets", "Entertainment", "24.00"),
    ]
    for month_start, day_number, description, category_name, amount in samples:
        db.add(
            Expense(
                user_id=user.id,
                category_id=categories[category_name].id,
                amount=Decimal(amount),
                currency="PLN",
                description=description,
                date=_day(month_start, day_number),
            )
        )

    db.add(Budget(user_id=user.id, amount=Decimal("250.00"), currency="PLN"))
    db.commit()
    return True


def seed() -> None:
    db = SessionLocal()
    try:
        created = seed_demo(db)
    finally:
        db.close()
    if created:
        print(f"Seeded demo user {settings.demo_user_email} with {len(DEFAULT_CATEGORIES)} categories.")
    else:
        print(f"Demo user {settings.demo_user_email} already exists; skipping seed.")


if __name__ == "__main__":
    seed()
