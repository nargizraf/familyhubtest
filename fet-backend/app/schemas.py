import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def _normalize_currency(value: str) -> str:
    currency = value.strip().upper()
    if len(currency) != 3 or not currency.isalpha():
        raise ValueError("Currency must be a 3-letter code")
    return currency


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str
    created_at: datetime


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    full_name: str = Field(min_length=1, max_length=255)

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, value: EmailStr) -> str:
        return value.lower()

    @field_validator("full_name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if not cleaned:
            raise ValueError("Name is required")
        return cleaned


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, value: EmailStr) -> str:
        return value.lower()


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if not cleaned:
            raise ValueError("Category name is required")
        return cleaned


class CategoryUpdate(CategoryCreate):
    pass


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ExpenseCreate(BaseModel):
    amount: Decimal = Field(gt=0, le=Decimal("9999999999.99"))
    currency: str = "PLN"
    description: str = Field(min_length=1, max_length=500)
    category_id: uuid.UUID
    date: date

    @field_validator("currency")
    @classmethod
    def check_currency(cls, value: str) -> str:
        return _normalize_currency(value)

    @field_validator("description")
    @classmethod
    def strip_description(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if not cleaned:
            raise ValueError("Description is required")
        return cleaned

    @field_validator("amount")
    @classmethod
    def quantize_amount(cls, value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"))


class ExpenseUpdate(ExpenseCreate):
    pass


class ExpenseOut(BaseModel):
    id: uuid.UUID
    amount: Decimal
    currency: str
    description: str
    category_id: uuid.UUID
    category: str
    date: date
    created_at: datetime
    updated_at: datetime
    user_id: uuid.UUID


class SortField(str, Enum):
    date = "date"
    amount = "amount"
    description = "description"
    created_at = "created_at"
    category = "category"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class BudgetUpdate(BaseModel):
    amount: Decimal = Field(gt=0, le=Decimal("9999999999.99"))
    currency: str = "PLN"

    @field_validator("currency")
    @classmethod
    def check_currency(cls, value: str) -> str:
        return _normalize_currency(value)

    @field_validator("amount")
    @classmethod
    def quantize_amount(cls, value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"))


class BudgetOut(BaseModel):
    amount: Decimal | None
    currency: str
    month: str
    spent: Decimal
    remaining: Decimal | None
    over_budget: bool


class CategorySpend(BaseModel):
    category_id: uuid.UUID
    category: str
    total: Decimal


class DashboardOut(BaseModel):
    currency: str
    month: str
    current_month_spending: Decimal
    previous_month_spending: Decimal
    monthly_budget: Decimal | None
    remaining_budget: Decimal | None
    over_budget: bool
    expense_count: int
    spending_by_category: list[CategorySpend]
    recent_expenses: list[ExpenseOut]
