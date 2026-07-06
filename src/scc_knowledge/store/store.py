"""Base de connaissance persistante (fichier JSON, sans dépendance).

Charge/sauvegarde les :class:`KnowledgeEntry` dans un fichier JSON
(``id -> entrée``) et maintient deux index :

* ``(domain, canonical_key) -> id`` pour la canonisation ;
* ``memory_id -> id`` pour résoudre les liens mémoire en relations de connaissance.

Interface volontairement simple : remplaçable (SQLite, base vectorielle) sans
toucher au reste du moteur.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from scc_knowledge.core.errors import NotFoundError, StoreError
from scc_knowledge.core.models import KnowledgeEntry


class KnowledgeStore:
    """Collection persistante d'entrées de connaissance."""

    def __init__(self, path: Union[str, Path]):
        self.path = Path(path)
        self._entries: Dict[str, KnowledgeEntry] = {}
        self._canonical_index: Dict[Tuple[str, str], str] = {}
        self._memory_index: Dict[str, str] = {}
        self.load()

    # -- Persistance -----------------------------------------------------------

    def load(self) -> None:
        self._entries = {}
        self._canonical_index = {}
        self._memory_index = {}
        if not self.path.exists():
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise StoreError(f"Base illisible ({self.path}) : {exc}") from exc
        for entry_id, data in raw.items():
            entry = KnowledgeEntry.from_dict(data)
            self._entries[entry_id] = entry
            self._reindex(entry)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {eid: e.to_dict() for eid, e in self._entries.items()}
        try:
            self.path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        except OSError as exc:
            raise StoreError(f"Écriture de la base impossible ({self.path}) : {exc}") from exc

    # -- Index -----------------------------------------------------------------

    def _reindex(self, entry: KnowledgeEntry) -> None:
        if entry.canonical_key:
            self._canonical_index[(entry.domain, entry.canonical_key)] = entry.id
        for source in entry.sources:
            if source.memory_id:
                self._memory_index[source.memory_id] = entry.id

    # -- Accès -----------------------------------------------------------------

    def has(self, entry_id: str) -> bool:
        return entry_id in self._entries

    def get(self, entry_id: str) -> KnowledgeEntry:
        if entry_id not in self._entries:
            raise NotFoundError(f"Entrée de connaissance introuvable : {entry_id}")
        return self._entries[entry_id]

    def put(self, entry: KnowledgeEntry) -> KnowledgeEntry:
        self._entries[entry.id] = entry
        self._reindex(entry)
        return entry

    def delete(self, entry_id: str) -> None:
        entry = self._entries.pop(entry_id, None)
        if entry is None:
            raise NotFoundError(f"Entrée de connaissance introuvable : {entry_id}")
        self._canonical_index.pop((entry.domain, entry.canonical_key), None)
        for source in entry.sources:
            self._memory_index.pop(source.memory_id, None)

    def all(self) -> List[KnowledgeEntry]:
        return list(self._entries.values())

    def count(self) -> int:
        return len(self._entries)

    def find_canonical(self, domain: str, canonical_key: str) -> Optional[KnowledgeEntry]:
        entry_id = self._canonical_index.get((domain, canonical_key))
        return self._entries.get(entry_id) if entry_id else None

    def entry_for_memory(self, memory_id: str) -> Optional[KnowledgeEntry]:
        entry_id = self._memory_index.get(memory_id)
        return self._entries.get(entry_id) if entry_id else None


__all__ = ["KnowledgeStore"]
