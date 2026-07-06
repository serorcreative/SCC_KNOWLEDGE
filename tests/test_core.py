"""Tests du noyau : modèles, loader, config, horloge."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scc_knowledge.core.clock import FixedClock, SystemClock
from scc_knowledge.core.config import load_config
from scc_knowledge.core.errors import ConfigError, LoaderError
from scc_knowledge.core.loader import load
from scc_knowledge.core.models import (
    KnowledgeEntry,
    MemoryRecord,
    canonical_key,
    content_checksum,
    normalize_text,
)


def test_normalize_and_checksum_stable():
    assert normalize_text("  Hello   WORLD ") == "hello world"
    assert content_checksum("a b") == content_checksum(" A   B ")


def test_canonical_key_uses_title_then_content():
    k1 = canonical_key("doctrine", "Titre", "contenu")
    k2 = canonical_key("doctrine", "  titre ", "autre contenu")  # même titre normalisé
    assert k1 == k2
    k3 = canonical_key("decision", "Titre", "contenu")  # domaine différent
    assert k3 != k1
    # Sans titre : basé sur le contenu.
    assert canonical_key("doctrine", "", "x") == canonical_key("doctrine", "", " X ")


def test_memory_record_from_dict_with_links():
    rec = MemoryRecord.from_dict(
        {"type": "decision", "content": "c", "id": "m1",
         "links": [{"target_id": "m2", "relation": "derived_from"}], "unknown": 1}
    )
    assert rec.id == "m1"
    assert rec.links[0].target_id == "m2"
    assert rec.status == "validated"


def test_knowledge_entry_roundtrip():
    e = KnowledgeEntry(domain="doctrine", content="c", title="t")
    restored = KnowledgeEntry.from_dict(e.to_dict())
    assert restored.domain == "doctrine"
    assert json.loads(json.dumps(e.to_dict()))["title"] == "t"


def test_loader_memory_json_dict_with_status_filter(tmp_path: Path):
    store = {
        "m1": {"id": "m1", "type": "doctrine", "content": "a", "status": "validated"},
        "m2": {"id": "m2", "type": "idea", "content": "b", "status": "candidate"},
    }
    f = tmp_path / "memory.json"
    f.write_text(json.dumps(store), encoding="utf-8")
    records = load(f, status_filter="validated")
    assert [r.id for r in records] == ["m1"]  # candidate filtré


def test_loader_no_filter(tmp_path: Path):
    store = {"m1": {"id": "m1", "type": "doctrine", "content": "a", "status": "candidate"}}
    f = tmp_path / "memory.json"
    f.write_text(json.dumps(store), encoding="utf-8")
    assert len(load(f, status_filter=None)) == 1


def test_loader_list_and_jsonl(tmp_path: Path):
    lst = tmp_path / "l.json"
    lst.write_text(json.dumps([{"id": "m1", "type": "doctrine", "content": "a", "status": "validated"}]), encoding="utf-8")
    assert len(load(lst)) == 1

    jl = tmp_path / "l.jsonl"
    jl.write_text(json.dumps({"id": "m1", "type": "doctrine", "content": "a", "status": "validated"}) + "\n", encoding="utf-8")
    assert len(load(jl)) == 1


def test_loader_missing_and_bad(tmp_path: Path):
    with pytest.raises(LoaderError):
        load(tmp_path / "absent.json")
    bad = tmp_path / "bad.jsonl"
    bad.write_text('{"ok":1}\n{bad}\n', encoding="utf-8")
    with pytest.raises(LoaderError):
        load(bad)


def test_config_defaults_and_missing(tmp_path: Path):
    assert load_config().input_status_filter == "validated"
    with pytest.raises(ConfigError):
        load_config(tmp_path / "absent.json")


def test_clocks():
    c = FixedClock(step=1)
    assert c.now() < c.now()
    assert "T" in SystemClock().now()
