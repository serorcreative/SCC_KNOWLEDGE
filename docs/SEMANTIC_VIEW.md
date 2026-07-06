# Vue sémantique

## Objectif (responsabilité 8)

Construire **automatiquement** le graphe reliant les connaissances (concepts,
projets, doctrines, workflows, relations) afin de préparer efficacement le
moteur de raisonnement. Déterministe et sans inférence : l'inférence reste à
`06_REASONING`.

## Structure — `semantic/graph.py`

`build_semantic_view(store, shared_tag_min, ignored_tags)` produit une
`SemanticView` :

| Élément | Contenu |
|---------|---------|
| `nodes` | une entrée = `{id, domain, title, tags, confidence}` |
| `edges` | relations **explicites** (liens mémoire) + **dérivées** (tags partagés) |
| `by_domain` | regroupement `domaine → [ids]` |
| `by_tag` | index `tag significatif → [ids]` (concepts / projets) |

Exporté en `knowledge/graph.json` via `engine.export_graph()`.

## Arêtes

- **Explicites** (`origin="explicit"`) : issues des relations portées par les
  entrées (traduction des liens mémoire).
- **Dérivées** (`origin="derived"`) : entre deux entrées partageant au moins
  `semantic_shared_tag_min` tags **significatifs**, avec `weight` = nombre de
  tags partagés et la liste `shared_tags`.

## Tags significatifs

Les tags « bruit » (noms de types et de sources : `doctrine`, `decision`,
`chatgpt`…) sont exclus via `ignored_tags` dans la configuration, afin que les
arêtes dérivées reflètent de vraies proximités thématiques (`architecture`,
`ingestion`, nom de projet…).

## Vues préparées pour le raisonnement

- **Concepts** : `by_tag` regroupe les entrées par thème.
- **Projets** : un tag de projet relie ses doctrines, décisions et workflows.
- **Domaines** : `by_domain` donne l'accès direct par nature de connaissance.

Le graphe est un **contrat de sortie stable** : `06_REASONING` le consommera —
comme KNOWLEDGE consomme MEMORY — par contrat de données, sans couplage de code.
