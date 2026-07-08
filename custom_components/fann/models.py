from dataclasses import dataclass


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