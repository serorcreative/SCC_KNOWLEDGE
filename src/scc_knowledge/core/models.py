"""Modèles de données du moteur de connaissance.

* :class:`MemoryRecord` — **entrée** : un objet de mémoire consolidable exporté
  par SCC_MEMORY (format de son ``memory.json``). Découplé : reconstruit par
  :meth:`MemoryRecord.from_dict`, sans importer le moteur de mémoire.
* :class:`KnowledgeEntry` — **unité de connaissance consolidée** : canonique,
  classée par domaine, tracée (sources), versionnée et reliée.
* Structures auxiliaires : :class:`SourceRef`, :class:`Relation`,
  :class:`Revision`, et les énumérations :class:`KnowledgeDomain` /
  :class:`RelationType`.
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


# --------------------------------------------------------------------------- #
# Énumérations
# --------------------------------------------------------------------------- #


class KnowledgeDomain(str, Enum):
    """Domaines de la taxonomie de connaissance."""

    DOCTRINE = "doctrine"
    DECISION = "decision"
    WORKFLOW = "workflow"
    PROMPT = "prompt"
    LESSON = "lesson"
    PROJECT = "project"
    CONCEPT = "concept"
    REFERENCE = "reference"


class RelationType(str, Enum):
    """Types de relations connues (la relation est stockée en chaîne libre)."""

    RELATES_TO = "relates_to"
    PART_OF = "part_of"
    DERIVED_FROM = "derived_from"
    SUPERSEDES = "supersedes"
    DEPENDS_ON = "depends_on"
    CONTRADICTS = "contradicts"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def new_id(prefix: str = "kno") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def content_checksum(text: str) -> str:
    return hashlib.sha1(normalize_text(text).encode("utf-8")).hexdigest()


def canonical_key(domain: str, title: str, content: str) -> str:
    """Clé de canonisation : hash du domaine + sujet normalisé (titre, sinon contenu).

    Deux objets mémoire de même domaine et même sujet convergent vers la même
    connaissance canonique.
    """
    subject = normalize_text(title) or normalize_text(content)
    return hashlib.sha1(f"{domain}\x00{subject}".encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------- #
# Entrée : objet de mémoire
# --------------------------------------------------------------------------- #


@dataclass
class MemoryLink:
    """Lien porté par un objet mémoire (cible = id d'un autre objet mémoire)."""

    target_id: str
    relation: str = RelationType.RELATES_TO.value

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryLink":
        return cls(
            target_id=str(data.get("target_id", "")),
            relation=str(data.get("relation", RelationType.RELATES_TO.value)),
        )


@dataclass
class MemoryRecord:
    """Objet de mémoire consolidable reçu de SCC_MEMORY (entrée du moteur)."""

    type: str
    content: str
    id: str = ""
    title: str = ""
    status: str = "validated"
    confidence: float = 0.0
    tags: List[str] = field(default_factory=list)
    origin_uri: str = ""
    checksum: str = ""
    links: List[MemoryLink] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryRecord":
        return cls(
            type=str(data.get("type", "unknown")),
            content=str(data.get("content", "")),
            id=str(data.get("id", "")),
            title=str(data.get("title", "")),
            status=str(data.get("status", "validated")),
            confidence=float(data.get("confidence", 0.0) or 0.0),
            tags=list(data.get("tags", []) or []),
            origin_uri=str(data.get("origin_uri", "")),
            checksum=str(data.get("checksum", "")),
            links=[MemoryLink.from_dict(l) for l in data.get("links", []) or []],
            metadata=dict(data.get("metadata", {}) or {}),
        )


# --------------------------------------------------------------------------- #
# Structures internes de l'entrée de connaissance
# --------------------------------------------------------------------------- #


@dataclass
class SourceRef:
    """Trace d'un objet mémoire ayant contribué à une connaissance (provenance)."""

    memory_id: str = ""
    origin_uri: str = ""
    checksum: str = ""
    confidence: float = 0.0
    consolidated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "origin_uri": self.origin_uri,
            "checksum": self.checksum,
            "confidence": round(self.confidence, 4),
            "consolidated_at": self.consolidated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SourceRef":
        return cls(
            memory_id=str(data.get("memory_id", "")),
            origin_uri=str(data.get("origin_uri", "")),
            checksum=str(data.get("checksum", "")),
            confidence=float(data.get("confidence", 0.0) or 0.0),
            consolidated_at=str(data.get("consolidated_at", "")),
        )


@dataclass
class Relation:
    """Relation dirigée typée vers une autre entrée de connaissance."""

    target_id: str
    relation: str = RelationType.RELATES_TO.value
    weight: float = 1.0
    origin: str = "explicit"  # "explicit" (lien mémoire) | "derived" (sémantique)
    created_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_id": self.target_id,
            "relation": self.relation,
            "weight": round(self.weight, 4),
            "origin": self.origin,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Relation":
        return cls(
            target_id=str(data.get("target_id", "")),
            relation=str(data.get("relation", RelationType.RELATES_TO.value)),
            weight=float(data.get("weight", 1.0) or 1.0),
            origin=str(data.get("origin", "explicit")),
            created_at=str(data.get("created_at", "")),
        )


@dataclass
class Revision:
    """Point de version d'une connaissance (canonisation successive)."""

    version: int
    checksum: str
    updated_at: str
    change: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {"version": self.version, "checksum": self.checksum,
                "updated_at": self.updated_at, "change": self.change}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Revision":
        return cls(
            version=int(data.get("version", 1)),
            checksum=str(data.get("checksum", "")),
            updated_at=str(data.get("updated_at", "")),
            change=str(data.get("change", "")),
        )


# --------------------------------------------------------------------------- #
# Entrée de connaissance
# --------------------------------------------------------------------------- #


@dataclass
class KnowledgeEntry:
    """Unité de connaissance consolidée, canonique, tracée, versionnée et reliée."""

    domain: str
    content: str
    id: str = field(default_factory=lambda: new_id("kno"))
    title: str = ""
    tags: List[str] = field(default_factory=list)
    confidence: float = 0.0
    status: str = "consolidated"
    version: int = 1
    created_at: str = ""
    updated_at: str = ""
    checksum: str = ""
    canonical_key: str = ""
    sources: List[SourceRef] = field(default_factory=list)
    relations: List[Relation] = field(default_factory=list)
    revisions: List[Revision] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "domain": self.domain,
            "title": self.title,
            "content": self.content,
            "tags": list(self.tags),
            "confidence": round(self.confidence, 4),
            "status": self.status,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "checksum": self.checksum,
            "canonical_key": self.canonical_key,
            "sources": [s.to_dict() for s in self.sources],
            "relations": [r.to_dict() for r in self.relations],
            "revisions": [r.to_dict() for r in self.revisions],
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeEntry":
        return cls(
            domain=str(data.get("domain", "reference")),
            content=str(data.get("content", "")),
            id=str(data.get("id") or new_id("kno")),
            title=str(data.get("title", "")),
            tags=list(data.get("tags", []) or []),
            confidence=float(data.get("confidence", 0.0) or 0.0),
            status=str(data.get("status", "consolidated")),
            version=int(data.get("version", 1)),
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", "")),
            checksum=str(data.get("checksum", "")),
            canonical_key=str(data.get("canonical_key", "")),
            sources=[SourceRef.from_dict(s) for s in data.get("sources", [])],
            relations=[Relation.from_dict(r) for r in data.get("relations", [])],
            revisions=[Revision.from_dict(r) for r in data.get("revisions", [])],
            metadata=dict(data.get("metadata", {}) or {}),
        )


__all__ = [
    "KnowledgeDomain",
    "RelationType",
    "new_id",
    "normalize_text",
    "content_checksum",
    "canonical_key",
    "MemoryLink",
    "MemoryRecord",
    "SourceRef",
    "Relation",
    "Revision",
    "KnowledgeEntry",
]
