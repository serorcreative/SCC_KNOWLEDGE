"""Taxonomie : classement d'un objet mémoire dans un domaine de connaissance.

La correspondance ``type mémoire → domaine`` est déterministe et surchargeable
par configuration (``taxonomy_overrides``). Tout type inconnu tombe dans
``REFERENCE`` (aucune connaissance n'est perdue).
"""

from __future__ import annotations

from typing import Dict, Optional

from scc_knowledge.core.models import KnowledgeDomain

# Correspondance par défaut : types d'extraction/mémoire → domaines.
DEFAULT_TAXONOMY: Dict[str, KnowledgeDomain] = {
    "doctrine": KnowledgeDomain.DOCTRINE,
    "decision": KnowledgeDomain.DECISION,
    "workflow": KnowledgeDomain.WORKFLOW,
    "prompt": KnowledgeDomain.PROMPT,
    "lesson": KnowledgeDomain.LESSON,
    "project_knowledge": KnowledgeDomain.PROJECT,
    "project": KnowledgeDomain.PROJECT,
    "idea": KnowledgeDomain.CONCEPT,
    "concept": KnowledgeDomain.CONCEPT,
}


def classify_domain(
    memory_type: str, overrides: Optional[Dict[str, str]] = None
) -> KnowledgeDomain:
    """Retourne le domaine de connaissance d'un type mémoire.

    Les surcharges (``overrides``) priment sur la table par défaut ; un type
    inconnu retourne :attr:`KnowledgeDomain.REFERENCE`.
    """
    key = (memory_type or "").strip().lower()
    if overrides and key in overrides:
        try:
            return KnowledgeDomain(overrides[key])
        except ValueError:
            return KnowledgeDomain.REFERENCE
    return DEFAULT_TAXONOMY.get(key, KnowledgeDomain.REFERENCE)


__all__ = ["DEFAULT_TAXONOMY", "classify_domain"]
