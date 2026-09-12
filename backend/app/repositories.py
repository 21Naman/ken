"""Small SQLModel repositories used by Phase 2's CRUD routes."""

from typing import Any, Generic, TypeVar

from fastapi import HTTPException, status
from sqlmodel import SQLModel, Session, select

T = TypeVar("T", bound=SQLModel)


class Repository(Generic[T]):
    def __init__(self, model: type[T], session: Session) -> None:
        self.model = model
        self.session = session

    def get(self, item_id: int) -> T:
        item = self.session.get(self.model, item_id)
        if item is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"{self.model.__name__} {item_id} was not found")
        return item

    def list_for_household(self, household_id: int) -> list[T]:
        return list(self.session.exec(select(self.model).where(self.model.household_id == household_id)))  # type: ignore[attr-defined]

    def create(self, item: T) -> T:
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def update(self, item: T, values: dict[str, Any]) -> T:
        item.sqlmodel_update(values)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def delete(self, item_id: int) -> None:
        self.session.delete(self.get(item_id))
        self.session.commit()
