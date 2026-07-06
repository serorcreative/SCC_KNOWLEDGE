# Architecture de la connaissance consolidée SCC

## Objectif

Recevoir les **objets de mémoire consolidables** (statut `validated`) de
SCC_MEMORY et en construire une **connaissance consolidée** : canonique, classée
par domaine, dédupliquée, reliée en graphe sémantique et prête pour le
raisonnement.

## Position dans le flux SCC (figé)

```
INGESTION → EXTRACTION → MEMORY → KNOWLEDGE → REASONING
                          (validated)  (consolidée)
```

MEMORY valide et historise ; KNOWLEDGE **consolide et organise**. La distinction
est nette : aucune re-validation ici, aucune inférence (réservée à REASONING).

## Contrat de données (couplage faible)

Le moteur ne connaît que le *format* de sortie de la mémoire (objet mémoire),
reconstruit via `MemoryRecord.from_dict(dict)` — tolérant. Il **n'importe pas**
SCC_MEMORY. Seuls les objets au statut configuré (`validated` par défaut) sont
consolidés.

Champs consommés : `id`, `type`, `title`, `content`, `status`, `confidence`,
`tags`, `origin_uri`, `checksum`, `links`, `metadata`.

## Couches

| Couche | Rôle | Module |
|--------|------|--------|
| **Core** | Modèles, config, rapport, erreurs, horloge, chargement | `scc_knowledge.core` |
| **Taxonomy** | Classement type mémoire → domaine | `scc_knowledge.taxonomy` |
| **Consolidation** | Promotion, canonisation, relations | `scc_knowledge.consolidation` |
| **Store** | Base persistante + journal d'historique | `scc_knowledge.store` |
| **Semantic** | Vue sémantique (graphe) | `scc_knowledge.semantic` |
| **Coherence** | Doublons, conflits, intégrité | `scc_knowledge.coherence` |
| **Search** | Recherche multi-critères | `scc_knowledge.search` |
| **Reporting / Façade / CLI** | Rapports, API, ligne de commande | `reporting`, `engine.py`, `cli.py` |

## Les huit responsabilités, où elles vivent

| # | Responsabilité | Emplacement |
|---|----------------|-------------|
| 1 | Promotion | `consolidation/promote.py` |
| 2 | Taxonomie | `taxonomy/classifier.py` |
| 3 | Structuration (relations) | `consolidation/consolidate.py` (`build_relations`) |
| 4 | Cohérence | `coherence/conflicts.py` |
| 5 | Requêtage | `search/query.py` |
| 6 | Publication | `store` + `engine.export_graph` + `reporting` |
| 7 | Canonisation | `consolidation/canonicalize.py` |
| 8 | Vue sémantique | `semantic/graph.py` |

## Décisions d'architecture

1. **Découplage par contrat de données** : dépôts Git séparés, évolutions
   indépendantes.
2. **Clé canonique** = `domaine + sujet normalisé` : ancre stable de fusion des
   connaissances compatibles.
3. **Relations en deux temps** : consolidation d'abord, puis traduction des
   liens mémoire en relations de connaissance (les cibles existent alors).
4. **Vue sémantique déterministe** : relations explicites + relations dérivées
   par tags partagés, sans inférence — le raisonnement reste à REASONING.
5. **Base fichier JSON** remplaçable derrière l'interface `KnowledgeStore`.

## Voir aussi

- Modèle de données → [`DATA_MODEL.md`](DATA_MODEL.md)
- Taxonomie & canonisation → [`TAXONOMY_CANONICALIZATION.md`](TAXONOMY_CANONICALIZATION.md)
- Vue sémantique → [`SEMANTIC_VIEW.md`](SEMANTIC_VIEW.md)
- Étendre → [`EXTENSIONS.md`](EXTENSIONS.md)
