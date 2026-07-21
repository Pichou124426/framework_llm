# attack/attack.py
from common.retriever import Retriever
from common.generation import Generation
from common.indexation import Indexeur
from common.initialisation import Initialisation
from common.rag_config import RagConfig
from dataclasses import asdict

class Attack:
    def __init__(self, name, description, target: RagConfig):
        self.name = name
        self.description = description
        self.rag = {}

        if target.retriever_config:
            self.rag["retriever"] = Retriever(**asdict(target.retriever_config))
        if target.generation_config:
            self.rag["generation"] = Generation(**asdict(target.generation_config))
        if target.indexeur_config:
            self.rag["indexeur"] = Indexeur(**asdict(target.indexeur_config))
        if target.initialisation_config:
            self.rag["initialisation"] = Initialisation(**asdict(target.initialisation_config))