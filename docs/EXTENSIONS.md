# Étendre la connaissance

Extension par **ajout**, sans toucher au socle. Points d'extension : taxonomie,
politiques de canonisation, relations, vue sémantique, magasin, recherche.

## Enrichir la taxonomie

Ajouter un domaine à `KnowledgeDomain` (`core/models.py`) puis une entrée dans
`DEFAULT_TAXONOMY` (`taxonomy/classifier.py`). Ou, sans coder, mapper un type via
`taxonomy_overrides` dans `config/knowledge.json`.

## Ajouter une politique de canonisation

`canonicalize.py` connaît `highest_confidence`, `longest`, `keep_existing`. Une
nouvelle politique s'ajoute dans `_should_replace_content` et se sélectionne via
`canonicalize_policy`.

## Relations dérivées plus riches

`semantic/graph.py` dérive des relations par tags partagés. On peut ajouter
d'autres heuristiques (proximité de titre, co-domaine, cooccurrence de sources)
en enrichissant `build_semantic_view`, sans impacter la consolidation.

## Vue sémantique par embeddings

La signature `build_semantic_view(store, …) -> SemanticView` est le point
d'extension : une variante par similarité vectorielle produit le même objet, la
dépendance lourde restant isolée dans ce module.

## Remplacer le magasin

`KnowledgeStore` (fichier JSON) est remplaçable par tout objet exposant la même
interface (`get`, `put`, `find_canonical`, `entry_for_memory`, `all`, `save`,
`load`, …) : SQLite, base de graphe, base vectorielle.

## Brancher le raisonnement

`knowledge/knowledge.json` et `knowledge/graph.json` constituent le contrat de
sortie : `06_REASONING` les consomme **par contrat de données, sans couplage de
code** — exactement comme KNOWLEDGE consomme MEMORY.

## Principes à respecter

- **Consolidation, pas validation ni inférence.**
- **Rien de spécifique à une source dans le socle.**
- **Dépendances lourdes optionnelles**, isolées dans le composant concerné.
- **Une responsabilité = un module**, testable isolément.
