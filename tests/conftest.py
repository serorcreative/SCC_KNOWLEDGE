"""Fixtures partagées : configuration isolée, horloge déterministe, objets mémoire."""

from __future__ import annotations

from pathlib import Path
from typing import List

import pytest

from scc_knowledge.core.clock import FixedClock
from scc_knowledge.core.config import KnowledgeConfig
from scc_knowledge.core.models import MemoryLink, MemoryRecord
from scc_knowledge.engine import KnowledgeEngine


@pytest.fixture
def config(tmp_path: Path) -> KnowledgeConfig:
    cfg = KnowledgeConfig(
        engine_root=tmp_path,
        knowledge_path=tmp_path / "knowledge" / "knowledge.json",
        graph_path=tmp_path / "knowledge" / "graph.json",
        history_path=tmp_path / "knowledge" / "history.jsonl",
        reports_dir=tmp_path / "reports",
        logs_dir=tmp_path / "logs",
        input_status_filter="validated",
        canonicalize_policy="highest_confidence",
        semantic_shared_tag_min=1,
        ignored_tags=["doctrine", "decision", "workflow", "task", "chatgpt", "claude"],
    )
    cfg.ensure_directories()
    return cfg


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock(step=1)


@pytest.fixture
def memory_records() -> List[MemoryRecord]:
    """Objets mémoire validés : domaines variés, un doublon canonique, un lien."""
    return [
        MemoryRecord(
            type="doctrine", id="m1", title="Couplage",
            content="Ne jamais coupler les modules.", status="validated",
            confidence=0.8, tags=["doctrine", "architecture"],
            origin_uri="/raw/a.md",
        ),
        MemoryRecord(  # même sujet canonique que m1 → canonisation
            type="doctrine", id="m2", title="Couplage",
            content="Ne jamais coupler les modules.", status="validated",
            confidence=0.9, tags=["doctrine", "modularite"],
            origin_uri="/raw/b.md",
        ),
        MemoryRecord(
            type="decision", id="m3", title="Base de donnees",
            content="Adopter PostgreSQL.", status="validated",
            confidence=0.9, tags=["decision", "architecture"],
            origin_uri="/raw/c.md",
            links=[MemoryLink(target_id="m1", relation="derived_from")],
        ),
        MemoryRecord(
            type="workflow", id="m4", title="Pipeline",
            content="Etapes du pipeline d'ingestion.", status="validated",
            confidence=0.7, tags=["workflow", "ingestion"],
        ),
        MemoryRecord(
            type="task", id="m5", title="",
            content="Ecrire les tests d'integration.", status="validated",
            confidence=0.5, tags=["task"],
        ),
    ]


@pytest.fixture
def engine(config: KnowledgeConfig, clock: FixedClock) -> KnowledgeEngine:
    return KnowledgeEngine(config=config, clock=clock)
