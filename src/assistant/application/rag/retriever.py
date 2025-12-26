from loguru import logger

from assistant.infrastructure.qdrant.service import QdrantIngestionService
from assistant.application.rag.embeddings import get_openai_embedding_model
from assistant.config import settings

class QdrantRetrieverService:
    """Initializes from an existing Qdrant collection and provides a retriever."""

    def __init__(
        self,
        vector_store: QdrantIngestionService,
    ):
        self.vector_store = QdrantIngestionService()
        self.collection_name = settings.QDRANT_DATABASE_NAME
        self.embeddings = get_openai_embedding_model()

    def get_retriever(self, search_type="similarity", k=settings.RAG_TOP_K, filters: dict = None):
        """Returns a LangChain retriever from an existing Qdrant collection."""

        retriever = self.vector_store.as_retriever(
            search_type=search_type,
            search_kwargs={"k": k, "filter": filters or {}},
        )

        logger.info(f"Retriever initialized from collection: {self.collection_name}")
        return retriever

def get_retriever():
    return QdrantRetrieverService(QdrantIngestionService).get_retriever()