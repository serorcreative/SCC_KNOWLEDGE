# SCC — Base de connaissance consolidée (`04_KNOWLEDGE`)

Module de **Seror Créative Core** consolidant la connaissance. Il reçoit les
**objets de mémoire consolidables** (statut `validated`) exportés par
[`SCC_MEMORY`](../05_MEMORY) et en construit une **connaissance consolidée,
organisée et canonique** : classée par domaine, dédupliquée, canonisée, reliée
en graphe sémantique et prête pour le raisonnement.

> Flux logique figé : **INGESTION → EXTRACTION → MEMORY → KNOWLEDGE → REASONING**

> V1 — fondation générique, modulaire et testée, **sans dépendance externe**
> (bibliothèque standard Python uniquement).

## Responsabilités

1. Promotion · 2. Taxonomie · 3. Structuration · 4. Cohérence · 5. Requêtage ·
6. Publication · 7. Canonisation · 8. Vue sémantique

## Installation

```bash
cd 04_KNOWLEDGE
python -m pip install -e ".[dev]"      # ou : export PYTHONPATH=src
```

## Ligne de commande

```bash
scc-knowledge consolidate <memory.json>   # consolide les objets mémoire validés
scc-knowledge search --domain doctrine --tags architecture
scc-knowledge show <id>                    # sources, relations, versions
scc-knowledge graph                        # exporte la vue sémantique (graph.json)
scc-knowledge conflicts                    # doublons + conflits potentiels
scc-knowledge verify                       # contrôle d'intégrité
scc-knowledge report                       # rapport de connaissance (JSON + Markdown)
```

Sans installation : `python -m scc_knowledge <commande>` (avec `PYTHONPATH=src`).

## Utilisation programmatique

```python
from scc_knowledge.engine import KnowledgeEngine

engine = KnowledgeEngine()
engine.consolidate_path("../05_MEMORY/store/memory.json")   # filtre status=validated
engine.export_graph()
for entry in engine.search(domain="doctrine"):
    print(entry.id, entry.confidence, entry.title)
```

## Connexion à SCC_MEMORY

Le moteur consomme le format de sortie de la mémoire (objets `validated`)
**sans aucune dépendance de code** : contrat de données reconstruit via
`MemoryRecord.from_dict`. Voir [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Arborescence

```
04_KNOWLEDGE/
├── src/scc_knowledge/
│   ├── core/           modèles, config, rapport, erreurs, horloge, loader
│   ├── taxonomy/       classement type mémoire → domaine
│   ├── consolidation/  promotion, canonisation, relations
│   ├── store/          base persistante + journal d'historique
│   ├── semantic/       vue sémantique (graphe)
│   ├── coherence/      doublons, conflits, intégrité
│   ├── search/         recherche
│   ├── reporting/      rapports JSON + Markdown
│   ├── engine.py       façade
│   └── cli.py          interface ligne de commande
├── config/             knowledge.json
├── knowledge/ reports/ logs/   données runtime
├── docs/               documentation détaillée
└── tests/              tests unitaires et d'intégration (pytest)
```

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/DATA_MODEL.md`](docs/DATA_MODEL.md)
- [`docs/TAXONOMY_CANONICALIZATION.md`](docs/TAXONOMY_CANONICALIZATION.md)
- [`docs/SEMANTIC_VIEW.md`](docs/SEMANTIC_VIEW.md)
- [`docs/EXTENSIONS.md`](docs/EXTENSIONS.md)

## Tests

```bash
python -m pytest -q          # 54 tests, tous verts
```

## Principes

- **Consolidation, pas validation** : la validation reste à `05_MEMORY` ;
  `04_KNOWLEDGE` consolide et organise.
- **Générique** : taxonomie et marqueurs surchargeables ; aucun code propre à
  une source.
- **Sans dépendance** : base fichier JSON et graphe remplaçables (SQLite, base
  vectorielle) derrière la même interface.
