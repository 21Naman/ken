from datetime import UTC, date, datetime
from typing import Any, TypeVar

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
import httpx
from pydantic import BaseModel
from sqlmodel import SQLModel, Session, select

from app.database import get_session
from app.models import (
    ApprovalRequest, AuditEvent, Budget, CookProfile, DemoStoreItem, Dish, DishHistory, Household, HouseholdMember, InventoryLot, LocalTask,
    Leftover, MealLoopRecord, PreferenceSignal,
)
from app.providers.ollama import OllamaProvider
from app.providers.whisper import WhisperProvider
from app.providers.vision import VisionProvider
from app.repositories import Repository
from app.schemas import (
    BudgetWrite, CookProfileWrite, DishCreate, HistoryCreate, HouseholdCreate,
    HouseholdUpdate, InventoryCreate, InventoryUpdate, LeftoverCreate, MealLoopCreate,
    LoopStart, MemberCreate, PlanRequest, PreferenceCreate, TransitionRequest, ApprovalDecision, ProposedAction, OutcomeCapture, FeedbackText, CaptureConfirm, CaptureCandidate, CapturePreview,
)
from app.seed import reset_demo_data
from app.services import expiry_status
from app.settings import Settings, get_settings
from app.domain.planner import PlanInput, plan
from app.domain.workflow import autonomy_tier, inventory_is_fresh, transition
from app.scheduler import add_daily_trigger, scheduled_trigger, scheduler_status

router = APIRouter(prefix="/api")
T = TypeVar("T", bound=SQLModel)


class DatabaseHealth(BaseModel):
    status: str


class OllamaHealthResponse(BaseModel):
    status: str
    model: str
    detail: str | None = None


class SchedulerHealthResponse(BaseModel):
    status: str
    detail: str | None = None


class HealthResponse(BaseModel):
    status: str
    database: DatabaseHealth
    ollama: OllamaHealthResponse
    scheduler: SchedulerHealthResponse


class DemoResetResponse(BaseModel):
    status: str
    scenario: str
    recipes: int
    store_items: int
    household_id: int


def _household(session: Session, household_id: int) -> Household:
    return Repository(Household, session).get(household_id)


def _scoped(session: Session, model: type[T], household_id: int, item_id: int) -> T:
    _household(session, household_id)
    item = Repository(model, session).get(item_id)
    if getattr(item, "household_id", None) != household_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Record was not found in this household")
    return item


def _list(session: Session, model: type[T], household_id: int) -> list[T]:
    _household(session, household_id)
    return Repository(model, session).list_for_household(household_id)


def _create(session: Session, model: type[T], household_id: int, values: dict[str, Any]) -> T:
    _household(session, household_id)
    return Repository(model, session).create(model(household_id=household_id, **values))


def _update(session: Session, model: type[T], household_id: int, item_id: int, values: dict[str, Any]) -> T:
    return Repository(model, session).update(_scoped(session, model, household_id, item_id), values)


def _delete(session: Session, model: type[T], household_id: int, item_id: int) -> None:
    item = _scoped(session, model, household_id, item_id)
    session.delete(item)
    session.commit()


def _inventory_view(item: InventoryLot) -> dict[str, Any]:
    return {**item.model_dump(), "expiry_status": expiry_status(item.expiry_date)}


def _leftover_view(item: Leftover) -> dict[str, Any]:
    return {**item.model_dump(), "expiry_status": expiry_status(item.expiry_date)}


@router.get("/health", response_model=HealthResponse)
def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    provider = OllamaProvider(settings.ollama_base_url, settings.ollama_model, settings.request_timeout_seconds)
    ollama = provider.health()
    scheduler_state, scheduler_detail = scheduler_status()
    return HealthResponse(status="ok", database=DatabaseHealth(status="available"), ollama=OllamaHealthResponse(**ollama.__dict__), scheduler=SchedulerHealthResponse(status=scheduler_state, detail=scheduler_detail))


@router.post("/demo/reset", response_model=DemoResetResponse)
def demo_reset(scenario: str = "default", session: Session = Depends(get_session)) -> DemoResetResponse:
    try:
        return DemoResetResponse(status="reset", **reset_demo_data(session, scenario))
    except ValueError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc


@router.get("/households")
def list_households(session: Session = Depends(get_session)) -> list[Household]:
    return list(session.exec(select(Household).order_by(Household.id)))


@router.post("/households", status_code=status.HTTP_201_CREATED)
def create_household(payload: HouseholdCreate, session: Session = Depends(get_session)) -> Household:
    return Repository(Household, session).create(Household(**payload.model_dump()))


@router.get("/households/{household_id}")
def get_household(household_id: int, session: Session = Depends(get_session)) -> Household:
    return _household(session, household_id)


@router.put("/households/{household_id}")
def update_household(household_id: int, payload: HouseholdUpdate, session: Session = Depends(get_session)) -> Household:
    return Repository(Household, session).update(_household(session, household_id), payload.model_dump())


@router.delete("/households/{household_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_household(household_id: int, session: Session = Depends(get_session)) -> None:
    # Phase 2 keeps deletion explicit and removes all owned memory records first.
    _household(session, household_id)
    for model in (HouseholdMember, CookProfile, InventoryLot, Leftover, Dish, DishHistory, Budget, PreferenceSignal, MealLoopRecord):
        for item in _list(session, model, household_id):
            session.delete(item)
    session.delete(_household(session, household_id))
    session.commit()


@router.get("/households/{household_id}/members")
def list_members(household_id: int, session: Session = Depends(get_session)) -> list[HouseholdMember]:
    return _list(session, HouseholdMember, household_id)


@router.post("/households/{household_id}/members", status_code=status.HTTP_201_CREATED)
def create_member(household_id: int, payload: MemberCreate, session: Session = Depends(get_session)) -> HouseholdMember:
    return _create(session, HouseholdMember, household_id, payload.model_dump())


@router.put("/households/{household_id}/members/{item_id}")
def update_member(household_id: int, item_id: int, payload: MemberCreate, session: Session = Depends(get_session)) -> HouseholdMember:
    return _update(session, HouseholdMember, household_id, item_id, payload.model_dump())


@router.delete("/households/{household_id}/members/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(household_id: int, item_id: int, session: Session = Depends(get_session)) -> None:
    _delete(session, HouseholdMember, household_id, item_id)


@router.get("/households/{household_id}/cook-profile")
def get_cook_profile(household_id: int, session: Session = Depends(get_session)) -> CookProfile | None:
    _household(session, household_id)
    return session.exec(select(CookProfile).where(CookProfile.household_id == household_id)).first()


@router.put("/households/{household_id}/cook-profile")
def put_cook_profile(household_id: int, payload: CookProfileWrite, session: Session = Depends(get_session)) -> CookProfile:
    _household(session, household_id)
    item = session.exec(select(CookProfile).where(CookProfile.household_id == household_id)).first()
    if item is None:
        return _create(session, CookProfile, household_id, payload.model_dump())
    return Repository(CookProfile, session).update(item, payload.model_dump())


@router.get("/households/{household_id}/inventory")
def list_inventory(household_id: int, session: Session = Depends(get_session)) -> list[dict[str, Any]]:
    return [_inventory_view(item) for item in _list(session, InventoryLot, household_id)]


@router.post("/households/{household_id}/inventory", status_code=status.HTTP_201_CREATED)
def create_inventory(household_id: int, payload: InventoryCreate, session: Session = Depends(get_session)) -> dict[str, Any]:
    return _inventory_view(_create(session, InventoryLot, household_id, payload.model_dump()))


@router.put("/households/{household_id}/inventory/{item_id}")
def update_inventory(household_id: int, item_id: int, payload: InventoryUpdate, session: Session = Depends(get_session)) -> dict[str, Any]:
    values = {**payload.model_dump(), "updated_at": datetime.now(UTC)}
    return _inventory_view(_update(session, InventoryLot, household_id, item_id, values))


@router.delete("/households/{household_id}/inventory/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inventory(household_id: int, item_id: int, session: Session = Depends(get_session)) -> None:
    _delete(session, InventoryLot, household_id, item_id)


@router.get("/households/{household_id}/leftovers")
def list_leftovers(household_id: int, session: Session = Depends(get_session)) -> list[dict[str, Any]]:
    return [_leftover_view(item) for item in _list(session, Leftover, household_id)]


@router.post("/households/{household_id}/leftovers", status_code=status.HTTP_201_CREATED)
def create_leftover(household_id: int, payload: LeftoverCreate, session: Session = Depends(get_session)) -> dict[str, Any]:
    return _leftover_view(_create(session, Leftover, household_id, payload.model_dump()))


@router.put("/households/{household_id}/leftovers/{item_id}")
def update_leftover(household_id: int, item_id: int, payload: LeftoverCreate, session: Session = Depends(get_session)) -> dict[str, Any]:
    return _leftover_view(_update(session, Leftover, household_id, item_id, payload.model_dump()))


@router.delete("/households/{household_id}/leftovers/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_leftover(household_id: int, item_id: int, session: Session = Depends(get_session)) -> None:
    _delete(session, Leftover, household_id, item_id)


@router.get("/households/{household_id}/dishes")
def list_dishes(household_id: int, session: Session = Depends(get_session)) -> list[Dish]:
    return _list(session, Dish, household_id)


@router.post("/households/{household_id}/dishes", status_code=status.HTTP_201_CREATED)
def create_dish(household_id: int, payload: DishCreate, session: Session = Depends(get_session)) -> Dish:
    return _create(session, Dish, household_id, payload.model_dump())


@router.put("/households/{household_id}/dishes/{item_id}")
def update_dish(household_id: int, item_id: int, payload: DishCreate, session: Session = Depends(get_session)) -> Dish:
    return _update(session, Dish, household_id, item_id, payload.model_dump())


@router.delete("/households/{household_id}/dishes/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dish(household_id: int, item_id: int, session: Session = Depends(get_session)) -> None:
    _delete(session, Dish, household_id, item_id)


@router.get("/households/{household_id}/history")
def list_history(household_id: int, session: Session = Depends(get_session)) -> list[DishHistory]:
    return _list(session, DishHistory, household_id)


@router.post("/households/{household_id}/history", status_code=status.HTTP_201_CREATED)
def create_history(household_id: int, payload: HistoryCreate, session: Session = Depends(get_session)) -> DishHistory:
    return _create(session, DishHistory, household_id, payload.model_dump())


@router.put("/households/{household_id}/history/{item_id}")
def update_history(household_id: int, item_id: int, payload: HistoryCreate, session: Session = Depends(get_session)) -> DishHistory:
    return _update(session, DishHistory, household_id, item_id, payload.model_dump())


@router.delete("/households/{household_id}/history/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_history(household_id: int, item_id: int, session: Session = Depends(get_session)) -> None:
    _delete(session, DishHistory, household_id, item_id)


@router.get("/households/{household_id}/budget")
def get_budget(household_id: int, session: Session = Depends(get_session)) -> Budget | None:
    _household(session, household_id)
    return session.exec(select(Budget).where(Budget.household_id == household_id)).first()


@router.put("/households/{household_id}/budget")
def put_budget(household_id: int, payload: BudgetWrite, session: Session = Depends(get_session)) -> Budget:
    _household(session, household_id)
    item = session.exec(select(Budget).where(Budget.household_id == household_id)).first()
    if item is None:
        return _create(session, Budget, household_id, payload.model_dump())
    return Repository(Budget, session).update(item, payload.model_dump())


@router.get("/households/{household_id}/preferences")
def list_preferences(household_id: int, session: Session = Depends(get_session)) -> list[PreferenceSignal]:
    return _list(session, PreferenceSignal, household_id)


@router.post("/households/{household_id}/preferences", status_code=status.HTTP_201_CREATED)
def create_preference(household_id: int, payload: PreferenceCreate, session: Session = Depends(get_session)) -> PreferenceSignal:
    return _create(session, PreferenceSignal, household_id, payload.model_dump())


@router.put("/households/{household_id}/preferences/{item_id}")
def update_preference(household_id: int, item_id: int, payload: PreferenceCreate, session: Session = Depends(get_session)) -> PreferenceSignal:
    return _update(session, PreferenceSignal, household_id, item_id, payload.model_dump())


@router.delete("/households/{household_id}/preferences/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_preference(household_id: int, item_id: int, session: Session = Depends(get_session)) -> None:
    _delete(session, PreferenceSignal, household_id, item_id)


@router.get("/households/{household_id}/meal-loops")
def list_meal_loops(household_id: int, session: Session = Depends(get_session)) -> list[MealLoopRecord]:
    return _list(session, MealLoopRecord, household_id)


@router.post("/households/{household_id}/meal-loops", status_code=status.HTTP_201_CREATED)
def create_meal_loop(household_id: int, payload: MealLoopCreate, session: Session = Depends(get_session)) -> MealLoopRecord:
    return _create(session, MealLoopRecord, household_id, payload.model_dump())


@router.post("/households/{household_id}/plan")
def create_plan(household_id: int, payload: PlanRequest, session: Session = Depends(get_session)) -> dict[str, Any]:
    """Read-only, repeatable Phase 3 proposal; it never creates a workflow action."""
    _household(session, household_id)
    members = [item.model_dump() for item in _list(session, HouseholdMember, household_id)]
    cook = session.exec(select(CookProfile).where(CookProfile.household_id == household_id)).first()
    budget = session.exec(select(Budget).where(Budget.household_id == household_id)).first()
    dishes = [item.model_dump() for item in _list(session, Dish, household_id)]
    inventory = [item.model_dump(mode="json") for item in _list(session, InventoryLot, household_id)]
    leftovers = [item.model_dump(mode="json") for item in _list(session, Leftover, household_id)]
    history = _list(session, DishHistory, household_id)
    preferences = [item.signal for item in _list(session, PreferenceSignal, household_id)]
    stores = [item.model_dump() for item in session.exec(select(DemoStoreItem))]
    result = plan(dishes, PlanInput(
        servings=payload.servings + payload.guests, available_minutes=payload.available_minutes,
        today=date.today(), inventory=inventory, leftovers=leftovers, members=members,
        cook_skill=cook.skill_level if cook else "beginner",
        budget_remaining=max(0, (budget.monthly_limit - budget.spent_amount - budget.planned_amount) if budget else 0),
        recent_dishes=[item.dish_name for item in history[-5:]], preferences=preferences, stores=stores,
    ))
    return {"context": {"servings": payload.servings + payload.guests, "available_minutes": payload.available_minutes, "urgency": payload.urgency}, **result}

@router.post("/households/{household_id}/loops", status_code=201)
def start_loop(household_id: int, payload: LoopStart, session: Session = Depends(get_session)) -> dict[str, Any]:
    loop = _create(session, MealLoopRecord, household_id, {"trigger_type": payload.trigger_type, "context_note": payload.context_note, "status": "triggered"})
    session.add(AuditEvent(household_id=household_id, meal_loop_id=loop.id, event="triggered", detail=payload.trigger_type)); session.commit()
    return {"id": loop.id, "household_id": loop.household_id, "trigger_type": loop.trigger_type, "status": loop.status}

@router.post("/households/{household_id}/loops/{loop_id}/transition")
def transition_loop(household_id: int, loop_id: int, payload: TransitionRequest, session: Session = Depends(get_session)) -> MealLoopRecord:
    loop = _scoped(session, MealLoopRecord, household_id, loop_id)
    target = transition(loop.status, payload.target_status)
    loop.status = target; session.add(loop); session.add(AuditEvent(household_id=household_id, meal_loop_id=loop_id, event=target, detail="manual local transition")); session.commit(); session.refresh(loop)
    return loop

@router.get("/households/{household_id}/audit")
def audit(household_id: int, session: Session = Depends(get_session)) -> list[AuditEvent]:
    return _list(session, AuditEvent, household_id)

@router.post("/households/{household_id}/loops/{loop_id}/propose", status_code=201)
def propose_action(household_id: int, loop_id: int, payload: ProposedAction, session: Session = Depends(get_session)) -> dict[str, Any]:
    loop = _scoped(session, MealLoopRecord, household_id, loop_id)
    if loop.status != "planned": raise HTTPException(409, "A proposal requires a planned loop")
    inventory = _list(session, InventoryLot, household_id)
    fresh = bool(inventory) and all(inventory_is_fresh(item.updated_at, datetime.now(UTC)) for item in inventory)
    tier = autonomy_tier(payload.amount_inr, fresh, payload.unusual)
    if tier == "green":
        task = _create(session, LocalTask, household_id, {"meal_loop_id": loop_id, "task_type": payload.action, "details": payload.details})
        session.add(AuditEvent(household_id=household_id, meal_loop_id=loop_id, event="local_task_created", detail=payload.action)); session.commit()
        return {"tier": tier, "task_id": task.id, "approval_id": None}
    loop.status = "awaiting_approval"; session.add(loop)
    approval = _create(session, ApprovalRequest, household_id, {"meal_loop_id": loop_id, "tier": tier, "action": payload.action, "amount_inr": payload.amount_inr, "reason": "stale inventory, unusual action, or spending variance"})
    session.add(AuditEvent(household_id=household_id, meal_loop_id=loop_id, event="approval_requested", detail=tier)); session.commit()
    return {"tier": tier, "task_id": None, "approval_id": approval.id}

@router.get("/households/{household_id}/approvals")
def approvals(household_id: int, session: Session = Depends(get_session)) -> list[ApprovalRequest]:
    return _list(session, ApprovalRequest, household_id)

@router.post("/households/{household_id}/approvals/{approval_id}/decision")
def decide_approval(household_id: int, approval_id: int, payload: ApprovalDecision, session: Session = Depends(get_session)) -> ApprovalRequest:
    approval = _scoped(session, ApprovalRequest, household_id, approval_id)
    if approval.status != "pending": raise HTTPException(409, "Approval is already decided")
    loop = _scoped(session, MealLoopRecord, household_id, approval.meal_loop_id)
    approval.status = "approved" if payload.approved else "rejected"
    loop.status = "approved" if payload.approved else "planned"
    session.add(approval); session.add(loop); session.add(AuditEvent(household_id=household_id, meal_loop_id=loop.id, event=approval.status, detail=approval.action)); session.commit(); session.refresh(approval)
    return approval

@router.post("/households/{household_id}/loops/{loop_id}/timeout")
def timeout_loop(household_id: int, loop_id: int, session: Session = Depends(get_session)) -> MealLoopRecord:
    loop = _scoped(session, MealLoopRecord, household_id, loop_id)
    if loop.status in {"completed", "unclosed"}: raise HTTPException(409, "Loop cannot time out")
    loop.status = "unclosed"; session.add(loop); session.add(AuditEvent(household_id=household_id, meal_loop_id=loop_id, event="unclosed", detail="local timeout")); session.commit(); session.refresh(loop)
    return loop

@router.post("/households/{household_id}/scheduled-trigger", status_code=201)
def run_scheduled_trigger(household_id: int, session: Session = Depends(get_session)) -> dict[str, int]:
    _household(session, household_id)
    loop_id = scheduled_trigger(household_id)
    return {"loop_id": loop_id}

@router.put("/households/{household_id}/schedule")
def schedule_daily_trigger(household_id: int, session: Session = Depends(get_session)) -> dict[str, str]:
    _household(session, household_id)
    try:
        add_daily_trigger(household_id)
    except RuntimeError as exc:
        raise HTTPException(503, str(exc)) from exc
    return {"status": "scheduled_local_daily_trigger"}

@router.post("/households/{household_id}/loops/{loop_id}/outcome")
def capture_outcome(household_id: int, loop_id: int, payload: OutcomeCapture, session: Session = Depends(get_session)) -> dict[str, str]:
    loop = _scoped(session, MealLoopRecord, household_id, loop_id)
    if loop.status not in {"cooking", "approved", "cook_briefed"}: raise HTTPException(409, "Outcome requires an active approved loop")
    session.add(DishHistory(household_id=household_id, dish_name=payload.dish_name, rating=payload.rating, feedback=payload.feedback, leftovers_portions=payload.leftovers_portions, accepted=payload.cook_status == "confirmed"))
    if payload.feedback:
        sentiment = "negative" if any(x in payload.feedback.lower() for x in ("heavy", "not again", "bad")) else "positive"
        session.add(PreferenceSignal(household_id=household_id, signal=payload.feedback, sentiment=sentiment, context="meal outcome"))
    if payload.leftovers_portions:
        session.add(Leftover(household_id=household_id, dish_name=payload.dish_name, portions=payload.leftovers_portions))
    for usage in payload.consumed:
        item = session.exec(select(InventoryLot).where(InventoryLot.household_id == household_id, InventoryLot.ingredient == usage["ingredient"])).first()
        if item: item.quantity = max(0, item.quantity - float(usage["quantity"])); session.add(item)
    loop.status = "recovered" if payload.mishap else "completed"
    session.add(loop); session.add(AuditEvent(household_id=household_id, meal_loop_id=loop_id, event=loop.status, detail="outcome captured")); session.commit()
    return {"status": loop.status}

@router.post("/households/{household_id}/cook-brief")
def cook_brief(household_id: int, dish: str, settings: Settings = Depends(get_settings), session: Session = Depends(get_session)) -> dict[str, Any]:
    cook = session.exec(select(CookProfile).where(CookProfile.household_id == household_id)).first()
    language = cook.language if cook else "English"
    provider = OllamaProvider(settings.ollama_base_url, settings.ollama_model, settings.request_timeout_seconds)
    try: return provider.generate_structured(f'Return JSON with one key "brief". Write a short cook brief in {language} for {dish}.')
    except (httpx.HTTPError, ValueError) as exc: raise HTTPException(503, f"Cook brief unavailable; use manual instructions. {exc}")

@router.post("/households/{household_id}/feedback/parse")
def parse_feedback(household_id: int, payload: FeedbackText, settings: Settings = Depends(get_settings), session: Session = Depends(get_session)) -> dict[str, Any]:
    _household(session, household_id)
    provider = OllamaProvider(settings.ollama_base_url, settings.ollama_model, settings.request_timeout_seconds)
    try:
        parsed = provider.generate_structured('Return JSON with keys sentiment and summary for this English/Hindi/Hinglish feedback: ' + payload.text)
        if not isinstance(parsed.get("sentiment"), str): raise ValueError("Missing sentiment")
        return parsed
    except (httpx.HTTPError, ValueError) as exc: raise HTTPException(503, f"Feedback parser unavailable; request manual entry. {exc}")

@router.get("/households/{household_id}/reflection")
def weekly_reflection(household_id: int, session: Session = Depends(get_session)) -> dict[str, Any]:
    history = _list(session, DishHistory, household_id)[-7:]
    signals = _list(session, PreferenceSignal, household_id)[-7:]
    return {"meals_recorded": len(history), "average_rating": round(sum(x.rating for x in history if x.rating) / max(1, len([x for x in history if x.rating])), 1), "recent_feedback": [x.feedback for x in history if x.feedback], "preference_signals": [x.signal for x in signals]}

@router.post("/households/{household_id}/capture/confirm", status_code=201)
def confirm_capture(household_id: int, payload: CaptureConfirm, session: Session = Depends(get_session)) -> dict[str, Any]:
    if not payload.confirmed: raise HTTPException(409, "Capture requires explicit confirmation")
    return _inventory_view(_create(session, InventoryLot, household_id, payload.model_dump()))


def _capture_candidates(payload: dict[str, Any]) -> list[CaptureCandidate]:
    items = payload.get("items")
    if not isinstance(items, list):
        raise ValueError("The local model did not return inventory items")
    candidates: list[CaptureCandidate] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        candidates.append(CaptureCandidate(
            ingredient=str(item.get("ingredient", "")).strip(),
            quantity=float(item.get("estimated_quantity", item.get("quantity", 0))),
            unit=str(item.get("unit", "item")).strip() or "item",
            expiry_date=item.get("expiry_date") or None,
            storage_location=str(item.get("storage_hint", item.get("storage_location", "pantry"))),
            readability_confidence=float(item.get("readability_confidence", item.get("confidence", 0))),
        ))
    return [candidate for candidate in candidates if candidate.ingredient]


def _upload_bytes(upload: UploadFile, allowed_prefix: str) -> bytes:
    if not upload.content_type or not upload.content_type.startswith(allowed_prefix):
        raise HTTPException(415, f"Upload a supported {allowed_prefix} file")
    data = upload.file.read(25 * 1024 * 1024 + 1)
    if not data or len(data) > 25 * 1024 * 1024:
        raise HTTPException(422, "Upload is empty, corrupt, or exceeds 25 MB")
    return data


def _valid_image_bytes(data: bytes) -> bool:
    return data.startswith((b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"P3\n", b"P6\n")) or (data.startswith(b"RIFF") and data[8:12] == b"WEBP")


def _valid_audio_bytes(data: bytes) -> bool:
    """Reject obvious non-audio uploads before an optional local provider sees them."""
    return (
        data.startswith(b"\x1aE\xdf\xa3")  # WebM/Matroska
        or data.startswith(b"OggS")
        or (data.startswith(b"RIFF") and data[8:12] == b"WAVE")
        or data.startswith(b"ID3")
        or (len(data) >= 2 and data[0] == 0xFF and data[1] & 0xF6 == 0xF0)  # AAC/MP3 frame sync
    )


@router.post("/households/{household_id}/capture/audio", response_model=CapturePreview)
async def preview_audio_capture(household_id: int, audio: UploadFile = File(...), settings: Settings = Depends(get_settings), session: Session = Depends(get_session)) -> CapturePreview:
    _household(session, household_id)
    data = _upload_bytes(audio, "audio/")
    if not _valid_audio_bytes(data):
        raise HTTPException(422, "The audio file is corrupt or unsupported")
    try:
        spoken = WhisperProvider(settings.whisper_model).transcribe(data, suffix="." + (audio.filename or "webm").rsplit(".", 1)[-1])
    except (RuntimeError, ValueError) as exc:
        return CapturePreview(source="audio", requires_confirmation=True, fallback=str(exc))
    try:
        parsed = OllamaProvider(settings.ollama_base_url, settings.ollama_model, settings.request_timeout_seconds).generate_structured(
            'Return JSON only with an "items" array. Parse this English/Hindi/Hinglish inventory transcript into ingredient, estimated_quantity, unit, expiry_date, storage_hint, readability_confidence (0 to 1): ' + spoken["transcript"]
        )
        candidates = _capture_candidates(parsed)
    except (httpx.HTTPError, ValueError) as exc:
        return CapturePreview(source="audio", transcript=spoken["transcript"], language=spoken["language"], warning=f"Inventory candidates could not be proposed. Edit the transcript or use typed entry. {exc}")
    return CapturePreview(source="audio", transcript=spoken["transcript"], language=spoken["language"], candidates=candidates)


@router.post("/households/{household_id}/capture/image", response_model=CapturePreview)
def preview_image_capture(household_id: int, image: UploadFile = File(...), settings: Settings = Depends(get_settings), session: Session = Depends(get_session)) -> CapturePreview:
    _household(session, household_id)
    data = _upload_bytes(image, "image/")
    if not _valid_image_bytes(data):
        raise HTTPException(422, "The image file is corrupt or unsupported")
    try:
        extracted = VisionProvider(settings.ollama_base_url, settings.vision_model, settings.vision_request_timeout_seconds).extract_inventory(data)
        return CapturePreview(source="image", candidates=_capture_candidates(extracted))
    except (RuntimeError, ValueError) as exc:
        return CapturePreview(source="image", requires_confirmation=True, fallback=str(exc))
