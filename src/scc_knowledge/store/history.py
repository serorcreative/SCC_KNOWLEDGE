"""Journal d'historique append-only (historisation de la consolidation)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from scc_knowledge.core.clock import Clock, SystemClock
from scc_knowledge.core.errors import StoreError


class HistoryLog:
    """Journal d'événements append-only, persistant en JSONL."""

    def __init__(self, path: Union[str, Path], clock: Optional[Clock] = None):
        self.path = Path(path)
        self.clock = clock or SystemClock()

    def append(self, action: str, entry_id: str, detail: str = "", **extra: Any) -> Dict[str, Any]:
        event = {
            "timestamp": self.clock.now(),
            "action": action,
            "entry_id": entry_id,
            "detail": detail,
        }
        if extra:
            event.update(extra)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.path, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        except OSError as exc:
            raise StoreError(f"Écriture de l'historique impossible ({self.path}) : {exc}") from exc
        return event

    def events(self) -> List[Dict[str, Any]]:
        if not self.path.exists():
            return []
        events: List[Dict[str, Any]] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                events.append(json.loads(line))
        return events

    def events_for(self, entry_id: str) -> List[Dict[str, Any]]:
        return [e for e in self.events() if e.get("entry_id") == entry_id]


__all__ = ["HistoryLog"]
