import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.initialisation import Initialisation
from common.rag_config import RagConfig, RetrieverConfig, GenerationConfig, IndexeurConfig, InitialisationConfig
from attack.Membership_Inference import MembershipInference



# Variable Globale 
collection_name = "CGI_collection"
user_permission = True

# Variable indexation  
flux_data_rss = "https://rmcsport.bfmtv.com/rss/football/coupe-du-monde/"

# Variable Retriever 
modele_vectorisation = "nomic-embed-text"
reranking = False

#Variable Generation 
modele_generation = "llama3"
guardrails = False
use_pregeneration = False
use_postgeneration = False

# Personnalisation du RAG 
use_initialisation : bool = True
use_indexation : bool = False
use_retriever : bool = True
use_generation : bool = True


"------------------------- Automatique attribution ---------------------"

# Initialisation de la collection 
init_db = Initialisation (collection_name)
init_db.creation()
init_db.afficher_informations()
identifiant_collection = init_db.recuperer_id()


# Configuration des modules   
initialisation_config = InitialisationConfig(nom_collection= collection_name)
indexation_config = IndexeurConfig(flux_rss= flux_data_rss, collection_id= identifiant_collection )
retriever_config = RetrieverConfig (id_collection= identifiant_collection, embedding_model= modele_vectorisation, use_reranker = reranking,user_is_admin= user_permission)
generation_config = GenerationConfig (ai_model= modele_generation, collection_id= identifiant_collection,retriever_config= retriever_config,balise_system= guardrails, pre_generation= use_pregeneration, post_generation=use_postgeneration)



# Création de la cible en fonction des modules souhaités et construit sur les configurations données en amont  
target = RagConfig (
    initialisation_config=initialisation_config if use_initialisation else None,
    indexeur_config=indexation_config if use_indexation else None,
    retriever_config=retriever_config if use_retriever else None,
    generation_config=generation_config if use_generation else None
    )

"""------------------------------------------------------------------------------"""


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

