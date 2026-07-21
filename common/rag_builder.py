# rag_builder.py
from dataclasses import asdict
from common.retriever import Retriever
from common.generation import Generation
from common.indexation import Indexeur
from common.initialisation import Initialisation
from common.rag_config import RagConfig

def build_rag(target: RagConfig) -> dict:
    rag = {}
    if target.retriever_config:
        rag["retriever"] = Retriever(**asdict(target.retriever_config))
    if target.generation_config:
        rag["generation"] = Generation(**asdict(target.generation_config))
    if target.indexeur_config:
        rag["indexeur"] = Indexeur(**asdict(target.indexeur_config))
    if target.initialisation_config:
        rag["initialisation"] = Initialisation(**asdict(target.initialisation_config))
    return rag