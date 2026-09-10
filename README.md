# L'architecture RAG modulable présente dans le Framework

## Préambule

Le développement de ce framework s'inscrit dans le cadre d'un stage d'une durée de 6 semaines, effectué par un étudiant en deuxième année d'école d'informatique. L'objectif est de réaliser un framework simulant un environnement RAG complet, constitué de modules indépendants dont les paramètres sont individuellement modifiables. Ce framework permet ainsi de comprendre concrètement l'impact de différentes attaques sur une architecture RAG. Le point de vue est offensif, dans l'idée de mieux comprendre les attaques et les protections efficaces afin de rendre les RAG de demain plus sécurisés.

## Installation rapide

```powershell
# Créer et activer l'environnement virtuel Python
python -m venv rag-env
.\rag-env\Scripts\Activate.ps1

# Installer les dépendances
pip install -r requirements.txt

# Lancer les conteneurs Docker (ollama + chromadb)
docker compose up -d

# Extraire l'archive de données fournie
Expand-Archive -Path .\chroma_data.zip -DestinationPath .\chroma_export

# Importer les données dans le conteneur chromadb
docker cp .\chroma_export\. chromadb:/data
docker restart chromadb

# Lance l'application
streamlit run .\streamlit_app.py
```

Vérifier que tout fonctionne en ouvrant cette URL dans un navigateur (doit renvoyer un nombre de documents supérieur à 0) :

```
http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections
```
---

## Découverte de l'architecture

### Introduction

Cette partie permet de découvrir les modules disponibles à l'utilisation du Framework.

La totalité des scripts sont développés à l'aide du langage Python, les différentes dépendances utilisées sont à retrouver dans le `requirement.txt`. Nous retrouvons :

- **Requests**, pour effectuer les appels HTTP vers les API de la base vectorielle (ChromaDB) et du serveur Ollama.
- **Feedparser**, utilisé pour sourcer la donnée en provenance des flux RSS.
- **Sentence-Transformers**, pour l'utilisation du cross-encodeur durant le reranking.

Dans celui-ci, vous retrouverez deux dossiers principaux :

- **`/common`**, qui vous permettra de retrouver l'ensemble des composants constituant votre RAG (initialisation, indexeur, retriever, génération…).
- **`/attack`**, stockant les différentes attaques développées ou prévues sur les architectures RAG (Membership Inference Attack, Prompt Injection, et d'autres attaques du Top 10 OWASP à venir).
- **`/script`**, hébergeant les différents launchers des attaques simulées. 
- **`/ui`**, contenant le contenu pédagogique et les fonctions utilitaires de l'interface graphique.

### Configuration Azure OpenAI

La génération (`common/generation.py`, `common/post_generation.py`) passe par Azure OpenAI. Les embeddings
(Retriever/Indexeur) continuent d'utiliser Ollama en local. Créez un fichier `.env` à la racine du projet
(non versionné, voir `.gitignore`) avec :

```
AZURE_OPENAI_API_ENDPOINT=https://<votre-ressource>.openai.azure.com
AZURE_OPENAI_API_KEY=<votre-clé>
AZURE_OPENAI_API_VERSION=<version-api, ex: 2024-02-15-preview>
AZURE_OPENAI_DEPLOYMENT_NAME=<nom-du-déploiement>
```

### Interface graphique (Streamlit)

Une interface graphique Streamlit permet de piloter le framework sans écrire de code, utile pour une démonstration à un public non technique. Elle propose deux pages :

- **Chat libre** : live prompting sur la cible RAG construite dans l'autre onglet — chaque message traverse tout le pipeline configuré (retriever, guardrails, pré-/post-génération). Nécessite d'avoir construit une cible au préalable.
- **Cible RAG & Attaques** : construction d'une cible RAG module par module (Initialisation, Indexation, Retriever avec reranking optionnel, Génération avec guardrails / pré- / post-génération), puis sélection et lancement d'une attaque avec un résultat structuré et un bloc pédagogique (description, contre-mesure, exemple) qui se met à jour selon l'attaque choisie.

**Lancement :**

```bash
docker compose up -d          # démarre ChromaDB et Ollama
pip install -r requirements.txt
# créer le fichier .env (voir section Configuration Azure OpenAI ci-dessus)
streamlit run streamlit_app.py
```

L'interface est ensuite accessible sur `http://localhost:8501`.

### Initialisation

La présence d'une classe `Initialisation` a pour objectif de créer l'environnement responsable du stockage des données dans la base vectorielle. Pour cela, vous retrouverez un objet `Initialisation` prenant en attribut `nom_collection`, et possédant de multiples fonctions :

- `creation()` permet de créer la collection avec le nom renseigné en attribut.
- `recuperer_id()` permet de récupérer l'identifiant de la collection créée.
- `afficher_informations()` retourne le nom et l'identifiant de la collection à l'écran.
- `supprimer()` afin de supprimer la collection ainsi que l'ensemble des données qu'elle contient.

**Exemple d'utilisation :**

```python
from common.initialisation import Initialisation

rag_db = Initialisation("CGI_collection")
rag_db.creation()
rag_db.afficher_informations()
```

### Indexation

La classe `Indexeur` a pour responsabilité d'offrir une gestion autour de la data. C'est dans cette classe que les données sont récupérées (en flux RSS uniquement), classifiées, vectorisées et stockées dans la base vectorielle. Pour l'utiliser, l'`Indexeur` attend en attribut une URL (`flux_rss`) et un identifiant pour le lieu de stockage (`collection_id`). Elle met à notre disposition des fonctions telles que :

- `feed_rss()` qui récupère les articles du flux RSS et les stocke dans un dictionnaire ayant pour clefs `title`, `content` et `sensibility`.
- `classify(text)` qui retourne la catégorisation de sensibilité du document à l'aide de la présence ou non des mots interdits dans le contenu du chunk.
- `insert_data()` responsable de la vectorisation du contenu et du stockage dans la collection, en récupérant automatiquement les données à l'aide des autres fonctions.
- `listening_data_db()` qui liste le contenu de la collection.

**Exemple d'utilisation :**

```python
from common.indexation import Indexeur
from common.initialisation import Initialisation

rag_db = Initialisation("CGI_collection")
index_rag = Indexeur("https://rmcsport.bfmtv.com/rss/football/euro/", rag_db.recuperer_id())
index_rag.insert_data()
```

### Retriever

Le retriever est une étape de récupération de données dans la base vectorielle à l'aide d'un prompt utilisateur. Son objectif est simple : proposer à l'étape de génération les vecteurs les plus proches mathématiquement de la question de l'utilisateur. Pour simuler cela, nous avons créé une classe `Retriever` prenant en attribut : un identifiant de collection (`id_collection`), un modèle de vectorisation (`embedding_model`, ayant pour valeur par défaut `nomic-embed-text`), un booléen pour le choix d'activer l'étape de reranking (`use_reranker`, ayant pour valeur par défaut `False`), et un booléen afin de déterminer les droits d'accès aux documents de l'utilisateur (`user_is_admin`, ayant pour valeur par défaut `False`). Nous retrouvons également des fonctions comme :

- `embed(text)` afin de vectoriser un texte à l'aide du modèle choisi.
- `retriever(query, top_k_init)` responsable de l'étape de récupération des données.
- `rerank(query, chunks, metadatas, distances, top_k)`, étape qui gère le reranking via le cross-encodeur.

**Exemple d'utilisation :**

```python
from common.initialisation import Initialisation
from common.retriever import Retriever

rag_db = Initialisation("CGI_collection")
rag_db.creation()
retriever_rag = Retriever(rag_db.recuperer_id(), use_reranker=False, user_is_admin=True)
retriever_rag.retriever("Score France-Portugal", top_k_init=5)
```

### Pre-Génération

L'étape de pré-génération intervient en amont de la transmission des `top_k` au module M8 (Génération). Elle permet d'effectuer un contrôle sur les données qui vont être proposées à l'étape suivante. Son objectif est de vérifier si les droits de l'utilisateur et les permissions associées aux documents remontés sont cohérents. À noter qu'un filtrage a déjà eu lieu en amont, lors de l'étape de Retriever, mais nous recontrôlons au cas où !

La classe `Pre-génération` attend un attribut (`user_is_admin`) ayant pour valeur par défaut `False`. L'unique fonction associée à cette classe est nommée `check_permissions`, qui contrôle l'accessibilité de chaque document.

### Génération

Le module de Génération est la dernière étape du pipeline RAG et l'une des plus vulnérables. Pour cela, nous avons créé une classe `Génération` prenant comme paramètres : un modèle d'IA génératrice (`ai_model`), un identifiant de collection (`collection_id`), un booléen permettant de mettre en place une méthode défensive à l'aide de balises système (`balise_system`), les droits de l'utilisateur (`user_admin`, booléen), un booléen pour activer la pré-génération (`pre_generation`), et de même pour la post-génération (`post_generation`). Nous retrouvons deux fonctions : une fonction `chat()` afin d'effectuer une simple requête au modèle et d'obtenir une réponse, et une fonction `chatbox()` afin d'obtenir une conversation avec le modèle.

**Exemple d'utilisation :**

```python
from common.initialisation import Initialisation
from common.generation import Generation

rag_db = Initialisation("CGI_collection")
rag_db.creation()
generation_rag = Generation("llama3", rag_db.recuperer_id(), True, False, True, True)
generation_rag.chatbox()
```

### Post-Génération

L'étape de Post-Génération intervient en aval de la réponse de l'IA génératrice, afin de vérifier qu'elle ne divulgue pas d'information trop proche du contenu réellement stocké dans le data set. Cette classe possède une fonction `fuite_verbatim`, qui contrôle la proximité entre la réponse générée par l'IA et les chunks qui lui ont été transmis. Si la valeur est au-dessus du seuil donné, alors nous procédons à une reformulation de l'IA à l'aide d'un prompt système, puis nous recontrôlons la sortie.

### Rag_builder, Rag_config…

Au sein du dossier `common/`, nous retrouvons également des fichiers de configuration et de construction (builder). Leur présence apporte une facilité pour l'utilisation des modules cités auparavant.

Le fichier `rag_config.py` recense l'ensemble des attributs que nous pouvons retrouver dans les modules du pipeline, afin de pouvoir automatiser leur création à l'aide du décorateur `@dataclass`.

Le fichier `rag_builder.py` est responsable de la traduction d'un `RagConfig` en un dictionnaire contenant les instances nécessaires à l'utilisation de l'architecture RAG ciblée.

Prenons un exemple afin de bien comprendre :

```python
@dataclass
class RetrieverConfig:
    id_collection: str
    embedding_model: str = "nomic-embed-text"
    use_reranker: bool = False
    user_is_admin: bool = False
```

Sous nos yeux, un décorateur pour la classe `RetrieverConfig`, possédant les mêmes attributs que notre classe `Retriever`.

Il devient alors possible de préparer la configuration complète d'une architecture RAG, module par module, de manière indépendante :

```python
target = RagConfig(
    retriever_config=RetrieverConfig(
        id_collection=collection_id,
        use_reranker=True
    ),
    generation_config=GenerationConfig(
        ai_model="llama3",
        collection_id=collection_id,
        balise_system=True,
        user_admin=True,
        pre_generation=True,
        post_generation=True
    )
)
```

Cette mise en place permet à la classe `Attack`, qui attend par défaut une cible représentant notre RAG, d'accepter un objet `RagConfig` comme cible. Cet objet peut représenter une architecture constituée d'un retriever et/ou d'un indexeur, selon les modules réellement nécessaires à l'attaque simulée. La fonction `build_rag()` transforme alors ce `RagConfig` en instances réelles, stockées dans un dictionnaire accessible via `self.rag`.

Lors du développement d'une attaque, il devient alors possible d'utiliser directement les modules ciblés à l'aide de la variable associée, par exemple :

```python
self.rag["retriever"].retriever(query, top_k)
self.rag["generation"].chat(query)
```

---
