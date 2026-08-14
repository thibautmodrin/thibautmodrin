"""Grille calendrier (semaine commençant le lundi)."""

from __future__ import annotations

from calendar import Calendar, monthrange
from datetime import date


WEEKDAYS = ("Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim")
MONTHS = (
    "",
    "janvier",
    "février",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "août",
    "septembre",
    "octobre",
    "novembre",
    "décembre",
)


def month_weeks(year: int, month: int) -> list[list[date | None]]:
    cal = Calendar(firstweekday=0)
    weeks: list[list[date | None]] = []
    for week in cal.monthdatescalendar(year, month):
        weeks.append([d if d.month == month else None for d in week])
    return weeks


def shift_month(year: int, month: int, delta: int) -> tuple[int, int]:
    total = year * 12 + (month - 1) + delta
    return total // 12, total % 12 + 1


def month_label(year: int, month: int) -> str:
    return f"{MONTHS[month]} {year}"


def last_day(year: int, month: int) -> int:
    return monthrange(year, month)[1]
