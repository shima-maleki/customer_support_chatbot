from typing import Generic, Type, TypeVar
from typing import List, Optional, Dict, Any
from bson import ObjectId
from loguru import logger
from pydantic import BaseModel
from uuid import uuid4

from langchain_qdrant import QdrantVectorStore, RetrievalMode
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from langchain.schema import Document
from assistant.application.rag.embeddings import get_openai_embedding_model

from assistant.config import settings

# qdrant_manager.py
from typing import List, Optional, Dict, Any
from uuid import uuid4

from langchain_qdrant import QdrantVectorStore, RetrievalMode
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, SparseVectorParams, SparseIndexParams


class QdrantManager:
    """
    A modular class to manage Qdrant vector store operations including
    client initialization, collection creation, document ingestion, and retrieval.
    """

    def __init__(
        self,
        collection_name: str,
        embedding,
        path: Optional[str] = None,
        distance_metric: Distance = Distance.COSINE,
        vector_size: int = 1536,
        api_key: Optional[str] = None,
        retrieval_mode: RetrievalMode = RetrievalMode.DENSE,
        vector_name: Optional[str] = '',  # Modified: default to unnamed vector
        sparse_vector_name: Optional[str] = None,
        sparse_embedding=None,
        force_recreate: bool = False,  # New: force recreation flag
    ):
        self.collection_name = collection_name
        self.embedding = embedding
        self.sparse_embedding = sparse_embedding
        self.retrieval_mode = retrieval_mode
        self.vector_name = vector_name
        self.sparse_vector_name = sparse_vector_name
        self.force_recreate = force_recreate

        # Initialize Qdrant client
        self.client = self._init_client(path)

        # Create collection if it does not exist or force_recreate is True
        self._create_collection(distance_metric, vector_size)

        # Initialize LangChain QdrantVectorStore wrapper
        self.vector_store = self._init_vector_store()

    def _init_client(
        self,
        path: Optional[str],
    ) -> QdrantClient:
        if path:
            return QdrantClient(path=path)
        else:
            return QdrantClient(url=settings.QDRANT_URI, api_key=settings.QDRANT_API_KEY)

    def _create_collection(self, distance_metric: Distance, vector_size: int):
        vectors_config = None
        sparse_vectors_config = None

        if self.retrieval_mode == RetrievalMode.DENSE:
            if self.vector_name:
                vectors_config = {self.vector_name: VectorParams(size=vector_size, distance=distance_metric)}
            else:
                vectors_config = VectorParams(size=vector_size, distance=distance_metric)

        elif self.retrieval_mode == RetrievalMode.SPARSE:
            sparse_vectors_config = {
                self.sparse_vector_name or "sparse_vector": SparseVectorParams(
                    index=SparseIndexParams(on_disk=False)
                )
            }
            vectors_config = {}

        elif self.retrieval_mode == RetrievalMode.HYBRID:
            vectors_config = (
                {self.vector_name: VectorParams(size=vector_size, distance=distance_metric)}
                if self.vector_name else
                VectorParams(size=vector_size, distance=distance_metric)
            )
            sparse_vectors_config = {
                self.sparse_vector_name or "sparse_vector": SparseVectorParams(
                    index=SparseIndexParams(on_disk=False)
                )
            }

        existing_collections = self.client.get_collections().collections
        existing_names = [col.name for col in existing_collections]

        if self.force_recreate and self.collection_name in existing_names:
            self.client.delete_collection(self.collection_name)

        if self.collection_name not in existing_names or self.force_recreate:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=vectors_config,
                sparse_vectors_config=sparse_vectors_config,
            )

    def _init_vector_store(self) -> QdrantVectorStore:
        return QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embedding,
            sparse_embedding=self.sparse_embedding,
            retrieval_mode=self.retrieval_mode,
            vector_name=self.vector_name,
        )

    def add_documents(self, documents: List[Document], ids: Optional[List[str]] = None):
        if ids is None:
            ids = [str(uuid4()) for _ in documents]
        self.vector_store.add_documents(documents=documents, ids=ids)

    def delete_documents(self, ids: List[str]) -> bool:
        return self.vector_store.delete(ids=ids)

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        search_type: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        search_kwargs: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """
        Perform a similarity search with optional metadata (payload) filtering.

        Args:
            query: Query string to search.
            k: Number of top documents to return.
            search_type: Type of search ("similarity", "mmr", etc.).
            filters: Metadata filter for narrowing results.
            search_kwargs: Additional search options.

        Returns:
            List of Document objects.
        """
        # Build search kwargs with default k
        search_kwargs = search_kwargs or {}
        search_kwargs.setdefault("k", k)

        retriever = self.vector_store.as_retriever(
            search_type=search_type or "similarity",
            search_kwargs=search_kwargs,
            filter = filters
        )
        return retriever.invoke(query)

def vectorstore():
    # Instantiate QdrantManager
    return QdrantManager(
        collection_name=settings.QDRANT_DATABASE_NAME,
        embedding=get_openai_embedding_model(),
        vector_size=1536,
        retrieval_mode=RetrievalMode.DENSE,
    )