"""Recherche dans la base de connaissance.

Filtre déterministe : domaine, tags (tous requis), sous-chaîne de texte
(titre + contenu), confiance minimale, relation (entrées ayant une relation d'un
type donné). Résultats triés par confiance décroissante puis date de mise à jour.
"""

from __future__ import annotations

from typing import List, Optional, Sequence

from scc_knowledge.core.models import KnowledgeEntry
from scc_knowledge.store.store import KnowledgeStore


def search(
    store: KnowledgeStore,
    domain: Optional[str] = None,
    tags: Optional[Sequence[str]] = None,
    text: Optional[str] = None,
    min_confidence: Optional[float] = None,
    relation: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[KnowledgeEntry]:
    """Retourne les entrées satisfaisant tous les critères fournis."""
    required_tags = set(tags) if tags else None
    needle = text.lower() if text else None

    results: List[KnowledgeEntry] = []
    for entry in store.all():
        if domain is not None and entry.domain != domain:
            continue
        if required_tags is not None and not required_tags.issubset(set(entry.tags)):
            continue
        if min_confidence is not None and entry.confidence < min_confidence:
            continue
        if relation is not None and not any(r.relation == relation for r in entry.relations):
            continue
        if needle is not None and needle not in f"{entry.title} {entry.content}".lower():
            continue
        results.append(entry)

    results.sort(key=lambda e: (-e.confidence, e.updated_at))
    if limit is not None:
        results = results[:limit]
    return results


__all__ = ["search"]
