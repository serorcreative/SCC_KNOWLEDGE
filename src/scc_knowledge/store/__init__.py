"""Couche de persistance : base de connaissance et journal d'historique."""

from __future__ import annotations

from scc_knowledge.store.history import HistoryLog
from scc_knowledge.store.store import KnowledgeStore

__all__ = ["KnowledgeStore", "HistoryLog"]
