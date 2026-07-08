"""Models for FANN."""

from __future__ import annotations

from dataclasses import dataclass

from .const import MODEL_ECOTREAT, STATE_OFF, STATE_ON


@dataclass(slots=True)
class FannDevice:
    """Represents a FANN device."""

    dbid: int
    nickname: str
    model: str
    connected: bool
    is_on: bool
    state: str
    raw_status: str
    next_action: str
    people: int | None = None
    schedule: str | None = None

    @property
    def is_sleeping(self) -> bool:
        return self.state == STATE_OFF

    @property
    def is_active(self) -> bool:
        return self.state == STATE_ON

    @property
    def display_name(self) -> str:
        if self.model == MODEL_ECOTREAT:
            return "EkoTreat"
        return self.model or self.nickname