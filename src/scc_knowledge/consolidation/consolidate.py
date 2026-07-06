"""Orchestrateur de consolidation : promotion, canonisation, relations.

Pour chaque objet mémoire consolidable :

* clé canonique inconnue → **promotion** (nouvelle entrée de connaissance) ;
* clé canonique connue → **canonisation** (fusion dans l'entrée existante).

Un second passage (:func:`build_relations`) traduit les liens *mémoire* en
relations *de connaissance* (structuration, responsabilité 3).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from scc_knowledge.consolidation.canonicalize import canonicalize
from scc_knowledge.consolidation.promote import bump_version, promote
from scc_knowledge.core.clock import Clock, SystemClock
from scc_knowledge.core.models import KnowledgeEntry, MemoryRecord, Relation, canonical_key
from scc_knowledge.store.history import HistoryLog
from scc_knowledge.store.store import KnowledgeStore
from scc_knowledge.taxonomy.classifier import classify_domain


@dataclass
class ConsolidationOutcome:
    action: str  # "promoted" | "canonicalized"
    entry: KnowledgeEntry


@dataclass
class ConsolidationResult:
    promoted: int = 0
    canonicalized: int = 0
    relations_added: int = 0
    outcomes: List[ConsolidationOutcome] = field(default_factory=list)


def consolidate_record(
    store: KnowledgeStore,
    history: HistoryLog,
    record: MemoryRecord,
    clock: Optional[Clock] = None,
    policy: str = "highest_confidence",
    taxonomy_overrides: Optional[Dict[str, str]] = None,
) -> ConsolidationOutcome:
    """Consolide un objet mémoire (promotion ou canonisation)."""
    clock = clock or SystemClock()
    domain = classify_domain(record.type, taxonomy_overrides)
    key = canonical_key(domain.value, record.title, record.content)
    existing = store.find_canonical(domain.value, key)
    timestamp = clock.now()

    if existing is None:
        entry = promote(record, domain, timestamp)
        store.put(entry)
        history.append("promoted", entry.id, f"domain={domain.value} memory={record.id}")
        return ConsolidationOutcome("promoted", entry)

    changed = canonicalize(existing, record, timestamp, policy=policy)
    if changed:
        bump_version(existing, timestamp, "content updated via canonicalization")
    store.put(existing)
    history.append("canonicalized", existing.id, f"memory={record.id} content_changed={changed}")
    return ConsolidationOutcome("canonicalized", existing)


def build_relations(
    store: KnowledgeStore,
    history: HistoryLog,
    records: Sequence[MemoryRecord],
    clock: Optional[Clock] = None,
) -> int:
    """Traduit les liens mémoire en relations de connaissance. Retourne le nb ajouté."""
    clock = clock or SystemClock()
    added = 0
    for record in records:
        entry = store.entry_for_memory(record.id)
        if entry is None:
            continue
        for link in record.links:
            target = store.entry_for_memory(link.target_id)
            if target is None or target.id == entry.id:
                continue
            if any(
                r.target_id == target.id and r.relation == link.relation and r.origin == "explicit"
                for r in entry.relations
            ):
                continue
            entry.relations.append(
                Relation(target_id=target.id, relation=link.relation, origin="explicit", created_at=clock.now())
            )
            added += 1
            history.append("linked", entry.id, f"{link.relation} -> {target.id}")
        store.put(entry)
    return added


def consolidate_many(
    store: KnowledgeStore,
    history: HistoryLog,
    records: Sequence[MemoryRecord],
    clock: Optional[Clock] = None,
    policy: str = "highest_confidence",
    taxonomy_overrides: Optional[Dict[str, str]] = None,
) -> ConsolidationResult:
    """Consolide un lot d'objets mémoire puis construit les relations."""
    result = ConsolidationResult()
    for record in records:
        outcome = consolidate_record(
            store, history, record, clock=clock, policy=policy, taxonomy_overrides=taxonomy_overrides
        )
        result.outcomes.append(outcome)
        if outcome.action == "promoted":
            result.promoted += 1
        else:
            result.canonicalized += 1
    result.relations_added = build_relations(store, history, records, clock=clock)
    return result


__all__ = [
    "consolidate_record",
    "consolidate_many",
    "build_relations",
    "ConsolidationOutcome",
    "ConsolidationResult",
]
