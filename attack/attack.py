# attack/attack.py
from common.retriever import Retriever
from common.generation import Generation
from common.indexation import Indexeur
from common.initialisation import Initialisation
from common.rag_config import RagConfig
from common.rag_builder import build_rag
from dataclasses import asdict
from typing import cast

class Attack:
    def __init__(self, name, description, target: RagConfig):
        self.name = name
        self.description = description
        self.rag = build_rag(target)

    @property
    def retriever(self) -> Retriever:
        return cast(Retriever, self.rag["retriever"])

    @property
    def generation(self) -> Generation:
        return cast(Generation, self.rag["generation"])

    @property
    def indexeur(self) -> Indexeur:
        return cast(Indexeur, self.rag["indexeur"])
    @property
    def initialisation(self) -> Initialisation:
        return cast(Initialisation, self.rag["initialisation"])