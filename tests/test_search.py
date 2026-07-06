"""Tests de la recherche."""

from __future__ import annotations

from pathlib import Path

from scc_knowledge.core.models import KnowledgeEntry, Relation
from scc_knowledge.search.query import search
from scc_knowledge.store.store import KnowledgeStore


def _store(tmp_path: Path) -> KnowledgeStore:
    store = KnowledgeStore(tmp_path / "k.json")
    store.put(KnowledgeEntry(domain="doctrine", id="D1", title="couplage", content="ne pas coupler",
                             tags=["architecture"], confidence=0.9, canonical_key="1"))
    store.put(KnowledgeEntry(domain="decision", id="X1", title="db", content="adopter postgres",
                             tags=["architecture", "database"], confidence=0.6, canonical_key="2",
                             relations=[Relation(target_id="D1", relation="derived_from")]))
    store.put(KnowledgeEntry(domain="decision", id="X2", title="cache", content="ajouter un cache",
                             tags=["perf"], confidence=0.4, canonical_key="3"))
    return store


def test_by_domain(tmp_path: Path):
    assert {e.id for e in search(_store(tmp_path), domain="decision")} == {"X1", "X2"}


def test_by_tags(tmp_path: Path):
    assert {e.id for e in search(_store(tmp_path), tags=["architecture", "database"])} == {"X1"}


def test_by_text(tmp_path: Path):
    assert {e.id for e in search(_store(tmp_path), text="postgres")} == {"X1"}


def test_by_min_confidence(tmp_path: Path):
    assert {e.id for e in search(_store(tmp_path), min_confidence=0.5)} == {"D1", "X1"}


def test_by_relation(tmp_path: Path):
    assert {e.id for e in search(_store(tmp_path), relation="derived_from")} == {"X1"}


def test_sorted_and_limit(tmp_path: Path):
    results = search(_store(tmp_path), limit=2)
    assert [e.id for e in results] == ["D1", "X1"]  # confiance décroissante
