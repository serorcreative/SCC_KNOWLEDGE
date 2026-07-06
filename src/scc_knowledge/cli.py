"""Interface en ligne de commande du moteur de connaissance (argparse, sans dépendance).

Commandes :

* ``consolidate <memory.json>`` — consolide les objets mémoire validés ;
* ``search``                    — interroge la base ;
* ``show <id>``                 — affiche une entrée (sources, relations, versions) ;
* ``graph``                     — exporte la vue sémantique (graph.json) ;
* ``conflicts``                 — détecte doublons et conflits ;
* ``verify``                    — contrôle d'intégrité ;
* ``report``                    — écrit le rapport de connaissance ;
* ``doctor`` / ``version``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from scc_knowledge import __version__
from scc_knowledge.core.config import load_config
from scc_knowledge.core.errors import KnowledgeError
from scc_knowledge.engine import KnowledgeEngine


def _engine(args: argparse.Namespace) -> KnowledgeEngine:
    config = load_config(Path(args.config)) if getattr(args, "config", None) else load_config()
    return KnowledgeEngine(config=config)


def _cmd_consolidate(args: argparse.Namespace) -> int:
    engine = _engine(args)
    try:
        result = engine.consolidate_path(args.memory)
    except KnowledgeError as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 2
    print(
        f"Consolidation : {result.promoted} promue(s), {result.canonicalized} canonisée(s), "
        f"{result.relations_added} relation(s). Total en base : {engine.count()}."
    )
    if not args.no_graph:
        path = engine.export_graph()
        print(f"Vue sémantique → {path}")
    return 0


def _cmd_search(args: argparse.Namespace) -> int:
    engine = _engine(args)
    results = engine.search(
        domain=args.domain, tags=args.tags, text=args.text,
        min_confidence=args.min_confidence, relation=args.relation, limit=args.limit,
    )
    if not results:
        print("Aucune entrée correspondante.")
        return 0
    print(f"{len(results)} entrée(s) :")
    for e in results:
        print(f"  • [{e.domain}] {e.id} conf={e.confidence} v{e.version} — {e.title}")
    return 0


def _cmd_show(args: argparse.Namespace) -> int:
    engine = _engine(args)
    try:
        e = engine.get(args.id)
    except KnowledgeError as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 2
    print(f"{e.id}  [{e.domain}]  v{e.version}  conf={e.confidence}")
    print(f"  titre     : {e.title}")
    print(f"  tags      : {', '.join(e.tags)}")
    print(f"  sources   : {len(e.sources)} (provenance)")
    print(f"  relations : {len(e.relations)}")
    print(f"  révisions : {len(e.revisions)}")
    print(f"  contenu   : {e.content[:200]}")
    return 0


def _cmd_graph(args: argparse.Namespace) -> int:
    engine = _engine(args)
    path = engine.export_graph()
    view = engine.semantic_view().to_dict()["counts"]
    print(f"Vue sémantique → {path}")
    print(f"  nœuds={view['nodes']} arêtes={view['edges']} domaines={view['domains']} tags={view['tags']}")
    return 0


def _cmd_conflicts(args: argparse.Namespace) -> int:
    engine = _engine(args)
    result = engine.detect_conflicts()
    print(f"Doublons canoniques : {len(result.duplicates)}")
    for group in result.duplicates:
        print(f"  • {', '.join(group)}")
    print(f"Conflits potentiels : {len(result.conflicts)}")
    for conflict in result.conflicts:
        print(f"  • {conflict['a']} ↔ {conflict['b']} ({conflict['domain']}, sim={conflict['similarity']})")
    return 0


def _cmd_verify(args: argparse.Namespace) -> int:
    engine = _engine(args)
    report = engine.verify()
    for check in report.checks:
        mark = "OK " if check.passed else "ÉCHEC"
        detail = f" — {check.detail}" if check.detail else ""
        print(f"  [{mark}] {check.label}{detail}")
    print("Intégrité :", "OK" if report.ok else "PROBLÈMES DÉTECTÉS")
    return 0 if report.ok else 1


def _cmd_report(args: argparse.Namespace) -> int:
    engine = _engine(args)
    paths = engine.report(name=args.name)
    print(f"Rapport → {paths['json']}")
    print(f"         {paths['markdown']}")
    return 0


def _cmd_doctor(args: argparse.Namespace) -> int:
    engine = _engine(args)
    cfg = engine.config
    print(f"Moteur de connaissance SCC v{__version__}")
    print(f"  racine moteur  : {cfg.engine_root}")
    print(f"  base           : {cfg.knowledge_path}")
    print(f"  graphe         : {cfg.graph_path}")
    print(f"  filtre entrée  : status={cfg.input_status_filter or '*'}")
    print(f"  entrées        : {engine.count()}")
    print("  répertoires runtime : OK")
    return 0


def _cmd_version(_: argparse.Namespace) -> int:
    print(__version__)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scc-knowledge",
        description="Base de connaissance consolidée de Seror Créative Core.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_con = sub.add_parser("consolidate", help="consolide un export mémoire validé")
    p_con.add_argument("memory", help="chemin du memory.json (ou JSON/JSONL)")
    p_con.add_argument("--no-graph", action="store_true", help="ne pas exporter la vue sémantique")
    p_con.add_argument("--config")
    p_con.set_defaults(func=_cmd_consolidate)

    p_search = sub.add_parser("search", help="interroge la base")
    p_search.add_argument("--domain")
    p_search.add_argument("--tags", nargs="*")
    p_search.add_argument("--text")
    p_search.add_argument("--relation")
    p_search.add_argument("--min-confidence", type=float, dest="min_confidence")
    p_search.add_argument("--limit", type=int)
    p_search.add_argument("--config")
    p_search.set_defaults(func=_cmd_search)

    p_show = sub.add_parser("show", help="affiche une entrée de connaissance")
    p_show.add_argument("id")
    p_show.add_argument("--config")
    p_show.set_defaults(func=_cmd_show)

    p_graph = sub.add_parser("graph", help="exporte la vue sémantique")
    p_graph.add_argument("--config")
    p_graph.set_defaults(func=_cmd_graph)

    p_conf = sub.add_parser("conflicts", help="détecte doublons et conflits")
    p_conf.add_argument("--config")
    p_conf.set_defaults(func=_cmd_conflicts)

    p_verify = sub.add_parser("verify", help="contrôle d'intégrité")
    p_verify.add_argument("--config")
    p_verify.set_defaults(func=_cmd_verify)

    p_report = sub.add_parser("report", help="écrit le rapport de connaissance")
    p_report.add_argument("--name", default="knowledge")
    p_report.add_argument("--config")
    p_report.set_defaults(func=_cmd_report)

    p_doctor = sub.add_parser("doctor", help="vérifie configuration et base")
    p_doctor.add_argument("--config")
    p_doctor.set_defaults(func=_cmd_doctor)

    p_ver = sub.add_parser("version", help="affiche la version")
    p_ver.set_defaults(func=_cmd_version)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
