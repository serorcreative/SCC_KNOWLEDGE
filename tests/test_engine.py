"""Tests de la façade KnowledgeEngine (bout en bout)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from scc_knowledge.core.config import KnowledgeConfig
from scc_knowledge.core.models import MemoryRecord
from scc_knowledge.engine import KnowledgeEngine


def _write_memory(path: Path, records: List[MemoryRecord]) -> Path:
    store = {}
    for r in records:
        store[r.id] = {
            "id": r.id, "type": r.type, "title": r.title, "content": r.content,
            "status": r.status, "confidence": r.confidence, "tags": r.tags,
            "origin_uri": r.origin_uri,
            "links": [{"target_id": l.target_id, "relation": l.relation} for l in r.links],
        }
    path.write_text(json.dumps(store), encoding="utf-8")
    return path


def test_consolidate_and_persist(engine: KnowledgeEngine, memory_records: List[MemoryRecord]):
    result = engine.consolidate(memory_records)
    assert result.promoted == 4 and result.canonicalized == 1
    assert result.relations_added == 1
    assert engine.count() == 4
    assert engine.config.knowledge_path.exists()


def test_consolidate_path_filters_status(engine: KnowledgeEngine, tmp_path: Path):
    records = [
        MemoryRecord(type="doctrine", id="m1", content="a", status="validated", confidence=0.8),
        MemoryRecord(type="doctrine", id="m2", content="b", status="candidate", confidence=0.8),
    ]
    path = _write_memory(tmp_path / "memory.json", records)
    result = engine.consolidate_path(path)
    assert result.promoted == 1  # seul le validé est consolidé
    assert engine.count() == 1


def test_search_and_export_graph(engine: KnowledgeEngine, memory_records: List[MemoryRecord]):
    engine.consolidate(memory_records)
    assert len(engine.search(domain="doctrine")) == 1
    graph_path = engine.export_graph()
    assert graph_path.exists()
    data = json.loads(graph_path.read_text(encoding="utf-8"))
    assert data["counts"]["nodes"] == 4


def test_verify_and_history(engine: KnowledgeEngine, memory_records: List[MemoryRecord]):
    engine.consolidate(memory_records)
    assert engine.verify().ok
    events = engine.history_events()
    assert len([e for e in events if e["action"] == "promoted"]) == 4
    assert len([e for e in events if e["action"] == "canonicalized"]) == 1
    assert len([e for e in events if e["action"] == "linked"]) == 1


def test_report_writes_files(engine: KnowledgeEngine, memory_records: List[MemoryRecord]):
    result = engine.consolidate(memory_records)
    paths = engine.report(consolidation=result)
    assert paths["json"].exists() and paths["markdown"].exists()
    payload = json.loads(paths["json"].read_text(encoding="utf-8"))
    assert payload["totals"]["entries"] == 4
    assert payload["consolidation"]["promoted"] == 4
    assert "coherence" in payload and "semantic" in payload


def test_reload_from_disk(config: KnowledgeConfig, memory_records: List[MemoryRecord]):
    KnowledgeEngine(config=config).consolidate(memory_records)
    reloaded = KnowledgeEngine(config=config)
    assert reloaded.count() == 4
