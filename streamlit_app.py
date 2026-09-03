"""Interface Streamlit du framework offensif RAG.

Deux pages :
- Chat libre : discussion directe avec le modèle (Ollama), hors pipeline RAG.
- Cible RAG & Attaques : construction module par module d'une cible RAG
  (Initialisation / Indexation / Retriever / Génération) puis lancement d'une
  attaque avec un résultat structuré et un bloc pédagogique associé.

Lancement : `streamlit run streamlit_app.py`
"""

import sys
import os
import traceback
from datetime import datetime

import streamlit as st

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from common.initialisation import Initialisation
from common.indexation import Indexeur
from common.rag_config import RagConfig, RetrieverConfig, GenerationConfig, IndexeurConfig, InitialisationConfig
from attack.Membership_Inference import MembershipInference
from attack.Prompt_Injection import Prompt_Injection
from ui.catalog import ATTACK_CATALOG, FAMILIES
from ui.backend import check_ollama as _check_ollama, check_chroma as _check_chroma, list_ollama_models as _list_ollama_models, ollama_chat_direct

st.set_page_config(page_title="RAG Security Lab", page_icon="🛡️", layout="wide")


@st.cache_data(ttl=15, show_spinner=False)
def check_ollama():
    return _check_ollama()


@st.cache_data(ttl=15, show_spinner=False)
def check_chroma():
    return _check_chroma()


@st.cache_data(ttl=30, show_spinner=False)
def list_ollama_models():
    return _list_ollama_models()

RSS_SUGGESTIONS = [
    "https://rmcsport.bfmtv.com/rss/football/coupe-du-monde/",
    "https://rmcsport.bfmtv.com/rss/football/euro/",
    "https://rmcsport.bfmtv.com/rss/football/",
]

PI_MODE_TO_KEY = {
    "dan": "pi_dan",
    "system": "pi_system",
    "indirecte": "pi_indirecte",
    "role": "pi_role",
    "contexte": "pi_contexte",
}

# --------------------------------------------------------------------------------------
# État de session
# --------------------------------------------------------------------------------------

DEFAULTS = {
    "collection_name": "CGI_collection",
    "collection_id": None,
    "flux_rss": RSS_SUGGESTIONS[0],
    "embedding_model": "nomic-embed-text",
    "generation_model": "llama3",
    "use_indexation": False,
    "use_reranker": False,
    "user_is_admin": True,
    "use_guardrails": True,
    "use_pregeneration": False,
    "use_postgeneration": False,
    "rag_config": None,
    "rag_config_snapshot": None,
    "index_report": None,
    "free_chat_history": [],
    "free_chat_model": "llama3",
    "attack_family": list(FAMILIES.keys())[0],
    "attack_history": [],
    "mia_pirate_input": "Le score du match test contre le Kazakhstan",
}
for key, value in DEFAULTS.items():
    st.session_state.setdefault(key, value)


def current_config_snapshot():
    return (
        st.session_state.collection_id,
        st.session_state.embedding_model,
        st.session_state.use_reranker,
        st.session_state.user_is_admin,
        st.session_state.generation_model,
        st.session_state.use_guardrails,
        st.session_state.use_pregeneration,
        st.session_state.use_postgeneration,
    )


# --------------------------------------------------------------------------------------
# Rendu d'un résultat d'attaque structuré (commun aux deux familles d'attaque)
# --------------------------------------------------------------------------------------

def render_attack_result(result: dict):
    verdict = result.get("verdict") or {}
    success = verdict.get("success")
    label = verdict.get("label", "Résultat")
    detail = verdict.get("detail", "")

    if success is True:
        st.error(f"🔓 **{label}**\n\n{detail}")
    elif success is False:
        st.success(f"🛡️ **{label}**\n\n{detail}")
    else:
        st.info(f"ℹ️ **{label}**\n\n{detail}")

    if verdict.get("note_technique"):
        st.caption(verdict["note_technique"])

    metrics = result.get("metrics") or {}
    numeric_metrics = {k: v for k, v in metrics.items() if isinstance(v, (int, float))}
    text_metrics = {k: v for k, v in metrics.items() if isinstance(v, str)}

    if numeric_metrics:
        cols = st.columns(len(numeric_metrics))
        for col, (k, v) in zip(cols, numeric_metrics.items()):
            col.metric(k.replace("_", " ").capitalize(), f"{v:.4f}")

    for k, v in text_metrics.items():
        st.caption(f"**{k.replace('_', ' ').capitalize()}**")
        st.code(v)

    st.markdown("**Déroulé de l'attaque**")
    for i, step in enumerate(result.get("steps", []), start=1):
        with st.expander(f"Étape {i} — {step.get('title', '')}", expanded=(i == len(result.get("steps", [])))):
            st.markdown(f"**Prompt envoyé :**")
            st.code(step.get("prompt", ""), language=None)
            if step.get("response") is not None:
                st.markdown("**Réponse du modèle :**")
                st.write(step["response"])
            if step.get("note"):
                st.caption(step["note"])


def render_explanatory_block(attack_key: str):
    info = ATTACK_CATALOG[attack_key]
    st.markdown(f"#### 📚 {info['label']}")
    st.caption("Modules impliqués : " + ", ".join(info["modules"]))
    tab_desc, tab_contre, tab_exemple = st.tabs(["Description", "Contre-mesure", "Exemple"])
    with tab_desc:
        st.write(info["description"])
    with tab_contre:
        st.write(info["contre_mesure"])
    with tab_exemple:
        st.write(info["exemple"])


# --------------------------------------------------------------------------------------
# Page : Chat libre
# --------------------------------------------------------------------------------------

def render_chat_page():
    st.header("💬 Chat libre avec le modèle")
    st.caption(
        "Discussion directe avec le LLM via Ollama, indépendamment de tout pipeline RAG. "
        "Idéal pour prendre en main l'assistant avant d'aborder la page de construction de cible et d'attaques."
    )

    models = list_ollama_models()
    col_model, col_reset = st.columns([3, 1])
    with col_model:
        current = st.session_state.free_chat_model
        index = models.index(current) if current in models else 0
        st.session_state.free_chat_model = st.selectbox("Modèle", models, index=index)
    with col_reset:
        st.write("")
        if st.button("🗑️ Réinitialiser la conversation", use_container_width=True):
            st.session_state.free_chat_history = []
            st.rerun()

    for msg in st.session_state.free_chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Écrivez votre message…")
    if prompt:
        st.session_state.free_chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Le modèle réfléchit…"):
                try:
                    response = ollama_chat_direct(st.session_state.free_chat_model, st.session_state.free_chat_history)
                except Exception as exc:
                    response = f"⚠️ Erreur lors de l'appel au modèle : {exc}"
            st.markdown(response)
        st.session_state.free_chat_history.append({"role": "assistant", "content": response})


# --------------------------------------------------------------------------------------
# Page : Cible RAG & Attaques
# --------------------------------------------------------------------------------------

def render_rag_page():
    st.header("🎯 Construire une cible RAG & lancer une attaque")
    st.caption(
        "Assemblez la cible module par module (comme on assemblerait une architecture RAG réelle), "
        "puis choisissez une attaque à exécuter dessus."
    )

    st.subheader("1️⃣ Initialisation de la collection")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.session_state.collection_name = st.text_input("Nom de la collection ChromaDB", value=st.session_state.collection_name)
    with col2:
        st.write("")
        if st.button("Créer / récupérer la collection", use_container_width=True):
            try:
                with st.spinner("Connexion à ChromaDB…"):
                    init_db = Initialisation(st.session_state.collection_name)
                    init_db.creation()
                    collection_id = init_db.recuperer_id()
                if collection_id:
                    st.session_state.collection_id = collection_id
                    st.success(f"Collection prête. Identifiant : `{collection_id}`")
                else:
                    st.error("Impossible de récupérer l'identifiant de la collection.")
            except Exception as exc:
                st.error(f"Échec de connexion à ChromaDB : {exc}")
                with st.expander("Détails techniques"):
                    st.code(traceback.format_exc())

    if st.session_state.collection_id:
        st.caption(f"✅ Collection active : `{st.session_state.collection_name}` (id : `{st.session_state.collection_id}`)")
    else:
        st.warning("Aucune collection active. Créez-en une avant de poursuivre.")

    st.divider()

    st.subheader("2️⃣ Indexation (optionnel)")
    st.session_state.use_indexation = st.checkbox(
        "Activer le module d'indexation (alimenter la collection depuis un flux RSS)",
        value=st.session_state.use_indexation,
        help="À n'utiliser que si la collection est vide ou doit être réalimentée. Sans cela, la démo réutilise les données déjà indexées.",
    )
    if st.session_state.use_indexation:
        flux_choice = st.selectbox(
            "Flux RSS", RSS_SUGGESTIONS + ["Autre (saisir une URL personnalisée)"],
            index=RSS_SUGGESTIONS.index(st.session_state.flux_rss) if st.session_state.flux_rss in RSS_SUGGESTIONS else 0,
        )
        if flux_choice == "Autre (saisir une URL personnalisée)":
            st.session_state.flux_rss = st.text_input("URL du flux RSS", value=st.session_state.flux_rss)
        else:
            st.session_state.flux_rss = flux_choice

        if st.button("📥 Indexer les données", disabled=not st.session_state.collection_id):
            try:
                with st.spinner("Récupération, vectorisation et stockage des articles…"):
                    indexeur = Indexeur(st.session_state.flux_rss, st.session_state.collection_id)
                    rapport = indexeur.insert_data()
                st.session_state.index_report = rapport
            except Exception as exc:
                st.error(f"Échec de l'indexation : {exc}")
                with st.expander("Détails techniques"):
                    st.code(traceback.format_exc())

    if st.session_state.index_report:
        rapport = st.session_state.index_report
        c1, c2, c3 = st.columns(3)
        c1.metric("Articles trouvés", rapport["total"])
        c2.metric("Indexés avec succès", rapport["success"])
        c3.metric("Erreurs", len(rapport["errors"]))
        if rapport["errors"]:
            with st.expander("Détail des erreurs d'indexation"):
                st.table(rapport["errors"])

    st.divider()

    st.subheader("3️⃣ Retriever")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.embedding_model = st.text_input("Modèle d'embedding", value=st.session_state.embedding_model)
    with col2:
        st.session_state.use_reranker = st.checkbox(
            "Activer le reranking (cross-encoder)", value=st.session_state.use_reranker,
            help="Étape M7 : ré-ordonne les documents remontés selon leur pertinence sémantique réelle. Charge un modèle à chaque appel : peut ralentir la démo.",
        )
    with col3:
        st.session_state.user_is_admin = st.checkbox(
            "Utilisateur avec droits admin", value=st.session_state.user_is_admin,
            help="Un utilisateur admin voit tous les documents, y compris ceux marqués 'critical'. Décochez pour simuler un utilisateur standard restreint aux documents 'easy'.",
        )

    st.subheader("4️⃣ Génération")
    gen_models = list_ollama_models()
    col1, col2 = st.columns([2, 3])
    with col1:
        current = st.session_state.generation_model
        index = gen_models.index(current) if current in gen_models else 0
        st.session_state.generation_model = st.selectbox("Modèle de génération", gen_models, index=index)
    with col2:
        st.session_state.use_guardrails = st.checkbox(
            "Activer les guardrails (balises système + instructions défensives)", value=st.session_state.use_guardrails,
            help="Encadre les données récupérées avec des balises <contenu_externe_non_fiable> et ajoute une instruction système défensive.",
        )
    col3, col4 = st.columns(2)
    with col3:
        st.session_state.use_pregeneration = st.checkbox(
            "Activer la pré-génération (contrôle des permissions)", value=st.session_state.use_pregeneration,
            help="Revérifie, juste avant la génération, que les droits de l'utilisateur autorisent bien les documents remontés.",
        )
    with col4:
        st.session_state.use_postgeneration = st.checkbox(
            "Activer la post-génération (détection de fuite verbatim)", value=st.session_state.use_postgeneration,
            help="Compare la réponse générée aux chunks sources et déclenche une reformulation en cas de similarité trop élevée.",
        )

    st.divider()

    build_disabled = not st.session_state.collection_id
    if st.button("🏗️ Construire la cible RAG", type="primary", disabled=build_disabled):
        retriever_config = RetrieverConfig(
            id_collection=st.session_state.collection_id,
            embedding_model=st.session_state.embedding_model,
            use_reranker=st.session_state.use_reranker,
            user_is_admin=st.session_state.user_is_admin,
        )
        generation_config = GenerationConfig(
            ai_model=st.session_state.generation_model,
            collection_id=st.session_state.collection_id,
            retriever_config=retriever_config,
            balise_system=st.session_state.use_guardrails,
            pre_generation=st.session_state.use_pregeneration,
            post_generation=st.session_state.use_postgeneration,
        )
        indexeur_config = None
        if st.session_state.use_indexation:
            indexeur_config = IndexeurConfig(flux_rss=st.session_state.flux_rss, collection_id=st.session_state.collection_id)

        st.session_state.rag_config = RagConfig(
            initialisation_config=InitialisationConfig(nom_collection=st.session_state.collection_name),
            indexeur_config=indexeur_config,
            retriever_config=retriever_config,
            generation_config=generation_config,
        )
        st.session_state.rag_config_snapshot = current_config_snapshot()
        st.success("Cible RAG construite avec succès.")

    if st.session_state.rag_config:
        stale = st.session_state.rag_config_snapshot != current_config_snapshot()
        if stale:
            st.warning("⚠️ La configuration a changé depuis la dernière construction. Reconstruisez la cible pour appliquer vos changements.")
        with st.expander("📋 Résumé de la cible construite", expanded=False):
            cfg = st.session_state.rag_config
            st.json({
                "collection": {"nom": cfg.initialisation_config.nom_collection, "id": st.session_state.collection_id},
                "indexation": {"flux_rss": cfg.indexeur_config.flux_rss} if cfg.indexeur_config else "désactivée",
                "retriever": {
                    "embedding_model": cfg.retriever_config.embedding_model,
                    "reranking": cfg.retriever_config.use_reranker,
                    "utilisateur_admin": cfg.retriever_config.user_is_admin,
                },
                "generation": {
                    "modele": cfg.generation_config.ai_model,
                    "guardrails": cfg.generation_config.balise_system,
                    "pre_generation": cfg.generation_config.pre_generation,
                    "post_generation": cfg.generation_config.post_generation,
                },
            })

    st.divider()

    st.subheader("5️⃣ Choisir et lancer une attaque")
    if not st.session_state.rag_config:
        st.info("Construisez d'abord une cible RAG ci-dessus pour pouvoir lancer une attaque.")
        return

    col_family, col_variant = st.columns(2)
    with col_family:
        family_keys = list(FAMILIES.keys())
        family_index = family_keys.index(st.session_state.attack_family) if st.session_state.attack_family in family_keys else 0
        st.session_state.attack_family = st.selectbox("Famille d'attaque", family_keys, index=family_index)
    with col_variant:
        variant_keys = FAMILIES[st.session_state.attack_family]
        if st.session_state.get("attack_variant") not in variant_keys:
            st.session_state.attack_variant = variant_keys[0]
        variant_index = variant_keys.index(st.session_state.attack_variant)
        variant_key = st.selectbox(
            "Variante", variant_keys, index=variant_index, format_func=lambda k: ATTACK_CATALOG[k]["label"],
        )
        st.session_state.attack_variant = variant_key

    render_explanatory_block(variant_key)

    extra_input = None
    if variant_key == "mia_whitebox":
        st.session_state.mia_pirate_input = st.text_input(
            "Information dont vous voulez vérifier la présence dans la base",
            value=st.session_state.mia_pirate_input,
        )
        extra_input = st.session_state.mia_pirate_input

    if st.button("🚀 Lancer l'attaque", type="primary"):
        try:
            with st.spinner("Attaque en cours…"):
                if variant_key.startswith("mia_"):
                    attack = MembershipInference(
                        name=ATTACK_CATALOG[variant_key]["label"],
                        description=ATTACK_CATALOG[variant_key]["description"],
                        modules_config=st.session_state.rag_config,
                        white_box=(variant_key == "mia_whitebox"),
                    )
                    result = attack.launcher(pirate_input=extra_input) if variant_key == "mia_whitebox" else attack.launcher()
                else:
                    mode = next(m for m, k in PI_MODE_TO_KEY.items() if k == variant_key)
                    attack = Prompt_Injection(
                        name=ATTACK_CATALOG[variant_key]["label"],
                        description=ATTACK_CATALOG[variant_key]["description"],
                        modules_config=st.session_state.rag_config,
                        mode_attaque=mode,
                    )
                    result = attack.launcher()

            result["_timestamp"] = datetime.now().strftime("%H:%M:%S")
            result["_variant_key"] = variant_key
            st.session_state.attack_history.insert(0, result)
        except Exception as exc:
            st.error(f"L'attaque a échoué : {exc}")
            with st.expander("Détails techniques"):
                st.code(traceback.format_exc())

    if st.session_state.attack_history:
        st.divider()
        st.subheader("📜 Résultats")
        latest = st.session_state.attack_history[0]
        render_attack_result(latest)

        if len(st.session_state.attack_history) > 1:
            with st.expander(f"Historique ({len(st.session_state.attack_history) - 1} résultat(s) précédent(s))"):
                if st.button("🗑️ Vider l'historique"):
                    st.session_state.attack_history = []
                    st.rerun()
                for past in st.session_state.attack_history[1:]:
                    st.markdown(f"**{past['attack']}** — {past.get('_timestamp', '')}")
                    render_attack_result(past)
                    st.divider()


# --------------------------------------------------------------------------------------
# Page : À propos
# --------------------------------------------------------------------------------------

def render_about_page():
    st.header("ℹ️ À propos de ce laboratoire")
    st.markdown(
        """
Cette interface met en accès à des personnes non expertes du RAG le framework offensif
développé pour comprendre et démontrer des attaques sur une architecture RAG (Retrieval-Augmented
Generation) : ChromaDB pour la base vectorielle, Ollama pour les modèles de langage.

**Pages disponibles :**
- **Chat libre** : discussion directe avec le modèle, sans RAG, pour prendre en main l'assistant.
- **Cible RAG & Attaques** : construction d'une architecture RAG module par module (Initialisation,
  Indexation, Retriever avec reranking optionnel, Génération avec guardrails / pré- / post-génération),
  puis sélection et lancement d'une attaque (Membership Inference, Prompt Injection) avec un résultat
  structuré et une explication pédagogique (description, contre-mesure, exemple).

**Pré-requis techniques** : Ollama (`localhost:11434`) et ChromaDB (`localhost:8000`) doivent être
démarrés — voir `docker-compose.yml` à la racine du projet (`docker compose up -d`).
        """
    )


# --------------------------------------------------------------------------------------
# Navigation
# --------------------------------------------------------------------------------------

with st.sidebar:
    st.title("🛡️ RAG Security Lab")
    page = st.radio("Navigation", ["💬 Chat libre", "🎯 Cible RAG & Attaques", "ℹ️ À propos"])
    st.divider()
    st.caption("État des services")
    ollama_ok = check_ollama()
    chroma_ok = check_chroma()
    st.markdown(f"{'🟢' if ollama_ok else '🔴'} Ollama (`localhost:11434`)")
    st.markdown(f"{'🟢' if chroma_ok else '🔴'} ChromaDB (`localhost:8000`)")
    if not (ollama_ok and chroma_ok):
        st.caption("Démarrez les services avec `docker compose up -d` si besoin.")

if page == "💬 Chat libre":
    render_chat_page()
elif page == "🎯 Cible RAG & Attaques":
    render_rag_page()
else:
    render_about_page()
