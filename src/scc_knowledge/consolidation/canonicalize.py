"""Canonisation : fusion d'un objet mémoire compatible dans une connaissance.

Responsabilité 7. Un objet mémoire partageant la clé canonique d'une entrée est
**fusionné** : provenance enrichie (nouvelle source), union des tags, confiance
maximale, éventuel remplacement du contenu selon la politique. Ne versionne pas
lui-même : signale un changement de contenu à l'orchestrateur.
"""

from __future__ import annotations

from scc_knowledge.core.models import (
    KnowledgeEntry,
    MemoryRecord,
    SourceRef,
    normalize_text,
)


def _should_replace_content(entry: KnowledgeEntry, record: MemoryRecord, policy: str) -> bool:
    if policy == "keep_existing":
        return False
    if policy == "longest":
        return len(record.content) > len(entry.content)
    return record.confidence > entry.confidence  # "highest_confidence"


def canonicalize(
    entry: KnowledgeEntry,
    record: MemoryRecord,
    timestamp: str,
    policy: str = "highest_confidence",
) -> bool:
    """Fusionne ``record`` dans ``entry``. Retourne ``True`` si le contenu a changé."""
    prev_confidence = entry.confidence

    # Provenance : nouvelle source tracée (si l'objet mémoire n'est pas déjà présent).
    if not any(s.memory_id == record.id for s in entry.sources):
        entry.sources.append(
            SourceRef(
                memory_id=record.id,
                origin_uri=record.origin_uri,
                checksum=record.checksum,
                confidence=record.confidence,
                consolidated_at=timestamp,
            )
        )

    # Tags : union en conservant l'ordre.
    for tag in record.tags:
        if tag not in entry.tags:
            entry.tags.append(tag)

    # Titre : adopté si absent.
    if not entry.title and record.title:
        entry.title = record.title

    # Contenu : remplacement selon la politique (décidé avant maj de confiance).
    content_changed = False
    if _should_replace_content(entry, record, policy) and normalize_text(
        record.content
    ) != normalize_text(entry.content):
        entry.content = record.content
        content_changed = True

    entry.confidence = max(prev_confidence, record.confidence)
    entry.updated_at = timestamp
    return content_changed


__all__ = ["canonicalize"]
