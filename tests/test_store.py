"""Tests de la base persistante et du journal d'historique."""

from __future__ import annotations

from pathlib import Path

import pytest

from scc_knowledge.core.clock import FixedClock
from scc_knowledge.core.errors import NotFoundError
from scc_knowledge.core.models import KnowledgeEntry, SourceRef
from scc_knowledge.store.history import HistoryLog
from scc_knowledge.store.store import KnowledgeStore


def _entry(**kw) -> KnowledgeEntry:
    base = dict(domain="doctrine", content="c", canonical_key="ck1")
    base.update(kw)
    return KnowledgeEntry(**base)


def test_put_get_count(tmp_path: Path):
    store = KnowledgeStore(tmp_path / "k.json")
    e = _entry()
    store.put(e)
    assert store.has(e.id) and store.get(e.id) is e
    assert store.count() == 1


def test_get_missing(tmp_path: Path):
    with pytest.raises(NotFoundError):
        KnowledgeStore(tmp_path / "k.json").get("nope")


def test_find_canonical(tmp_path: Path):
    store = KnowledgeStore(tmp_path / "k.json")
    e = _entry(canonical_key="abc")
    store.put(e)
    assert store.find_canonical("doctrine", "abc") is e
    assert store.find_canonical("decision", "abc") is None


def test_entry_for_memory(tmp_path: Path):
    store = KnowledgeStore(tmp_path / "k.json")
    e = _entry(sources=[SourceRef(memory_id="m1")])
    store.put(e)
    assert store.entry_for_memory("m1") is e
    assert store.entry_for_memory("m2") is None


def test_save_load_roundtrip_rebuilds_indexes(tmp_path: Path):
    path = tmp_path / "k.json"
    store = KnowledgeStore(path)
    store.put(_entry(canonical_key="ck", sources=[SourceRef(memory_id="mX")]))
    store.save()

    reloaded = KnowledgeStore(path)
    assert reloaded.count() == 1
    assert reloaded.find_canonical("doctrine", "ck") is not None
    assert reloaded.entry_for_memory("mX") is not None


def test_delete(tmp_path: Path):
    store = KnowledgeStore(tmp_path / "k.json")
    e = _entry(sources=[SourceRef(memory_id="m1")])
    store.put(e)
    store.delete(e.id)
    assert not store.has(e.id)
    assert store.entry_for_memory("m1") is None


def test_history(tmp_path: Path):
    log = HistoryLog(tmp_path / "h.jsonl", clock=FixedClock(step=1))
    log.append("promoted", "k1", "domain=doctrine")
    log.append("canonicalized", "k1")
    assert len(log.events()) == 2
    assert len(log.events_for("k1")) == 2
    assert log.events()[0]["entry_id"] == "k1"
