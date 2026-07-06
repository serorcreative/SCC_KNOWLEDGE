"""Tests de la vue sémantique (graphe)."""

from __future__ import annotations

from pathlib import Path

from scc_knowledge.core.models import KnowledgeEntry, Relation
from scc_knowledge.semantic.graph import build_semantic_view
from scc_knowledge.store.store import KnowledgeStore


def _store(tmp_path: Path) -> KnowledgeStore:
    store = KnowledgeStore(tmp_path / "k.json")
    store.put(KnowledgeEntry(domain="doctrine", id="A", title="A", content="a",
                             tags=["architecture", "doctrine"], confidence=0.9, canonical_key="a"))
    store.put(KnowledgeEntry(domain="decision", id="B", title="B", content="b",
                             tags=["architecture", "decision"], confidence=0.8, canonical_key="b",
                             relations=[Relation(target_id="A", relation="derived_from", origin="explicit")]))
    store.put(KnowledgeEntry(domain="workflow", id="C", title="C", content="c",
                             tags=["ingestion"], confidence=0.7, canonical_key="c"))
    return store


def test_nodes_and_domains(tmp_path: Path):
    view = build_semantic_view(_store(tmp_path))
    assert {n["id"] for n in view.nodes} == {"A", "B", "C"}
    assert set(view.by_domain) == {"doctrine", "decision", "workflow"}


def test_explicit_edge_present(tmp_path: Path):
    view = build_semantic_view(_store(tmp_path))
    explicit = [e for e in view.edges if e["origin"] == "explicit"]
    assert any(e["source"] == "B" and e["target"] == "A" for e in explicit)


def test_derived_edge_from_shared_tags(tmp_path: Path):
    # A et B partagent « architecture » → arête dérivée (ignorer les tags de domaine).
    view = build_semantic_view(_store(tmp_path), shared_tag_min=1, ignored_tags=["doctrine", "decision"])
    derived = [e for e in view.edges if e["origin"] == "derived"]
    assert any({e["source"], e["target"]} == {"A", "B"} for e in derived)
    # C ne partage aucun tag significatif → pas d'arête dérivée le concernant.
    assert not any("C" in {e["source"], e["target"]} for e in derived)


def test_by_tag_index_excludes_ignored(tmp_path: Path):
    view = build_semantic_view(_store(tmp_path), ignored_tags=["doctrine", "decision"])
    assert "architecture" in view.by_tag
    assert "doctrine" not in view.by_tag  # tag ignoré


def test_to_dict_counts(tmp_path: Path):
    view = build_semantic_view(_store(tmp_path))
    counts = view.to_dict()["counts"]
    assert counts["nodes"] == 3
    assert counts["edges"] >= 1
