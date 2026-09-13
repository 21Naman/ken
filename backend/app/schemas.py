from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class HouseholdCreate(APIModel):
    name: str = Field(min_length=1, max_length=120)
    default_language: str = "English"


class HouseholdUpdate(HouseholdCreate):
    pass


class MemberCreate(APIModel):
    name: str = Field(min_length=1, max_length=120)
    language: str = "English"
    dietary_preferences: list[str] = []
    allergies: list[str] = []
    health_constraints: list[str] = []
    likes: list[str] = []
    dislikes: list[str] = []


class CalendarSelection(APIModel):
    calendar_id: str = Field(min_length=1, max_length=512)
    calendar_name: str = Field(min_length=1, max_length=255)


class CookBriefRequest(APIModel):
    plan_date: date = Field(default_factory=date.today)


class CookProfileWrite(APIModel):
    name: str = "Cook"
    language: str = "Hindi"
    skill_level: str = "intermediate"
    available_hours: list[str] = []
    confident_dishes: list[str] = []


class InventoryCreate(APIModel):
    ingredient: str = Field(min_length=1, max_length=120)
    quantity: float = Field(ge=0)
    unit: str = Field(min_length=1, max_length=32)
    purchased_on: date | None = None
    expiry_date: date | None = None
    freshness: str = "fresh"
    storage_location: str = "pantry"
    confirmed: bool = False


class InventoryUpdate(InventoryCreate):
    pass


class LeftoverCreate(APIModel):
    dish_name: str = Field(min_length=1, max_length=120)
    portions: float = Field(ge=0)
    stored_on: date = Field(default_factory=date.today)
    expiry_date: date | None = None
    storage_location: str = "fridge"
    reuse_suggestions: list[str] = []


class DishCreate(APIModel):
    name: str = Field(min_length=1, max_length=120)
    ingredients: list[dict[str, Any]] = []
    prep_minutes: int = Field(default=0, ge=0)
    servings: int = Field(default=1, ge=1)
    nutrition_notes: list[str] = []
    tags: list[str] = []
    cook_skill_required: str = "intermediate"


class DiscoveryApprovalRequest(APIModel):
    name: str = Field(min_length=1, max_length=120)
    ingredients: list[dict[str, Any]] = []
    servings: int = Field(default=2, ge=1)


class ZeptoCartRequest(APIModel):
    dish_name: str = Field(min_length=1, max_length=120)
    missing_ingredients: list[dict[str, Any]] = Field(min_length=1)


class ZeptoSyncRequest(APIModel):
    items_added: list[dict[str, Any]] = Field(min_length=1)


class HistoryCreate(APIModel):
    dish_id: int | None = None
    dish_name: str = Field(min_length=1, max_length=120)
    served_on: date = Field(default_factory=date.today)
    accepted: bool | None = None
    rating: int | None = Field(default=None, ge=1, le=5)
    feedback: str | None = None
    leftovers_portions: float = Field(default=0, ge=0)
    cook_modifications: str | None = None


class BudgetWrite(APIModel):
    monthly_limit: float = Field(ge=0)
    spent_amount: float = Field(default=0, ge=0)
    planned_amount: float = Field(default=0, ge=0)
    category_allocations: dict[str, float] = {}


class PreferenceCreate(APIModel):
    member_id: int | None = None
    signal: str = Field(min_length=1, max_length=1000)
    sentiment: str = "neutral"
    context: str | None = None
    confidence: float = Field(default=1, ge=0, le=1)
    expires_on: date | None = None


class MealLoopCreate(APIModel):
    trigger_type: str = "manual"
    context_note: str | None = None
    status: str = "recorded"


class PlanRequest(APIModel):
    servings: int = Field(default=2, ge=1, le=20)
    available_minutes: int = Field(default=45, ge=1, le=360)
    guests: int = Field(default=0, ge=0, le=18)
    urgency: str = "routine"

class LoopStart(APIModel):
    trigger_type: str = "manual"
    context_note: str | None = None

class TransitionRequest(APIModel):
    target_status: str

class ApprovalDecision(APIModel):
    approved: bool

class ProposedAction(APIModel):
    action: str
    amount_inr: float = Field(default=0, ge=0)
    unusual: bool = False
    details: str = ""

class OutcomeCapture(APIModel):
    dish_name: str
    rating: int | None = Field(default=None, ge=1, le=5)
    feedback: str = ""
    leftovers_portions: float = Field(default=0, ge=0)
    consumed: list[dict[str, float | str]] = []
    cook_status: str = "confirmed"
    mishap: bool = False

class FeedbackText(APIModel):
    text: str = Field(min_length=1, max_length=1000)

class CaptureConfirm(APIModel):
    ingredient: str
    quantity: float = Field(ge=0)
    unit: str
    expiry_date: date | None = None
    freshness: str = "fresh"
    storage_location: str = "pantry"
    confirmed: bool = False


class CaptureCandidate(APIModel):
    ingredient: str
    quantity: float = Field(ge=0)
    unit: str
    expiry_date: date | None = None
    freshness: str = "fresh"
    storage_location: str = "pantry"
    readability_confidence: float = Field(ge=0, le=1)


class CapturePreview(APIModel):
    source: str
    transcript: str | None = None
    language: str | None = None
    candidates: list[CaptureCandidate] = []
    requires_confirmation: bool = True
    fallback: str | None = None
    warning: str | None = None
