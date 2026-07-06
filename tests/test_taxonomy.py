"""Tests de la taxonomie (type mémoire → domaine)."""

from __future__ import annotations

from scc_knowledge.core.models import KnowledgeDomain
from scc_knowledge.taxonomy.classifier import classify_domain


def test_default_mapping():
    assert classify_domain("doctrine") is KnowledgeDomain.DOCTRINE
    assert classify_domain("decision") is KnowledgeDomain.DECISION
    assert classify_domain("workflow") is KnowledgeDomain.WORKFLOW
    assert classify_domain("prompt") is KnowledgeDomain.PROMPT
    assert classify_domain("lesson") is KnowledgeDomain.LESSON
    assert classify_domain("project_knowledge") is KnowledgeDomain.PROJECT
    assert classify_domain("idea") is KnowledgeDomain.CONCEPT


def test_unknown_falls_back_to_reference():
    assert classify_domain("task") is KnowledgeDomain.REFERENCE
    assert classify_domain("n_importe_quoi") is KnowledgeDomain.REFERENCE
    assert classify_domain("") is KnowledgeDomain.REFERENCE


def test_case_insensitive():
    assert classify_domain("DOCTRINE") is KnowledgeDomain.DOCTRINE


def test_override():
    assert classify_domain("task", {"task": "workflow"}) is KnowledgeDomain.WORKFLOW
    # Override invalide → reference.
    assert classify_domain("task", {"task": "inconnu"}) is KnowledgeDomain.REFERENCE
