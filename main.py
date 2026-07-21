from common.initialisation import Initialisation
from common.rag_config import RagConfig, RetrieverConfig, GenerationConfig
from attack.Membership_Inference import MembershipInference


rag_db = Initialisation("CGI_collection")
rag_db.creation()
rag_db.afficher_informations()
collection_id = rag_db.recover_id()

target = RagConfig(
    retriever_config=RetrieverConfig(
        id_collection=collection_id,
        use_reranker=True
    ),
    generation_config=GenerationConfig(
        ai_model="llama3",
        collection_id=collection_id,
        balise_system=True,
        user_admin=False,
        pre_generation=True,
        post_generation=True
    )
)

print("\n========== TEST WHITE-BOX ==========\n")
mia_white = MembershipInference(
    name="Membership Attack - WhiteBox",
    description="Vérifie la présence d'un chunk via les distances de similarité",
    modules_config=target,
    white_box=True
)
mia_white.launcher()

print("\n========== TEST BLACK-BOX ==========\n")
mia_black = MembershipInference(
    name="Membership Attack - BlackBox",
    description="Vérifie la fuite du chunk via complétion de texte",
    modules_config=target,
    white_box=False
)
mia_black.launcher()