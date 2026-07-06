# Taxonomie & canonisation

## Taxonomie (responsabilité 2)

`taxonomy/classifier.py` classe chaque objet mémoire dans un **domaine de
connaissance** selon son type. Correspondance par défaut :

| Type mémoire | Domaine |
|--------------|---------|
| `doctrine` | `doctrine` |
| `decision` | `decision` |
| `workflow` | `workflow` |
| `prompt` | `prompt` |
| `lesson` | `lesson` |
| `project_knowledge`, `project` | `project` |
| `idea`, `concept` | `concept` |
| *(inconnu)* | `reference` |

Surchargeable via `taxonomy_overrides` dans `config/knowledge.json` (aucune
connaissance n'est perdue : tout type inconnu tombe dans `reference`).

## Consolidation

Pour chaque objet mémoire (`consolidation/consolidate.py`) :

1. **domaine** = taxonomie(type) ;
2. **clé canonique** = `sha1(domaine + sujet normalisé)` ;
3. si la clé est inconnue → **promotion** (nouvelle entrée, `promote.py`) ;
4. si la clé existe → **canonisation** (fusion, `canonicalize.py`).

## Promotion (responsabilité 1)

Crée une `KnowledgeEntry` : contenu, titre, tags, confiance, `canonical_key`,
première `SourceRef` (provenance), version 1 et première révision.

## Canonisation (responsabilité 7)

Fusionne un objet mémoire compatible dans l'entrée existante :

- **provenance** : nouvelle `SourceRef` (si l'objet n'est pas déjà tracé) ;
- **tags** : union en conservant l'ordre ;
- **confiance** : maximum ;
- **titre** : adopté si absent ;
- **contenu** : remplacé selon la politique (`highest_confidence` par défaut,
  `longest`, `keep_existing`). Un changement de contenu **incrémente la version**
  et ajoute une révision (historique conservé).

Ainsi plusieurs objets mémoire compatibles deviennent **une connaissance
canonique unique**, avec historique, provenance et versions.

## Structuration des relations (responsabilité 3)

Après consolidation, `build_relations` traduit les **liens mémoire** (entre
objets mémoire) en **relations de connaissance** (entre entrées) : le lien
`m3 → m1` devient `entrée(m3) → entrée(m1)`, avec `origin="explicit"`.
Idempotent : relancer n'ajoute pas de doublon.

## Cohérence (responsabilité 4)

`coherence/conflicts.py` :

- **doublons canoniques** : entrées de même domaine partageant la clé (anomalie
  après canonisation) ;
- **conflits potentiels** : dans les domaines normatifs (`doctrine`, `decision`),
  paires au sujet proche (similarité de titre) mais au contenu divergent ;
- **intégrité** : empreintes, provenance, clés, résolution des relations.
