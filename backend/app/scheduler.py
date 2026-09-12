from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import Session
from app.database import engine
from app.models import AuditEvent, LocalTask, MealLoopRecord

scheduler = BackgroundScheduler()
_scheduler_error: str | None = None


def scheduler_status() -> tuple[str, str | None]:
    if scheduler.running:
        return "available", None
    return "unavailable", _scheduler_error or "Automatic local triggers are unavailable; use the manual trigger instead."

def start_scheduler() -> None:
    global _scheduler_error
    if scheduler.running:
        return
    try:
        scheduler.start()
        _scheduler_error = None
    except Exception as exc:
        _scheduler_error = str(exc)

def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)

def scheduled_trigger(household_id: int) -> int:
    with Session(engine) as session:
        loop = MealLoopRecord(household_id=household_id, trigger_type="scheduled", status="triggered")
        session.add(loop); session.commit(); session.refresh(loop)
        session.add(LocalTask(household_id=household_id, meal_loop_id=loop.id, task_type="daily_meal_check", details="Scheduled local planning reminder"))
        session.add(AuditEvent(household_id=household_id, meal_loop_id=loop.id, event="scheduled_trigger", detail="local task created")); session.commit()
        return loop.id

def add_daily_trigger(household_id: int, hour: int = 9) -> None:
    if not scheduler.running:
        raise RuntimeError(scheduler_status()[1])
    try:
        scheduler.add_job(scheduled_trigger, "cron", args=[household_id], hour=hour, id=f"daily-{household_id}", replace_existing=True)
    except Exception as exc:
        raise RuntimeError(f"Automatic local triggers are unavailable; use the manual trigger instead. {exc}") from exc
