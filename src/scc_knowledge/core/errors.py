"""Hiérarchie d'exceptions du moteur de connaissance."""

from __future__ import annotations


class KnowledgeError(Exception):
    """Erreur de base pour toute défaillance du moteur de connaissance."""


class ConfigError(KnowledgeError):
    """Configuration absente, illisible ou invalide."""


class LoaderError(KnowledgeError):
    """Un objet mémoire n'a pas pu être chargé ou décodé."""


class StoreError(KnowledgeError):
    """Défaillance de persistance de la base de connaissance."""


class NotFoundError(KnowledgeError):
    """Entrée de connaissance introuvable."""


class RelationError(KnowledgeError):
    """Création de relation invalide (cible absente, auto-relation, doublon)."""


__all__ = [
    "KnowledgeError",
    "ConfigError",
    "LoaderError",
    "StoreError",
    "NotFoundError",
    "RelationError",
]
