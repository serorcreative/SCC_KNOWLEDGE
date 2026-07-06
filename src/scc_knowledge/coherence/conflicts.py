"""Cohérence : détection de doublons et de conflits, contrôle d'intégrité.

Responsabilité 4. Deux analyses, volontairement transparentes (V1 lexicale) :

* **doublons canoniques** — entrées de même domaine partageant la clé canonique
  (ne devrait pas subsister après canonisation : signal d'anomalie) ;
* **conflits potentiels** — entrées d'un même domaine « normatif » (doctrine,
  décision) au sujet proche (similarité de titre) mais au contenu divergent.

:func:`verify_integrity` contrôle empreintes, provenance, clés et relations.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Sequence, Set

from scc_knowledge.core.models import KnowledgeEntry, content_checksum, normalize_text
from scc_knowledge.core.report import Report

DEFAULT_CONFLICT_DOMAINS = ("doctrine", "decision")


@dataclass
class CoherenceResult:
    """Résultat de l'analyse de cohérence."""

    duplicates: List[List[str]] = field(default_factory=list)
    conflicts: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"duplicates": self.duplicates, "conflicts": self.conflicts}


def _title_tokens(entry: KnowledgeEntry) -> Set[str]:
    return set(normalize_text(entry.title or entry.content).split())


def _jaccard(a: Set[str], b: Set[str]) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def detect_conflicts(
    store,
    similarity_threshold: float = 0.6,
    conflict_domains: Sequence[str] = DEFAULT_CONFLICT_DOMAINS,
) -> CoherenceResult:
    """Détecte doublons canoniques et conflits potentiels."""
    entries = sorted(store.all(), key=lambda e: e.id)
    result = CoherenceResult()

    # Doublons canoniques (même domaine + même clé).
    groups: Dict[tuple, List[str]] = defaultdict(list)
    for entry in entries:
        if entry.canonical_key:
            groups[(entry.domain, entry.canonical_key)].append(entry.id)
    result.duplicates = [ids for ids in groups.values() if len(ids) > 1]

    # Conflits potentiels dans les domaines normatifs.
    domains = set(conflict_domains)
    normative = [e for e in entries if e.domain in domains]
    for i in range(len(normative)):
        for j in range(i + 1, len(normative)):
            a, b = normative[i], normative[j]
            if a.domain != b.domain:
                continue
            similarity = _jaccard(_title_tokens(a), _title_tokens(b))
            same_content = normalize_text(a.content) == normalize_text(b.content)
            if similarity >= similarity_threshold and not same_content:
                result.conflicts.append(
                    {
                        "a": a.id,
                        "b": b.id,
                        "domain": a.domain,
                        "similarity": round(similarity, 4),
                        "reason": "sujet proche, contenu divergent",
                    }
                )
    return result


def coherence_report(result: CoherenceResult) -> Report:
    """Transforme un :class:`CoherenceResult` en rapport."""
    report = Report("Cohérence")
    report.add("doublons canoniques", not result.duplicates, f"{len(result.duplicates)} groupe(s)")
    report.add("conflits potentiels", not result.conflicts, f"{len(result.conflicts)} paire(s)")
    return report


def verify_integrity(store) -> Report:
    """Contrôle d'intégrité de la base (empreintes, provenance, clés, relations)."""
    report = Report("Intégrité connaissance")
    entries = store.all()
    ids = {e.id for e in entries}

    bad_checksum = [e.id for e in entries if e.checksum != content_checksum(e.content)]
    no_source = [e.id for e in entries if not e.sources]
    no_key = [e.id for e in entries if not e.canonical_key]
    dangling = [
        f"{e.id}->{r.target_id}"
        for e in entries
        for r in e.relations
        if r.target_id not in ids
    ]

    report.add("empreintes", not bad_checksum, ", ".join(bad_checksum))
    report.add("provenance", not no_source, ", ".join(no_source))
    report.add("clés canoniques", not no_key, ", ".join(no_key))
    report.add("relations résolues", not dangling, ", ".join(dangling))
    return report


__all__ = ["CoherenceResult", "detect_conflicts", "coherence_report", "verify_integrity"]
