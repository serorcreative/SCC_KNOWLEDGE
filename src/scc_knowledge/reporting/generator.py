"""Génération des rapports de connaissance (JSON + Markdown).

Résume l'état de la base (volumétrie par domaine, relations, provenance,
versions), l'éventuelle consolidation, la cohérence et la vue sémantique.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from scc_knowledge.coherence.conflicts import CoherenceResult
from scc_knowledge.consolidation.consolidate import ConsolidationResult
from scc_knowledge.semantic.graph import SemanticView
from scc_knowledge.store.history import HistoryLog
from scc_knowledge.store.store import KnowledgeStore


def build_report_payload(
    store: KnowledgeStore,
    history: Optional[HistoryLog] = None,
    consolidation: Optional[ConsolidationResult] = None,
    coherence: Optional[CoherenceResult] = None,
    view: Optional[SemanticView] = None,
    timestamp: Optional[str] = None,
) -> Dict[str, Any]:
    """Construit le dictionnaire de rapport à partir de l'état courant."""
    stamp = timestamp or datetime.now(timezone.utc).isoformat()
    entries = store.all()

    payload: Dict[str, Any] = {
        "timestamp": stamp,
        "totals": {
            "entries": len(entries),
            "relations": sum(len(e.relations) for e in entries),
            "sources": sum(len(e.sources) for e in entries),
            "versions": sum(e.version for e in entries),
            "history_events": len(history.events()) if history else 0,
        },
        "by_domain": dict(Counter(e.domain for e in entries)),
    }
    if consolidation is not None:
        payload["consolidation"] = {
            "promoted": consolidation.promoted,
            "canonicalized": consolidation.canonicalized,
            "relations_added": consolidation.relations_added,
        }
    if coherence is not None:
        payload["coherence"] = {
            "duplicates": len(coherence.duplicates),
            "conflicts": len(coherence.conflicts),
            "detail": coherence.to_dict(),
        }
    if view is not None:
        payload["semantic"] = view.to_dict()["counts"]
    return payload


def _render_markdown(payload: Dict[str, Any]) -> str:
    totals = payload["totals"]
    lines = [
        "# Rapport de connaissance — SCC",
        "",
        f"- **Horodatage** : {payload['timestamp']}",
        "",
        "## Volumétrie",
        f"- Entrées : {totals['entries']}",
        f"- Relations : {totals['relations']}",
        f"- Sources (provenance) : {totals['sources']}",
        f"- Versions cumulées : {totals['versions']}",
        f"- Événements d'historique : {totals['history_events']}",
        "",
        "## Par domaine",
    ]
    by_domain = payload["by_domain"]
    lines += [f"- {k} : {v}" for k, v in sorted(by_domain.items())] or ["- (aucun)"]

    if "consolidation" in payload:
        c = payload["consolidation"]
        lines += [
            "", "## Dernière consolidation",
            f"- Promues : {c['promoted']}",
            f"- Canonisées : {c['canonicalized']}",
            f"- Relations ajoutées : {c['relations_added']}",
        ]
    if "coherence" in payload:
        co = payload["coherence"]
        lines += [
            "", "## Cohérence",
            f"- Doublons canoniques : {co['duplicates']}",
            f"- Conflits potentiels : {co['conflicts']}",
        ]
    if "semantic" in payload:
        s = payload["semantic"]
        lines += [
            "", "## Vue sémantique",
            f"- Nœuds : {s['nodes']}",
            f"- Arêtes : {s['edges']}",
            f"- Domaines : {s['domains']}",
            f"- Tags indexés : {s['tags']}",
        ]
    lines.append("")
    return "\n".join(lines)


def write_report(
    store: KnowledgeStore,
    reports_dir: Path,
    history: Optional[HistoryLog] = None,
    consolidation: Optional[ConsolidationResult] = None,
    coherence: Optional[CoherenceResult] = None,
    view: Optional[SemanticView] = None,
    name: str = "knowledge",
    timestamp: Optional[str] = None,
) -> Dict[str, Path]:
    """Écrit les rapports JSON et Markdown ; retourne leurs chemins."""
    target_dir = Path(reports_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    payload = build_report_payload(store, history, consolidation, coherence, view, timestamp=timestamp)
    json_path = target_dir / f"{name}.json"
    md_path = target_dir / f"{name}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(_render_markdown(payload), encoding="utf-8")
    return {"json": json_path, "markdown": md_path}


__all__ = ["build_report_payload", "write_report"]
