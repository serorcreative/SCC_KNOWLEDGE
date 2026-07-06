"""Noyau du moteur de connaissance : modèles, config, rapport, erreurs, horloge, loader."""

from __future__ import annotations

from scc_knowledge.core.clock import Clock, FixedClock, SystemClock
from scc_knowledge.core.config import KnowledgeConfig, load_config
from scc_knowledge.core.loader import load, load_records_from_dicts
from scc_knowledge.core.models import (
    KnowledgeDomain,
    KnowledgeEntry,
    MemoryLink,
    MemoryRecord,
    Relation,
    RelationType,
    Revision,
    SourceRef,
    canonical_key,
    content_checksum,
    new_id,
    normalize_text,
)
from scc_knowledge.core.report import Check, Report

__all__ = [
    "Clock",
    "SystemClock",
    "FixedClock",
    "KnowledgeConfig",
    "load_config",
    "load",
    "load_records_from_dicts",
    "KnowledgeDomain",
    "KnowledgeEntry",
    "MemoryLink",
    "MemoryRecord",
    "Relation",
    "RelationType",
    "Revision",
    "SourceRef",
    "canonical_key",
    "content_checksum",
    "new_id",
    "normalize_text",
    "Check",
    "Report",
]
