import pytest
from fastapi import HTTPException
from app.domain.workflow import autonomy_tier, transition

def test_transitions_and_autonomy():
    assert transition("triggered", "planned") == "planned"
    with pytest.raises(HTTPException): transition("triggered", "completed")
    assert autonomy_tier(0, True) == "green"
    assert autonomy_tier(90, True) == "yellow"
    assert autonomy_tier(0, False) == "red"
