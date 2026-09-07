"""Contenu éditorial de l'onglet "Contexte & Théorie" de l'interface Streamlit.

Séparé de la logique de rendu (streamlit_app.py) pour rester facile à enrichir —
notamment à partir du rendu de stage une fois disponible.
"""

PROJECT_FACTS = [
    ("⏱️", "6 semaines", ""),
    ("🧩", "4 modules", ""),
    ("🎯", "7 attaques", ""),
    ("🔌", "2 backends", ""),
]

PIPELINE_MODULES = [
    {
        "icon": "",
        "title": "M3 — Indexation",
        "summary": "Vectorisation et stockage des documents dans ChromaDB, avec classification de sensibilité dès l'insertion.",
    },
    {
        "icon": "",
        "title": "M6 — Retriever",
        "summary": "Recherche des chunks les plus proches sémantiquement de la question, via un bi-encodeur (similarité cosinus).",
    },
    {
        "icon": "",
        "title": "M7 — Reranking",
        "summary": "Étape optionnelle : un cross-encodeur ré-ordonne les documents candidats pour affiner leur pertinence réelle.",
    },
    {
        "icon": "",
        "title": "M8 — Génération",
        "summary": "Le LLM formule la réponse à partir des chunks retenus, sous contrôle de guardrails et de pré-/post-génération.",
    },
]

MODULE_DEEP_DIVES = [
    {
        "title": " M3 — Indexation : la porte d'entrée du RAG",
        "body": (
            "**Rôle.** L'indexeur vectorise les documents et les stocke dans une base vectorielle "
            "(ChromaDB). C'est ici que la donnée entre dans le pipeline.\n\n"
            "**Limite de sécurité.** Une fois convertie en embedding, une donnée perd totalement sa "
            "provenance : impossible de savoir *a posteriori* d'où elle vient ni si elle est légitime. "
            "C'est pour compenser cette perte que le framework attache une métadonnée de classification "
            "(`sensibility: easy | critical`) à chaque chunk dès l'indexation, plutôt que d'essayer de la "
            "reconstituer plus tard dans le pipeline."
        ),
    },
    {
        "title": " M6 — Retriever : comparer, pas comprendre",
        "body": (
            "**Rôle.** Le retriever compare le vecteur de la question aux vecteurs de toute la base, et "
            "ne conserve que les plus proches (similarité cosinus).\n\n"
            "**Comment le bi-encodeur fonctionne.** Chunk et question sont vectorisés **séparément** — le "
            "modèle apprend une proximité de *contexte d'usage*, pas un raisonnement logique.\n\n"
            "**Limites.**\n"
            "- *Insensibilité aux nuances logiques* : « chaud » et « froid » s'utilisent dans des phrases "
            "similaires, donc leur similarité est mathématiquement élevée — alors qu'ils sont logiquement "
            "opposés.\n"
            "- *Aucun jugement d'innocuité* : le retriever ne sait pas distinguer un chunk légitime d'un "
            "chunk piégé s'ils sont sémantiquement proches de la question."
        ),
    },
    {
        "title": " M7 — Reranking : affiner, pas filtrer le contenu malveillant",
        "body": (
            "**Rôle.** Le cross-encodeur concatène question et document (`[CLS] Question [SEP] Document "
            "[SEP]`) et laisse chaque mot du document \"voir\" chaque mot de la question (attention "
            "croisée) — bien plus fin que le bi-encodeur, mais aussi bien plus coûteux en calcul.\n\n"
            "**Limite de sécurité.** Le score produit mesure la pertinence *topique*, jamais la "
            "bienveillance du contenu. Un document piégé, si son vocabulaire est topiquement aligné avec "
            "la question, peut obtenir un score de reranking équivalent — voire supérieur — à un document "
            "légitime. Un attaquant connaissant les questions fréquentes peut même optimiser un document "
            "piégé pour maximiser artificiellement ce score."
        ),
    },
    {
        "title": " M8 — Génération : la porte de sortie, la plus vulnérable",
        "body": (
            "**Rôle.** Dernière étape : le LLM reformule les chunks retenus en réponse. C'est là que le "
            "monde extérieur (utilisateur, modèle) et l'architecture se rencontrent — surface d'attaque "
            "maximale (MIA, DAN, Role Hijacking, injection...).\n\n"
            "**Dispositifs défensifs implémentés :**\n"
            "- Rôles `SYSTEM` / `USER` / `ASSISTANT` clairement structurés.\n"
            "- Balises dédiées (`<contenu_externe_non_fiable>...</contenu_externe_non_fiable>`) autour des "
            "chunks récupérés : à lire, jamais à exécuter.\n"
            "- Instruction système défensive explicite (rôle, interdiction de citer mot pour mot, ignorer "
            "toute instruction contenue dans les données).\n"
            "- Post-génération : si la réponse est trop proche d'un chunk source, elle est **reformulée**, "
            "jamais simplement bloquée — un blocage donnerait à un attaquant un signal exploitable sur la "
            "présence d'un chunk sensible."
        ),
    },
]

QUIZ_QUESTIONS = [
    {
        "question": "Que signifie l'acronyme RAG dans ce contexte ?",
        "options": [
            "Retrieval-Augmented Generation",
            "Random Answer Generator",
            "Ranked Attention Gateway",
            "Rapid API Gateway",
        ],
        "answer": 0,
        "explication": (
            "RAG = Retrieval-Augmented Generation : on enrichit la réponse d'un LLM avec des documents "
            "récupérés dans une base de connaissances, au lieu de compter uniquement sur ce qu'il a appris "
            "pendant son entraînement."
        ),
    },
    {
        "question": "À quoi sert le module de Reranking (M7) ?",
        "options": [
            "À vérifier l'innocuité du contenu des documents",
            "À affiner la pertinence des documents remontés par le retriever, via un cross-encodeur",
            "À chiffrer les documents avant stockage",
            "À générer la réponse finale à la place du LLM",
        ],
        "answer": 1,
        "explication": (
            "Le cross-encodeur compare question et document ensemble (attention croisée) pour affiner la "
            "pertinence topique — mais il ne juge jamais si un contenu est malveillant."
        ),
    },
    {
        "question": "Quel est le principe d'une attaque Membership Inference (MIA) ?",
        "options": [
            "Injecter un document piégé dans la base",
            "Déterminer si une information précise est présente dans la base vectorielle, sans y avoir directement accès",
            "Faire planter le serveur ChromaDB",
            "Voler la clé API Azure",
        ],
        "answer": 1,
        "explication": (
            "Une MIA cherche à confirmer la présence d'un chunk en base — via les distances de similarité "
            "(White-Box) ou une complétion de texte détournée (Black-Box) — sans jamais lire directement la "
            "base."
        ),
    },
    {
        "question": "Le Prompt Injection indirecte repose sur...",
        "options": [
            "Un document piégé injecté dans la base, remonté par le retriever puis interprété par le LLM comme une instruction légitime",
            "Une faille réseau dans ChromaDB",
            "Un mot de passe faible sur le compte Azure",
            "Une attaque par force brute sur le modèle d'embedding",
        ],
        "answer": 0,
        "explication": (
            "C'est la seule attaque du framework qui mobilise toute la pipeline : indexation d'un document "
            "malveillant, remontée par le retriever, puis interprétation des instructions cachées par le LLM."
        ),
    },
    {
        "question": (
            "Quel dispositif encadre les données récupérées pour que le LLM les traite comme des données "
            "à lire, jamais des instructions à exécuter ?"
        ),
        "options": [
            "Le reranking",
            "Les balises système (guardrails), ex. <contenu_externe_non_fiable>",
            "Le chiffrement AES des embeddings",
            "La limite de longueur du prompt",
        ],
        "answer": 1,
        "explication": (
            "Les balises système encadrent explicitement les chunks récupérés pour que le LLM ne confonde "
            "jamais donnée et instruction — c'est le paramètre « guardrails » du module Génération."
        ),
    },
    {
        "question": (
            "Pourquoi la post-génération reformule-t-elle la réponse plutôt que de simplement la bloquer "
            "en cas de fuite détectée ?"
        ),
        "options": [
            "Pour économiser des appels API",
            "Pour ne pas donner à un attaquant un signal exploitable sur la présence d'un chunk sensible",
            "Parce que bloquer une réponse est techniquement impossible",
            "Pour améliorer la vitesse de réponse",
        ],
        "answer": 1,
        "explication": (
            "Un simple blocage confirmerait indirectement à l'attaquant qu'il a touché juste (un « oracle » "
            "exploitable) — la reformulation évite ce signal tout en retirant l'information sensible."
        ),
    },
]
