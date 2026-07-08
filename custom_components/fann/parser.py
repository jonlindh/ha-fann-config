"""Parser for FANN dynamic.jsp."""

from __future__ import annotations

import re
from typing import Any

from bs4 import BeautifulSoup

from .const import (
    MODEL_BIOBED,
    MODEL_ECOTREAT,
    STATE_OFF,
    STATE_ON,
    STATE_SLEEPING,
    STATE_UNKNOWN,
    STATE_WAKING,
)
from .models import FannDevice


def parse_dynamic(html: str) -> list[FannDevice]:
    """Parse HTML returned by dynamic.jsp."""
    soup = BeautifulSoup(html, "html.parser")
    devices: list[FannDevice] = []

    for block in soup.select(".dynamiclistDevice"):
        dbid = _parse_dbid(block)
        nickname = _text(block, ".dynamiclistDeviceNickname")
        connected_text = _text(block, ".dynamiclistDeviceConnect")
        raw_status = _text(block, ".dynamiclistDeviceStatus")
        info = _text(block, ".dynamiclistDeviceInfo")

        attributes = _parse_info_attributes(info)
        next_action = _parse_next_action(block)

        devices.append(
            FannDevice(
                dbid=dbid,
                nickname=nickname,
                model=_parse_model(block),
                connected=connected_text.lower() == "connected",
                is_on=next_action == "zzz",
                state=_parse_state(raw_status, next_action),
                raw_status=raw_status,
                next_action=next_action,
                people=attributes.get("People"),
                schedule=attributes.get("Run schedule"),
            )
        )

    return devices


def _text(block: Any, selector: str) -> str:
    """Return text from selector."""
    element = block.select_one(selector)
    return element.get_text(strip=True) if element else ""


def _parse_dbid(block: Any) -> int:
    """Parse device dbid."""
    element = block.select_one("input[name='dbid']")
    if not element:
        return 0
    return int(element.get("value", 0))


def _parse_model(block: Any) -> str:
    """Parse model from product image."""
    image = block.select_one("#banner_im img")
    src = image.get("src", "") if image else ""

    if "ect.svg" in src:
        return MODEL_ECOTREAT

    if "bb5.svg" in src:
        return MODEL_BIOBED

    return "Unknown"


def _parse_next_action(block: Any) -> str:
    """Parse next action from zzz/wake button."""
    button = block.select_one(".zzzImg")
    onclick = button.get("onclick", "") if button else ""

    if onclick.startswith("wake("):
        return "wake"

    if onclick.startswith("zzz("):
        return "zzz"

    return ""


def _parse_state(raw_status: str, next_action: str) -> str:
    """Translate FANN status to internal state."""
    status = raw_status.lower()

    if "waking up device" in status:
        return STATE_WAKING

    if "putting device to sleep" in status:
        return STATE_SLEEPING

    if "status sleeping" in status:
        return STATE_OFF

    if "status ok" in status:
        return STATE_ON

    if next_action == "wake":
        return STATE_OFF

    if next_action == "zzz":
        return STATE_ON

    return STATE_UNKNOWN


def _parse_info_attributes(info: str) -> dict[str, Any]:
    """Parse dynamic info field into attributes."""
    attributes: dict[str, Any] = {}

    if not info:
        return attributes

    people = re.search(r"People:(\d+)", info)
    if people:
        attributes["People"] = int(people.group(1))

    schedule = re.search(r"Run schedule:(.+)", info)
    if schedule:
        attributes["Run schedule"] = schedule.group(1).strip()

    return attributes