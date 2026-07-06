# Modèle de données

## Entrée — `MemoryRecord`

Objet de mémoire consolidable reçu de SCC_MEMORY (contrat de données).
Reconstruit via `MemoryRecord.from_dict`, tolérant. Porte ses `links` (liens
vers d'autres objets mémoire), traduits ensuite en relations de connaissance.

## Sortie — `KnowledgeEntry`

Unité de connaissance consolidée.

| Champ | Type | Rôle |
|-------|------|------|
| `id` | str | identifiant `kno_…` |
| `domain` | str | domaine taxonomique (`doctrine`, `decision`, …) |
| `title` / `content` | str | sujet et contenu |
| `tags` | list | union des tags des objets sources |
| `confidence` | float | confiance agrégée (max des sources) |
| `status` | str | `consolidated` |
| `version` | int | version du contenu (canonisations successives) |
| `created_at` / `updated_at` | str | temporalité |
| `checksum` | str | empreinte SHA-1 du contenu normalisé |
| `canonical_key` | str | clé d'identité canonique (domaine + sujet) |
| `sources` | list[`SourceRef`] | provenance : objets mémoire contributeurs |
| `relations` | list[`Relation`] | relations sortantes (explicites + dérivées) |
| `revisions` | list[`Revision`] | historique des versions |
| `metadata` | dict | métadonnées (dont `memory_type`) |

### `SourceRef` (provenance)
`memory_id`, `origin_uri`, `checksum`, `confidence`, `consolidated_at`.

### `Relation`
`target_id`, `relation`, `weight`, `origin` (`explicit` = lien mémoire /
`derived` = tags partagés), `created_at`.

### `Revision`
`version`, `checksum`, `updated_at`, `change`.

## Énumérations

- **`KnowledgeDomain`** : `doctrine`, `decision`, `workflow`, `prompt`,
  `lesson`, `project`, `concept`, `reference`.
- **`RelationType`** : `relates_to`, `part_of`, `derived_from`, `supersedes`,
  `depends_on`, `contradicts` (la relation est stockée en chaîne libre).

## Clés

- **`checksum`** = `sha1(contenu normalisé)` — suit le contenu.
- **`canonical_key`** = `sha1(domaine + sujet normalisé)`, le sujet étant le
  titre (sinon le contenu) — **ancre stable** de canonisation. Deux objets
  mémoire de même domaine et même sujet convergent vers la même connaissance.

Normalisation commune : minuscules + espaces réduits (`normalize_text`).
