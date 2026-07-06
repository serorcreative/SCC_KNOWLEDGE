"""Vue sémantique : construction automatique du graphe de connaissance.

Responsabilité 8. Assemble un graphe reliant les entrées de connaissance :

* **nœuds** = entrées (id, domaine, titre, tags) ;
* **arêtes explicites** = relations issues des liens mémoire ;
* **arêtes dérivées** = relations inférées par tags partagés (au-delà d'un seuil) ;
* **vues** = regroupements par domaine et index par tag (concepts / projets).

Déterministe et sans dépendance : prépare le moteur de raisonnement sans réaliser
d'inférence.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Set

from scc_knowledge.core.models import KnowledgeEntry, RelationType
from scc_knowledge.store.store import KnowledgeStore


@dataclass
class SemanticView:
    """Graphe sémantique sérialisable."""

    nodes: List[Dict[str, Any]] = field(default_factory=list)
    edges: List[Dict[str, Any]] = field(default_factory=list)
    by_domain: Dict[str, List[str]] = field(default_factory=dict)
    by_tag: Dict[str, List[str]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": self.nodes,
            "edges": self.edges,
            "by_domain": self.by_domain,
            "by_tag": self.by_tag,
            "counts": {
                "nodes": len(self.nodes),
                "edges": len(self.edges),
                "domains": len(self.by_domain),
                "tags": len(self.by_tag),
            },
        }


def _meaningful_tags(entry: KnowledgeEntry, ignored: Set[str]) -> Set[str]:
    return {t for t in entry.tags if t not in ignored}


def build_semantic_view(
    store: KnowledgeStore,
    shared_tag_min: int = 1,
    ignored_tags: Optional[Sequence[str]] = None,
) -> SemanticView:
    """Construit la vue sémantique à partir de l'état de la base."""
    ignored = set(ignored_tags or [])
    entries = sorted(store.all(), key=lambda e: e.id)

    view = SemanticView()
    by_domain: Dict[str, List[str]] = defaultdict(list)
    by_tag: Dict[str, List[str]] = defaultdict(list)

    for entry in entries:
        view.nodes.append(
            {
                "id": entry.id,
                "domain": entry.domain,
                "title": entry.title,
                "tags": list(entry.tags),
                "confidence": round(entry.confidence, 4),
            }
        )
        by_domain[entry.domain].append(entry.id)
        for tag in _meaningful_tags(entry, ignored):
            by_tag[tag].append(entry.id)
        # Arêtes explicites (relations déjà portées par l'entrée).
        for relation in entry.relations:
            view.edges.append(
                {
                    "source": entry.id,
                    "target": relation.target_id,
                    "relation": relation.relation,
                    "origin": relation.origin,
                    "weight": round(relation.weight, 4),
                }
            )

    # Arêtes dérivées : paires partageant assez de tags significatifs.
    for i in range(len(entries)):
        tags_i = _meaningful_tags(entries[i], ignored)
        if not tags_i:
            continue
        for j in range(i + 1, len(entries)):
            shared = tags_i & _meaningful_tags(entries[j], ignored)
            if len(shared) >= shared_tag_min:
                view.edges.append(
                    {
                        "source": entries[i].id,
                        "target": entries[j].id,
                        "relation": RelationType.RELATES_TO.value,
                        "origin": "derived",
                        "weight": float(len(shared)),
                        "shared_tags": sorted(shared),
                    }
                )

    view.by_domain = {k: v for k, v in sorted(by_domain.items())}
    view.by_tag = {k: v for k, v in sorted(by_tag.items())}
    return view


__all__ = ["SemanticView", "build_semantic_view"]
