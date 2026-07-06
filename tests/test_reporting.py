"""Tests de la génération de rapports."""

from __future__ import annotations

import json
from typing import List

from scc_knowledge.core.config import KnowledgeConfig
from scc_knowledge.core.models import MemoryRecord
from scc_knowledge.engine import KnowledgeEngine
from scc_knowledge.reporting.generator import build_report_payload, write_report


def test_build_payload_serializable(engine: KnowledgeEngine, memory_records: List[MemoryRecord]):
    result = engine.consolidate(memory_records)
    payload = build_report_payload(
        engine.store, engine.history, consolidation=result,
        coherence=engine.detect_conflicts(), view=engine.semantic_view(),
        timestamp="2026-07-06T00:00:00Z",
    )
    json.dumps(payload)
    assert payload["totals"]["entries"] == 4
    assert set(payload["by_domain"]) == {"doctrine", "decision", "workflow", "reference"}


def test_write_report(engine: KnowledgeEngine, memory_records: List[MemoryRecord], config: KnowledgeConfig):
    result = engine.consolidate(memory_records)
    paths = write_report(
        engine.store, config.reports_dir, history=engine.history,
        consolidation=result, coherence=engine.detect_conflicts(), view=engine.semantic_view(),
        timestamp="2026-07-06T00:00:00Z",
    )
    md = paths["markdown"].read_text(encoding="utf-8")
    assert "Rapport de connaissance" in md
    assert "Par domaine" in md
    assert "Vue sémantique" in md
