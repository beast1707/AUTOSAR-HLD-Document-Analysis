from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from backend.utils.config import settings
from backend.utils.logging import setup_logger

logger = setup_logger("embedding_service")

# Singleton embedding model
_embeddings = None

def get_embeddings() -> HuggingFaceBgeEmbeddings:
    global _embeddings
    if _embeddings is None:
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        model_kwargs = {'device': 'cpu'}
        encode_kwargs = {'normalize_embeddings': True}
        
        _embeddings = HuggingFaceBgeEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
    return _embeddings
