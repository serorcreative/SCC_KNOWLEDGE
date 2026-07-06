"""Consolidation : promotion, canonisation, résolution des relations."""

from __future__ import annotations

from scc_knowledge.consolidation.canonicalize import canonicalize
from scc_knowledge.consolidation.consolidate import (
    ConsolidationOutcome,
    ConsolidationResult,
    build_relations,
    consolidate_many,
    consolidate_record,
)
from scc_knowledge.consolidation.promote import bump_version, promote, record_initial_revision

__all__ = [
    "promote",
    "record_initial_revision",
    "bump_version",
    "canonicalize",
    "consolidate_record",
    "consolidate_many",
    "build_relations",
    "ConsolidationOutcome",
    "ConsolidationResult",
]
