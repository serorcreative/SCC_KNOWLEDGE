"""Promotion d'un objet mémoire en entrée de connaissance + versionnement.

La promotion crée une :class:`KnowledgeEntry` canonique à partir d'un
:class:`MemoryRecord` (responsabilité 1). Le versionnement suit les évolutions
du contenu au fil des canonisations successives.
"""

from __future__ import annotations

from scc_knowledge.core.models import (
    KnowledgeDomain,
    KnowledgeEntry,
    MemoryRecord,
    Revision,
    SourceRef,
    canonical_key,
    content_checksum,
)

_TITLE_MAX = 70


def _derive_title(record: MemoryRecord) -> str:
    if record.title:
        return record.title
    flat = " ".join(record.content.split())
    return flat[:_TITLE_MAX] + ("…" if len(flat) > _TITLE_MAX else "")


def record_initial_revision(entry: KnowledgeEntry, timestamp: str, change: str = "promoted") -> KnowledgeEntry:
    """Initialise empreinte, version 1 et première révision."""
    entry.checksum = content_checksum(entry.content)
    entry.version = 1
    entry.revisions = [Revision(version=1, checksum=entry.checksum, updated_at=timestamp, change=change)]
    return entry


def bump_version(entry: KnowledgeEntry, timestamp: str, change: str) -> KnowledgeEntry:
    """Recalcule l'empreinte, incrémente la version et ajoute une révision."""
    entry.checksum = content_checksum(entry.content)
    entry.version += 1
    entry.updated_at = timestamp
    entry.revisions.append(
        Revision(version=entry.version, checksum=entry.checksum, updated_at=timestamp, change=change)
    )
    return entry


def promote(record: MemoryRecord, domain: KnowledgeDomain, timestamp: str) -> KnowledgeEntry:
    """Crée une entrée de connaissance canonique à partir d'un objet mémoire."""
    entry = KnowledgeEntry(
        domain=domain.value,
        content=record.content,
        title=_derive_title(record),
        tags=list(record.tags),
        confidence=record.confidence,
        created_at=timestamp,
        updated_at=timestamp,
        canonical_key=canonical_key(domain.value, record.title, record.content),
        sources=[
            SourceRef(
                memory_id=record.id,
                origin_uri=record.origin_uri,
                checksum=record.checksum,
                confidence=record.confidence,
                consolidated_at=timestamp,
            )
        ],
        metadata={"memory_type": record.type},
    )
    record_initial_revision(entry, timestamp)
    return entry


__all__ = ["promote", "record_initial_revision", "bump_version"]
