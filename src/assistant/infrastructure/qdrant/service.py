from typing import Generic, Type, TypeVar
from typing import List, Optional, Dict, Any
from bson import ObjectId
from loguru import logger
from pydantic import BaseModel
from uuid import uuid4

from langchain_qdrant import QdrantVectorStore, RetrievalMode
from langchain.embeddings import OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from langchain.schema import Document

from assistant.config import settings

T = TypeVar("T", bound=BaseModel)

class QdrantIngestionService(Generic[T]):
    """Initializes Qdrant collection and ingests BaseModel documents."""

    def __init__(
        self,
        model: Type[T],
        collection_name: str,
        qdrant_url: str = settings.QDRANT_URI,
        qdrant_api_key: str = settings.QDRANT_API_KEY,
        embeddings_model=None,
    ):
        self.model = model
        self.collection_name = collection_name
        self.client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
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

        existing_ids = set()
        for doc in documents:
            doc_id = getattr(doc, "id", None)
            if not doc_id:
                raise ValueError("Each document must have an 'id' field.")
            exists = self._doc_exists(doc_id)
            if exists:
                existing_ids.add(doc_id)

        new_documents = [doc for doc in documents if getattr(doc, "id") not in existing_ids]

        if not new_documents:
            logger.info("All documents already exist in the collection. Nothing to ingest.")
            return

        lc_documents = []
        for doc in new_documents:
            doc_dict = doc.model_dump()
            content = doc_dict.get(text_field)
            if not content:
                raise ValueError(f"Missing text field '{text_field}' in document")

            metadata = {k: v for k, v in doc_dict.items() if k != text_field}
            lc_documents.append(Document(page_content=content, metadata=metadata))

        QdrantVectorStore.from_documents(
            documents=lc_documents,
            embedding=self.embeddings,
            client=self.client,
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
