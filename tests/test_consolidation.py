"""Tests de la consolidation : promotion, canonisation, relations."""

from __future__ import annotations

from pathlib import Path
from typing import List

from scc_knowledge.consolidation.canonicalize import canonicalize
from scc_knowledge.consolidation.consolidate import (
    build_relations,
    consolidate_many,
    consolidate_record,
)
from scc_knowledge.consolidation.promote import promote
from scc_knowledge.core.clock import FixedClock
from scc_knowledge.core.models import KnowledgeDomain, MemoryRecord
from scc_knowledge.store.history import HistoryLog
from scc_knowledge.store.store import KnowledgeStore


def _ctx(tmp_path: Path):
    return (
        KnowledgeStore(tmp_path / "k.json"),
        HistoryLog(tmp_path / "h.jsonl", clock=FixedClock(step=1)),
        FixedClock(step=1),
    )


def test_promote_creates_entry():
    rec = MemoryRecord(type="doctrine", id="m1", title="T", content="c", confidence=0.7)
    entry = promote(rec, KnowledgeDomain.DOCTRINE, "t0")
    assert entry.domain == "doctrine"
    assert entry.version == 1
    assert len(entry.sources) == 1 and entry.sources[0].memory_id == "m1"
    assert len(entry.revisions) == 1
    assert entry.canonical_key


def test_consolidate_promotes_then_canonicalizes(tmp_path: Path):
    store, history, clock = _ctx(tmp_path)
    r1 = MemoryRecord(type="doctrine", id="m1", title="Couplage", content="Ne pas coupler.", confidence=0.7, tags=["a"])
    r2 = MemoryRecord(type="doctrine", id="m2", title="Couplage", content="Ne pas coupler.", confidence=0.9, tags=["b"])
    o1 = consolidate_record(store, history, r1, clock=clock)
    o2 = consolidate_record(store, history, r2, clock=clock)
    assert o1.action == "promoted"
    assert o2.action == "canonicalized"
    assert store.count() == 1
    entry = o2.entry
    assert entry.confidence == 0.9              # confiance max
    assert set(entry.tags) == {"a", "b"}        # tags fusionnés
    assert len(entry.sources) == 2              # provenance des deux objets
    assert entry.version == 1                   # contenu identique → pas de version


def test_canonicalize_content_replaced_by_policy():
    from scc_knowledge.core.models import KnowledgeEntry
    entry = KnowledgeEntry(domain="doctrine", content="ancien", confidence=0.4)
    rec = MemoryRecord(type="doctrine", id="m9", content="nouveau contenu", confidence=0.9)
    changed = canonicalize(entry, rec, "t0", policy="highest_confidence")
    assert changed is True
    assert entry.content == "nouveau contenu"


def test_consolidate_many_and_relations(tmp_path: Path, memory_records: List[MemoryRecord]):
    store, history, clock = _ctx(tmp_path)
    result = consolidate_many(store, history, memory_records, clock=clock)
    # m1+m2 canonisés (doctrine), m3 decision, m4 workflow, m5 reference = 4 entrées.
    assert result.promoted == 4
    assert result.canonicalized == 1
    assert store.count() == 4
    # Le lien m3 -> m1 devient une relation de connaissance.
    assert result.relations_added == 1
    decision = next(e for e in store.all() if e.domain == "decision")
    doctrine = next(e for e in store.all() if e.domain == "doctrine")
    assert decision.relations[0].target_id == doctrine.id
    assert decision.relations[0].relation == "derived_from"


def test_build_relations_idempotent(tmp_path: Path, memory_records: List[MemoryRecord]):
    store, history, clock = _ctx(tmp_path)
    consolidate_many(store, history, memory_records, clock=clock)
    added_again = build_relations(store, history, memory_records, clock=clock)
    assert added_again == 0  # relations déjà présentes, pas de doublon
