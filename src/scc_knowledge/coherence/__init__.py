"""Cohérence : doublons, conflits, intégrité."""

from __future__ import annotations

from scc_knowledge.coherence.conflicts import (
    CoherenceResult,
    coherence_report,
    detect_conflicts,
    verify_integrity,
)

__all__ = ["CoherenceResult", "detect_conflicts", "coherence_report", "verify_integrity"]
