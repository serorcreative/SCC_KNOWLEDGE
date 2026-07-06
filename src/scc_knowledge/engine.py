"""Façade du moteur de connaissance.

API unique reliant chargement, consolidation, base, sémantique, cohérence,
recherche et rapports :

    engine = KnowledgeEngine()
    engine.consolidate_path("../05_MEMORY/store/memory.json")
    engine.export_graph()
    engine.search(domain="doctrine")
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Union

from scc_knowledge.coherence.conflicts import CoherenceResult, detect_conflicts, verify_integrity
from scc_knowledge.consolidation.consolidate import ConsolidationResult, consolidate_many
from scc_knowledge.core import loader
from scc_knowledge.core.clock import Clock, SystemClock
from scc_knowledge.core.config import KnowledgeConfig, load_config
from scc_knowledge.core.models import KnowledgeEntry, MemoryRecord
from scc_knowledge.core.report import Report
from scc_knowledge.reporting.generator import write_report
from scc_knowledge.search.query import search as search_query
from scc_knowledge.semantic.graph import SemanticView, build_semantic_view
from scc_knowledge.store.history import HistoryLog
from scc_knowledge.store.store import KnowledgeStore


class KnowledgeEngine:
    """Point d'entrée programmatique de la base de connaissance consolidée."""

    def __init__(self, config: Optional[KnowledgeConfig] = None, clock: Optional[Clock] = None):
        self.config = config or load_config()
        self.config.ensure_directories()
        self.clock = clock or SystemClock()
        self.store = KnowledgeStore(self.config.knowledge_path)
        self.history = HistoryLog(self.config.history_path, clock=self.clock)

    # -- Consolidation ---------------------------------------------------------

    def consolidate(self, records: Sequence[MemoryRecord]) -> ConsolidationResult:
        result = consolidate_many(
            self.store,
            self.history,
            records,
            clock=self.clock,
            policy=self.config.canonicalize_policy,
            taxonomy_overrides=self.config.taxonomy_overrides,
        )
        self.store.save()
        return result

    def consolidate_path(self, path: Union[str, Path]) -> ConsolidationResult:
        records = loader.load(path, status_filter=self.config.input_status_filter or None)
        return self.consolidate(records)

    # -- Accès -----------------------------------------------------------------

    def get(self, entry_id: str) -> KnowledgeEntry:
        return self.store.get(entry_id)

    def all(self) -> List[KnowledgeEntry]:
        return self.store.all()

    def count(self) -> int:
        return self.store.count()

    def search(self, **criteria) -> List[KnowledgeEntry]:
        return search_query(self.store, **criteria)

    # -- Vue sémantique --------------------------------------------------------

    def semantic_view(self) -> SemanticView:
        return build_semantic_view(
            self.store,
            shared_tag_min=self.config.semantic_shared_tag_min,
            ignored_tags=self.config.ignored_tags,
        )

    def export_graph(self, path: Optional[Union[str, Path]] = None) -> Path:
        target = Path(path) if path else self.config.graph_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(self.semantic_view().to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return target

    # -- Cohérence -------------------------------------------------------------

    def detect_conflicts(self) -> CoherenceResult:
        return detect_conflicts(self.store)

    def verify(self) -> Report:
        return verify_integrity(self.store)

    # -- Historique & rapports -------------------------------------------------

    def history_events(self, entry_id: Optional[str] = None) -> List[dict]:
        return self.history.events_for(entry_id) if entry_id else self.history.events()

    def report(
        self,
        consolidation: Optional[ConsolidationResult] = None,
        name: str = "knowledge",
    ) -> Dict[str, Path]:
        return write_report(
            self.store,
            self.config.reports_dir,
            history=self.history,
            consolidation=consolidation,
            coherence=self.detect_conflicts(),
            view=self.semantic_view(),
            name=name,
        )

    def save(self) -> None:
        self.store.save()


__all__ = ["KnowledgeEngine"]
