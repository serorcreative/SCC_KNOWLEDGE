"""Horloge injectable — temporalité et tests déterministes."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


class Clock:
    """Contrat d'horloge : produit un horodatage ISO-8601."""

    def now(self) -> str:  # pragma: no cover - interface
        raise NotImplementedError


class SystemClock(Clock):
    """Horloge réelle en UTC."""

    def now(self) -> str:
        return datetime.now(timezone.utc).isoformat()


class FixedClock(Clock):
    """Horloge de test : horodatage fixe, éventuellement incrémenté par ``step`` secondes."""

    def __init__(self, value: str = "2026-07-06T00:00:00+00:00", step: int = 0):
        self._base = datetime.fromisoformat(value)
        self._step = step
        self._count = 0

    def now(self) -> str:
        stamp = self._base + timedelta(seconds=self._step * self._count)
        self._count += 1
        return stamp.isoformat()


__all__ = ["Clock", "SystemClock", "FixedClock"]
