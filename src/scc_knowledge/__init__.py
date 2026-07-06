"""SCC Knowledge — base de connaissance consolidée de Seror Créative Core.

Reçoit les **objets de mémoire consolidables** exportés par SCC_MEMORY (statut
``validated``) et en construit une **connaissance consolidée, organisée et
canonique** : classée par domaine, dédupliquée, canonisée, reliée en graphe
sémantique et prête pour le moteur de raisonnement.

Position dans le flux SCC (figé) :

    INGESTION → EXTRACTION → MEMORY → KNOWLEDGE → REASONING

Responsabilités :

1. Promotion — objet mémoire consolidable → entrée de connaissance ;
2. Taxonomie — classement par domaine (doctrine, décision, workflow, …) ;
3. Structuration — relations entre entrées + terminologie ;
4. Cohérence — détection de conflits et de doublons canoniques ;
5. Requêtage — recherche par domaine, tag, relation, texte ;
6. Publication — export stable consommable par le raisonnement ;
7. Canonisation — fusion d'objets mémoire compatibles en une connaissance
   canonique unique (historique, provenance, versions) ;
8. Vue sémantique — graphes de concepts, projets, doctrines, workflows et
   relations, préparant le moteur de raisonnement.

Le moteur est *conceptuellement* connecté à SCC_MEMORY mais **découplé au
niveau du code** : il ne connaît que le *format* de sortie de la mémoire
(contrat de données, voir :mod:`scc_knowledge.core.loader`).
"""

from __future__ import annotations

__version__ = "1.0.0"

__all__ = ["__version__"]
