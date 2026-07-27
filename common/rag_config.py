from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class RetrieverConfig:
    id_collection: str
    embedding_model: str = "nomic-embed-text"
    use_reranker: bool = False
    user_is_admin: bool = False


@dataclass
class GenerationConfig:
    ai_model: str
    collection_id: str
    retriever_config : RetrieverConfig
    balise_system: bool = False
    pre_generation: bool = False
    post_generation: bool = False

@dataclass
class IndexeurConfig:
    flux_rss: str
    collection_id: str

@dataclass
class InitialisationConfig:
    nom_collection  : str 
@dataclass
class RagConfig:
    initialisation_config: Optional[InitialisationConfig] = None
    indexeur_config: Optional[IndexeurConfig] = None
    retriever_config: Optional[RetrieverConfig] = None
    generation_config: Optional[GenerationConfig] = None
    

