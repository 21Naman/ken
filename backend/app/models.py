"""Persistent Phase 1 fixtures and Phase 2 household-memory entities."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

UTC = timezone.utc

from sqlalchemy import Column, JSON, UniqueConstraint
from sqlmodel import Field, SQLModel


class DemoRecipe(SQLModel, table=True):
    __tablename__ = "demo_recipes"
    __table_args__ = (UniqueConstraint("slug", name="uq_demo_recipe_slug"),)
    id: int | None = Field(default=None, primary_key=True)
    slug: str = Field(index=True)
    name: str
    ingredients: list[dict[str, Any]] = Field(sa_column=Column(JSON), default_factory=list)


class DemoStoreItem(SQLModel, table=True):
    __tablename__ = "demo_store_items"
    __table_args__ = (UniqueConstraint("store_name", "ingredient", name="uq_demo_store_ingredient"),)
    id: int | None = Field(default=None, primary_key=True)
    store_name: str
    ingredient: str = Field(index=True)
    unit: str
    price_inr: float


class Household(SQLModel, table=True):
    __tablename__ = "households"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, min_length=1, max_length=120)
    default_language: str = Field(default="English", max_length=32)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class HouseholdMember(SQLModel, table=True):
    __tablename__ = "household_members"
    id: int | None = Field(default=None, primary_key=True)
    household_id: int = Field(foreign_key="households.id", index=True)
    name: str = Field(min_length=1, max_length=120)
    language: str = Field(default="English", max_length=32)
    dietary_preferences: list[str] = Field(sa_column=Column(JSON), default_factory=list)
    allergies: list[str] = Field(sa_column=Column(JSON), default_factory=list)
    health_constraints: list[str] = Field(sa_column=Column(JSON), default_factory=list)
    likes: list[str] = Field(sa_column=Column(JSON), default_factory=list)
    dislikes: list[str] = Field(sa_column=Column(JSON), default_factory=list)


class GoogleCalendarConnection(SQLModel, table=True):
    """One consented Google Calendar connection per household member."""
    __tablename__ = "google_calendar_connections"
    __table_args__ = (UniqueConstraint("member_id", name="uq_google_calendar_member"),)
    id: int | None = Field(default=None, primary_key=True)
    household_id: int = Field(foreign_key="households.id", index=True)
    member_id: int = Field(foreign_key="household_members.id", index=True)
    google_subject: str = Field(index=True, max_length=255)
    google_email: str = Field(max_length=320)
    encrypted_refresh_token: str
    calendar_id: str | None = Field(default=None, max_length=512)
    calendar_name: str | None = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class GoogleOAuthState(SQLModel, table=True):
    """Short-lived, single-use OAuth state bound to a member."""
    __tablename__ = "google_oauth_states"
    state: str = Field(primary_key=True, max_length=128)
    household_id: int = Field(foreign_key="households.id", index=True)
    member_id: int = Field(foreign_key="household_members.id", index=True)
    expires_at: datetime


class ZeptoConnection(SQLModel, table=True):
    """One encrypted Zepto OAuth token per household."""
    __tablename__ = "zepto_connections"
    __table_args__ = (UniqueConstraint("household_id", name="uq_zepto_household"),)
    id: int | None = Field(default=None, primary_key=True)
    household_id: int = Field(foreign_key="households.id", index=True)
    encrypted_access_token: str
    phone_number: str | None = Field(default=None, max_length=32)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ZeptoOAuthState(SQLModel, table=True):
    """Short-lived PKCE state for a household's Zepto connection."""
    __tablename__ = "zepto_oauth_states"
    state: str = Field(primary_key=True, max_length=128)
    household_id: int = Field(foreign_key="households.id", index=True)
    code_verifier: str = Field(max_length=256)
    expires_at: datetime


class CookProfile(SQLModel, table=True):
    __tablename__ = "cook_profiles"
    __table_args__ = (UniqueConstraint("household_id", name="uq_cook_profile_household"),)
    id: int | None = Field(default=None, primary_key=True)
    household_id: int = Field(foreign_key="households.id", index=True)
    name: str = Field(default="Cook", max_length=120)
    language: str = Field(default="Hindi", max_length=32)
    skill_level: str = Field(default="intermediate", max_length=32)
    available_hours: list[str] = Field(sa_column=Column(JSON), default_factory=list)
    confident_dishes: list[str] = Field(sa_column=Column(JSON), default_factory=list)


class InventoryLot(SQLModel, table=True):
    __tablename__ = "inventory_lots"
    id: int | None = Field(default=None, primary_key=True)
    household_id: int = Field(foreign_key="households.id", index=True)
    ingredient: str = Field(index=True, min_length=1, max_length=120)
    quantity: float = Field(ge=0)
    unit: str = Field(min_length=1, max_length=32)
    purchased_on: date | None = None
    expiry_date: date | None = Field(default=None, index=True)
    freshness: str = Field(default="fresh", max_length=32)
    storage_location: str = Field(default="pantry", max_length=32)
    confirmed: bool = False
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Leftover(SQLModel, table=True):
    __tablename__ = "leftovers"
    id: int | None = Field(default=None, primary_key=True)
    household_id: int = Field(foreign_key="households.id", index=True)
    dish_name: str = Field(min_length=1, max_length=120)
    portions: float = Field(ge=0)
    stored_on: date = Field(default_factory=date.today)
    expiry_date: date | None = Field(default=None, index=True)
    storage_location: str = Field(default="fridge", max_length=32)
    reuse_suggestions: list[str] = Field(sa_column=Column(JSON), default_factory=list)


class Dish(SQLModel, table=True):
    __tablename__ = "dishes"
    id: int | None = Field(default=None, primary_key=True)
    household_id: int | None = Field(default=None, foreign_key="households.id", index=True)
    name: str = Field(index=True, min_length=1, max_length=120)
    ingredients: list[dict[str, Any]] = Field(sa_column=Column(JSON), default_factory=list)
    prep_minutes: int = Field(default=0, ge=0)
    servings: int = Field(default=1, ge=1)
    nutrition_notes: list[str] = Field(sa_column=Column(JSON), default_factory=list)
    tags: list[str] = Field(sa_column=Column(JSON), default_factory=list)
    cook_skill_required: str = Field(default="intermediate", max_length=32)


class DishHistory(SQLModel, table=True):
    __tablename__ = "dish_history"
    id: int | None = Field(default=None, primary_key=True)
    household_id: int = Field(foreign_key="households.id", index=True)
    dish_id: int | None = Field(default=None, foreign_key="dishes.id", index=True)
    dish_name: str = Field(min_length=1, max_length=120)
    served_on: date = Field(default_factory=date.today, index=True)
    accepted: bool | None = None
    rating: int | None = Field(default=None, ge=1, le=5)
    feedback: str | None = Field(default=None, max_length=1000)
    leftovers_portions: float = Field(default=0, ge=0)
    cook_modifications: str | None = Field(default=None, max_length=1000)


class Budget(SQLModel, table=True):
    __tablename__ = "budgets"
    __table_args__ = (UniqueConstraint("household_id", name="uq_budget_household"),)
    id: int | None = Field(default=None, primary_key=True)
    household_id: int = Field(foreign_key="households.id", index=True)
    monthly_limit: float = Field(ge=0)
    spent_amount: float = Field(default=0, ge=0)
    planned_amount: float = Field(default=0, ge=0)
    category_allocations: dict[str, float] = Field(sa_column=Column(JSON), default_factory=dict)


class PreferenceSignal(SQLModel, table=True):
    __tablename__ = "preference_signals"
    id: int | None = Field(default=None, primary_key=True)
    household_id: int = Field(foreign_key="households.id", index=True)
    member_id: int | None = Field(default=None, foreign_key="household_members.id", index=True)
    signal: str = Field(min_length=1, max_length=1000)
    sentiment: str = Field(default="neutral", max_length=32)
    context: str | None = Field(default=None, max_length=1000)
    confidence: float = Field(default=1.0, ge=0, le=1)
    expires_on: date | None = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class MealLoopRecord(SQLModel, table=True):
    """Passive history only; workflow transitions are a later phase."""
    __tablename__ = "meal_loop_records"
    id: int | None = Field(default=None, primary_key=True)
    household_id: int = Field(foreign_key="households.id", index=True)
    trigger_type: str = Field(default="manual", max_length=32)
    context_note: str | None = Field(default=None, max_length=1000)
    status: str = Field(default="recorded", max_length=32)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ApprovalRequest(SQLModel, table=True):
    __tablename__ = "approval_requests"
    id: int | None = Field(default=None, primary_key=True)
    household_id: int = Field(foreign_key="households.id", index=True)
    meal_loop_id: int = Field(foreign_key="meal_loop_records.id", index=True)
    tier: str
    action: str
    amount_inr: float = 0
    status: str = "pending"
    reason: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class LocalTask(SQLModel, table=True):
    __tablename__ = "local_tasks"
    id: int | None = Field(default=None, primary_key=True)
    household_id: int = Field(foreign_key="households.id", index=True)
    meal_loop_id: int = Field(foreign_key="meal_loop_records.id", index=True)
    task_type: str
    status: str = "pending"
    details: str


class AuditEvent(SQLModel, table=True):
    __tablename__ = "audit_events"
    id: int | None = Field(default=None, primary_key=True)
    household_id: int = Field(foreign_key="households.id", index=True)
    meal_loop_id: int = Field(foreign_key="meal_loop_records.id", index=True)
    event: str
    detail: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
