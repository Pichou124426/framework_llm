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
    balise_system: bool = False
    user_admin: bool = False
    pre_generation: bool = False
    post_generation: bool = False

@dataclass
class IndexeurConfig:
    flux_rss: str
    collection_id: str

@dataclass
class InitialisationConig:
    nom_collection  : str 
@dataclass
class RagConfig:
    retriever_config: Optional[RetrieverConfig] = None
    generation_config: Optional[GenerationConfig] = None
    indexeur_config: Optional[IndexeurConfig] = None
    initialisation_config: Optional[InitialisationConig] = None

