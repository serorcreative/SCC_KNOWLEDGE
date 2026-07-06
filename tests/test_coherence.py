"""Tests de cohérence : doublons, conflits, intégrité."""

from __future__ import annotations

from pathlib import Path

from scc_knowledge.coherence.conflicts import detect_conflicts, verify_integrity
from scc_knowledge.consolidation.promote import record_initial_revision
from scc_knowledge.core.models import KnowledgeEntry, Relation, SourceRef
from scc_knowledge.store.store import KnowledgeStore


def _valid_entry(**kw) -> KnowledgeEntry:
    base = dict(domain="doctrine", content="contenu", canonical_key="ck")
    base.update(kw)
    e = KnowledgeEntry(**base)
    e.sources.append(SourceRef(memory_id="m1"))
    record_initial_revision(e, "t0")
    return e


def test_integrity_ok(tmp_path: Path):
    store = KnowledgeStore(tmp_path / "k.json")
    store.put(_valid_entry(id="A"))
    assert verify_integrity(store).ok


def test_integrity_detects_tampered_checksum(tmp_path: Path):
    store = KnowledgeStore(tmp_path / "k.json")
    e = _valid_entry(id="A")
    e.content = "modifié sans recalcul"
    store.put(e)
    report = verify_integrity(store)
    assert not report.ok
    assert any(c.label == "empreintes" and not c.passed for c in report.checks)


def test_integrity_detects_dangling_relation(tmp_path: Path):
    store = KnowledgeStore(tmp_path / "k.json")
    e = _valid_entry(id="A")
    e.relations.append(Relation(target_id="INEXISTANT"))
    store.put(e)
    report = verify_integrity(store)
    assert any(c.label == "relations résolues" and not c.passed for c in report.checks)


def test_detect_duplicates(tmp_path: Path):
    store = KnowledgeStore(tmp_path / "k.json")
    # Deux entrées de même domaine + même clé canonique (anomalie).
    store.put(_valid_entry(id="A", canonical_key="same"))
    store.put(_valid_entry(id="B", canonical_key="same"))
    result = detect_conflicts(store)
    assert any(set(group) == {"A", "B"} for group in result.duplicates)


def test_detect_conflicts_similar_title_divergent_content(tmp_path: Path):
    store = KnowledgeStore(tmp_path / "k.json")
    store.put(_valid_entry(id="A", title="politique de déploiement", content="déployer le vendredi", canonical_key="k1"))
    store.put(_valid_entry(id="B", title="politique de déploiement", content="ne jamais déployer le vendredi", canonical_key="k2"))
    result = detect_conflicts(store, similarity_threshold=0.6)
    assert any({c["a"], c["b"]} == {"A", "B"} for c in result.conflicts)
