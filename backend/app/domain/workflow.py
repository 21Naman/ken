from fastapi import HTTPException

TRANSITIONS = {"triggered": {"planned", "unclosed"}, "planned": {"awaiting_approval", "approved", "unclosed"}, "awaiting_approval": {"approved", "unclosed"}, "approved": {"cook_briefed", "unclosed"}, "cook_briefed": {"cooking", "unclosed"}, "cooking": {"completed", "recovered", "unclosed"}, "recovered": {"cooking", "unclosed"}}

def transition(current: str, target: str) -> str:
    if target not in TRANSITIONS.get(current, set()):
        raise HTTPException(409, f"Invalid meal-loop transition: {current} → {target}")
    return target

def autonomy_tier(amount: float, inventory_fresh: bool, unusual: bool = False) -> str:
    if not inventory_fresh or unusual or amount > 1000: return "red"
    if amount > 0: return "yellow"
    return "green"

def inventory_is_fresh(updated_at, now, max_age_hours: int = 24) -> bool:
    if updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=now.tzinfo)
    return (now - updated_at).total_seconds() <= max_age_hours * 3600
