from typing import Generic, Type, TypeVar
from typing import List, Optional, Dict, Any
from loguru import logger
from pydantic import BaseModel
from uuid import uuid4

from langchain_qdrant import QdrantVectorStore, RetrievalMode
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from langchain_core.documents import Document

from assistant.config import settings
from assistant.domain.document import Document as KBDocument

T = TypeVar("T", bound=BaseModel)

class QdrantIngestionService(Generic[T]):
    """Initializes Qdrant collection and ingests BaseModel documents."""

    def __init__(
        self,
        model: Type[T],
        collection_name: str,
        qdrant_url: Optional[str] = settings.QDRANT_URL or settings.QDRANT_URI,
        qdrant_api_key: str = settings.QDRANT_API_KEY,
        embeddings_model=None,
    ):
        self.model = model
        self.collection_name = collection_name
        resolved_url = qdrant_url or settings.QDRANT_URL or settings.QDRANT_URI
        if not resolved_url:
            raise ValueError("Qdrant URL is not configured. Set QDRANT_URL or QDRANT_URI.")

        self.qdrant_url = resolved_url
        self.qdrant_api_key = qdrant_api_key
        self.client = QdrantClient(url=self.qdrant_url, api_key=self.qdrant_api_key)
        self.embeddings = embeddings_model or OpenAIEmbeddings()

    def check_collection_exists(self) -> bool:
        """Check if the Qdrant collection exists."""
        collections = self.client.get_collections().collections
        exists = any(col.name == self.collection_name for col in collections)
        logger.info(f"Collection '{self.collection_name}' exists: {exists}")
        return exists

    def delete_collection(self) -> None:
        """Delete the collection from Qdrant."""
        if self.check_collection_exists():
            self.client.delete_collection(collection_name=self.collection_name)
            logger.warning(f"Deleted collection: {self.collection_name}")
        else:
            logger.info(f"Collection '{self.collection_name}' does not exist. Nothing to delete.")

    def ingest_documents(self, documents: List[T], text_field: str = "content") -> None:
        """Ingest only new documents (by ID) into Qdrant."""
        if not documents:
            raise ValueError("No documents to ingest")

        lc_documents = []
        for doc in documents:
            doc_dict = doc.model_dump()
            content = doc_dict.get(text_field)
            if not content:
                raise ValueError(f"Missing text field '{text_field}' in document")

            metadata = {k: v for k, v in doc_dict.items() if k != text_field}
            lc_documents.append(Document(page_content=content, metadata=metadata))

        QdrantVectorStore.from_documents(
            documents=lc_documents,
            embedding=self.embeddings,
            url=self.qdrant_url,
            api_key=self.qdrant_api_key,
            collection_name=self.collection_name,
        )

        logger.info(f"Ingested {len(lc_documents)} new documents into collection: {self.collection_name}")

    def _doc_exists(self, doc_id: str) -> bool:
        """Check if a document with the given ID already exists in Qdrant."""
        try:
            search_filter = Filter(
                must=[
                    FieldCondition(key="id", match=MatchValue(value=doc_id))
                ]
            )
            result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=search_filter,
                limit=1,
            )
            return bool(result[0])
        except Exception as e:
            logger.error(f"Failed to check existence of doc ID '{doc_id}': {e}")
            return False

    # Convenience alias expected by scripts.
    def add_documents(self, documents: List[T], text_field: str = "content") -> None:
        self.ingest_documents(documents=documents, text_field=text_field)


def vectorstore(collection_name: Optional[str] = None) -> QdrantIngestionService:
    """Factory to create a QdrantIngestionService with defaults from settings."""
    target_collection = collection_name or settings.QDRANT_DATABASE_NAME
    return QdrantIngestionService(
        model=KBDocument,
        collection_name=target_collection,
        qdrant_url=settings.QDRANT_URL or settings.QDRANT_URI,
        qdrant_api_key=settings.QDRANT_API_KEY,
        embeddings_model=OpenAIEmbeddings(
            model=settings.EMBEDDINGS_MODEL_ID,
            api_key=settings.OPENAI_API_KEY,
        ),
    )
