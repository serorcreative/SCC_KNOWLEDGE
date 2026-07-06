"""Chargement des objets de mémoire (contrat de données avec SCC_MEMORY).

Supporte le ``memory.json`` de la mémoire (dict ``id -> objet``), une liste
d'objets, ou un JSONL. Filtre par statut (``validated`` par défaut) : seule la
connaissance *consolidable* entre dans le moteur. Aucun import du moteur de
mémoire : seul son format est connu.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Union

from scc_knowledge.core.errors import LoaderError
from scc_knowledge.core.models import MemoryRecord


def _records_from_items(
    items: Iterable[Dict[str, Any]], status_filter: Optional[str]
) -> List[MemoryRecord]:
    records: List[MemoryRecord] = []
    for item in items:
        if not isinstance(item, dict):
            raise LoaderError(f"Entrée invalide (dict attendu) : {type(item).__name__}")
        record = MemoryRecord.from_dict(item)
        if status_filter and record.status != status_filter:
            continue
        records.append(record)
    return records


def load_records_from_dicts(
    items: Iterable[Dict[str, Any]], status_filter: Optional[str] = "validated"
) -> List[MemoryRecord]:
    """Convertit des dicts (format mémoire) en :class:`MemoryRecord` filtrés."""
    return _records_from_items(items, status_filter)


def load(path: Union[str, Path], status_filter: Optional[str] = "validated") -> List[MemoryRecord]:
    """Charge un export mémoire (``memory.json`` / liste / JSONL) et filtre par statut."""
    target = Path(path)
    if not target.exists():
        raise LoaderError(f"Export mémoire introuvable : {target}")

    try:
        text = target.read_text(encoding="utf-8")
    except OSError as exc:
        raise LoaderError(f"Lecture impossible ({target}) : {exc}") from exc

    if target.suffix.lower() in {".jsonl", ".ndjson"}:
        items: List[Dict[str, Any]] = []
        for lineno, line in enumerate(text.splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise LoaderError(f"Ligne {lineno} illisible dans {target.name} : {exc}") from exc
        return _records_from_items(items, status_filter)

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise LoaderError(f"JSON illisible ({target}) : {exc}") from exc

    if isinstance(data, dict):
        # memory.json = { id: objet } ; sinon objet unique.
        values = list(data.values()) if all(isinstance(v, dict) for v in data.values()) else [data]
    elif isinstance(data, list):
        values = data
    else:
        raise LoaderError(f"Structure JSON inattendue dans {target.name}")
    return _records_from_items(values, status_filter)


__all__ = ["load", "load_records_from_dicts"]
