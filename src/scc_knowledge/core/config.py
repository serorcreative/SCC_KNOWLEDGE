"""Configuration du moteur de connaissance (JSON, sans dépendance)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from scc_knowledge.core.errors import ConfigError

ENGINE_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG_PATH = ENGINE_ROOT / "config" / "knowledge.json"


@dataclass
class KnowledgeConfig:
    """Configuration complète du moteur."""

    engine_root: Path = ENGINE_ROOT
    knowledge_path: Path = ENGINE_ROOT / "knowledge" / "knowledge.json"
    graph_path: Path = ENGINE_ROOT / "knowledge" / "graph.json"
    history_path: Path = ENGINE_ROOT / "knowledge" / "history.jsonl"
    reports_dir: Path = ENGINE_ROOT / "reports"
    logs_dir: Path = ENGINE_ROOT / "logs"

    # Politique de consolidation.
    input_status_filter: str = "validated"   # ne consolide que ce statut mémoire ("" = tous)
    canonicalize_policy: str = "highest_confidence"  # ou "longest" / "keep_existing"
    semantic_shared_tag_min: int = 1          # nb de tags partagés pour une relation dérivée
    taxonomy_overrides: Dict[str, str] = field(default_factory=dict)
    ignored_tags: List[str] = field(default_factory=list)
    extra: Dict[str, Any] = field(default_factory=dict)

    def ensure_directories(self) -> None:
        for directory in (
            self.knowledge_path.parent,
            self.graph_path.parent,
            self.history_path.parent,
            self.reports_dir,
            self.logs_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "engine_root": str(self.engine_root),
            "knowledge_path": str(self.knowledge_path),
            "graph_path": str(self.graph_path),
            "history_path": str(self.history_path),
            "reports_dir": str(self.reports_dir),
            "logs_dir": str(self.logs_dir),
            "input_status_filter": self.input_status_filter,
            "canonicalize_policy": self.canonicalize_policy,
            "semantic_shared_tag_min": self.semantic_shared_tag_min,
            "taxonomy_overrides": dict(self.taxonomy_overrides),
            "ignored_tags": list(self.ignored_tags),
        }


def _resolve(base: Path, value: str) -> Path:
    p = Path(value).expanduser()
    return p if p.is_absolute() else (base / p).resolve()


def load_config(path: Optional[Path] = None) -> KnowledgeConfig:
    """Charge la configuration JSON, avec repli sur les valeurs par défaut."""
    config = KnowledgeConfig()
    target = Path(path) if path else DEFAULT_CONFIG_PATH
    if not target.exists():
        if path is not None:
            raise ConfigError(f"Configuration introuvable : {target}")
        return config

    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"Configuration illisible ({target}) : {exc}") from exc

    base = config.engine_root
    paths = raw.get("paths", {})
    if "knowledge_path" in paths:
        config.knowledge_path = _resolve(base, paths["knowledge_path"])
    if "graph_path" in paths:
        config.graph_path = _resolve(base, paths["graph_path"])
    if "history_path" in paths:
        config.history_path = _resolve(base, paths["history_path"])
    if "reports_dir" in paths:
        config.reports_dir = _resolve(base, paths["reports_dir"])
    if "logs_dir" in paths:
        config.logs_dir = _resolve(base, paths["logs_dir"])

    config.input_status_filter = str(raw.get("input_status_filter", "validated"))
    config.canonicalize_policy = str(raw.get("canonicalize_policy", "highest_confidence"))
    config.semantic_shared_tag_min = int(raw.get("semantic_shared_tag_min", 1))
    config.taxonomy_overrides = dict(raw.get("taxonomy_overrides", {}))
    config.ignored_tags = list(raw.get("ignored_tags", []))
    config.extra = dict(raw.get("extra", {}))
    return config


__all__ = ["ENGINE_ROOT", "DEFAULT_CONFIG_PATH", "KnowledgeConfig", "load_config"]
