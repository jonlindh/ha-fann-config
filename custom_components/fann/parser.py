"""Parser for FANN dynamic.jsp."""

from __future__ import annotations

import re
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


def _parse_state(status: str) -> str:
    """Translate FANN status to internal state."""
    status = status.lower()

    if "status ok" in status:
        return STATE_ON

    if "status sleeping" in status:
        return STATE_OFF

    if "waking up device" in status:
        return STATE_WAKING

    if "putting device to sleep" in status:
        return STATE_SLEEPING

    return STATE_UNKNOWN


def _parse_model(img_src: str) -> str:
    """Return model based on image."""

    if "ect.svg" in img_src:
        return MODEL_ECOTREAT

    if "bb5.svg" in img_src:
        return MODEL_BIOBED

    return "Unknown"


def parse_dynamic(html: str) -> list[FannDevice]:
    """Parse HTML returned by dynamic.jsp."""

    soup = BeautifulSoup(html, "html.parser")

    devices: list[FannDevice] = []

    for device in soup.select(".dynamiclistDevice"):

        image = device.select_one("#banner_im img")
        img_src = image["src"] if image else ""

        nickname = device.select_one(
            ".dynamiclistDeviceNickname"
        ).text.strip()

        connected = (
            device.select_one(".dynamiclistDeviceConnect")
            .text.strip()
            == "Connected"
        )

        status = (
            device.select_one(".dynamiclistDeviceStatus")
            .text.strip()
        )

        info = (
            device.select_one(".dynamiclistDeviceInfo")
            .text.strip()
        )

        dbid = int(
            device.select_one("input[name=dbid]")["value"]
        )

        people = None
        schedule = None

        m = re.search(r"People:(\d+)", info)

        if m:
            people = int(m.group(1))

        m = re.search(r"Run schedule:(.+)", info)

        if m:
            schedule = m.group(1)

        next_action = _parse_next_action(device)

        is_on = _parse_is_on(next_action)

        devices.append(
            FannDevice(
                dbid=dbid,
                nickname=nickname,
                model=_parse_model(img_src),
                connected=connected,
                is_on=is_on,
                state=_parse_state(status),
                raw_status=status,
                next_action=next_action,
                people=people,
                schedule=schedule,
            )
        )

    return devices


def _parse_next_action(device) -> str:

    """Return wake or zzz depending on button."""

    button = device.select_one(".zzzImg")

    if not button:

        return ""

    onclick = button.get("onclick", "")

    if onclick.startswith("wake("):

        return "wake"

    if onclick.startswith("zzz("):

        return "zzz"

    return ""


def _parse_is_on(next_action: str) -> bool:
    """Determine current power state."""

    return next_action == "zzz"