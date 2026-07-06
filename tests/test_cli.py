"""Tests de l'interface en ligne de commande."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scc_knowledge import __version__
from scc_knowledge.cli import main


@pytest.fixture
def config_file(tmp_path: Path) -> Path:
    cfg = {
        "paths": {
            "knowledge_path": str(tmp_path / "knowledge" / "knowledge.json"),
            "graph_path": str(tmp_path / "knowledge" / "graph.json"),
            "history_path": str(tmp_path / "knowledge" / "history.jsonl"),
            "reports_dir": str(tmp_path / "reports"),
            "logs_dir": str(tmp_path / "logs"),
        },
        "input_status_filter": "validated",
        "ignored_tags": ["doctrine", "decision"],
    }
    path = tmp_path / "cfg.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    return path


@pytest.fixture
def memory_file(tmp_path: Path) -> Path:
    store = {
        "m1": {"id": "m1", "type": "doctrine", "title": "Couplage", "content": "Ne pas coupler.",
               "status": "validated", "confidence": 0.9, "tags": ["doctrine", "architecture"]},
        "m2": {"id": "m2", "type": "decision", "title": "DB", "content": "Adopter PostgreSQL.",
               "status": "validated", "confidence": 0.8, "tags": ["decision", "architecture"],
               "links": [{"target_id": "m1", "relation": "derived_from"}]},
        "m3": {"id": "m3", "type": "idea", "content": "brouillon", "status": "candidate", "confidence": 0.3},
    }
    path = tmp_path / "memory.json"
    path.write_text(json.dumps(store), encoding="utf-8")
    return path


def test_version(capsys):
    assert main(["version"]) == 0
    assert __version__ in capsys.readouterr().out


def test_doctor(config_file: Path, capsys):
    assert main(["doctor", "--config", str(config_file)]) == 0
    assert "Moteur de connaissance SCC" in capsys.readouterr().out


def test_consolidate_search_graph_verify(memory_file: Path, config_file: Path, tmp_path: Path, capsys):
    # consolidate (m3 candidate est filtré)
    assert main(["consolidate", str(memory_file), "--config", str(config_file)]) == 0
    out = capsys.readouterr().out
    assert "promue" in out
    assert (tmp_path / "knowledge" / "knowledge.json").exists()
    assert (tmp_path / "knowledge" / "graph.json").exists()

    # search
    assert main(["search", "--domain", "doctrine", "--config", str(config_file)]) == 0
    out = capsys.readouterr().out
    assert "doctrine" in out
    entry_id = "kno_" + out.split("kno_")[1].split()[0]

    # show
    assert main(["show", entry_id, "--config", str(config_file)]) == 0
    assert "relations" in capsys.readouterr().out

    # graph
    assert main(["graph", "--config", str(config_file)]) == 0
    assert "sémantique" in capsys.readouterr().out.lower()

    # verify
    assert main(["verify", "--config", str(config_file)]) == 0
    assert "Intégrité" in capsys.readouterr().out


def test_conflicts_and_report(memory_file: Path, config_file: Path, tmp_path: Path, capsys):
    main(["consolidate", str(memory_file), "--config", str(config_file)])
    capsys.readouterr()
    assert main(["conflicts", "--config", str(config_file)]) == 0
    assert "Doublons" in capsys.readouterr().out
    assert main(["report", "--config", str(config_file)]) == 0
    assert (tmp_path / "reports" / "knowledge.json").exists()
