"""Models for FANN."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

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
    attributes: dict[str, Any] = field(default_factory=dict)

    @property
    def people(self) -> int | None:
        return self.attributes.get("People")

    @property
    def schedule(self) -> str | None:
        return self.attributes.get("Run schedule")

    @property
    def is_sleeping(self) -> bool:
        return self.state == STATE_OFF

    @property
    def is_active(self) -> bool:
        return self.state == STATE_ON

    @property
    def transition(self) -> str | None:
        if self.state == "waking":
            return "starting"
        if self.state == "sleeping":
            return "stopping"
        return None

    @property
    def status_display(self) -> str:
        if self.state == "on":
            return "Running"
        if self.state == "off":
            return "Sleeping"
        if self.state == "waking":
            return "Starting"
        if self.state == "sleeping":
            return "Stopping"
        return self.raw_status

    @property
    def display_name(self) -> str:
        if self.model == MODEL_ECOTREAT:
            return "EkoTreat"
        return self.model or self.nickname