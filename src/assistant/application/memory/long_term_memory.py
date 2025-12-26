from langchain_core.documents import Document
from loguru import logger

from assistant.application.data import deduplicate_documents, get_extraction_generator
from assistant.application.rag.retrievers import Retriever, get_retriever
from assistant.config import settings
from assistant.infrastructure.qdrant import QdrantIngestionService


class LongTermMemoryCreator:
    def __init__(self) -> None:
        self.retriever = QdrantRetrieverService().get_retriever()

    def __call__(self, philosophers: list[PhilosopherExtract]) -> None:
        if len(philosophers) == 0:
            logger.warning("No philosophers to extract. Exiting.")

            return

        # First clear the long term memory collection to avoid duplicates.
        with MongoClientWrapper(
            model=Document, collection_name=settings.QDRANT_LONG_TERM_MEMORY_COLLECTION
        ) as client:
            client.clear_collection()

        extraction_generator = get_extraction_generator(philosophers)
        for _, docs in extraction_generator:
            chunked_docs = self.splitter.split_documents(docs)

            chunked_docs = deduplicate_documents(chunked_docs, threshold=0.7)

            self.retriever.vectorstore.add_documents(chunked_docs)

        self.__create_index()

    def __create_index(self) -> None:
        with MongoClientWrapper(
            model=Document, collection_name=settings.QDRANT_LONG_TERM_MEMORY_COLLECTION
        ) as client:
            self.index = MongoIndex(
                retriever=self.retriever,
                mongodb_client=client,
            )
            self.index.create(
                is_hybrid=True, embedding_dim=settings.RAG_TEXT_EMBEDDING_MODEL_DIM
            )


class LongTermMemoryRetriever:
    def __init__(self) -> None:
        self.retriever = QdrantRetrieverService().get_retriever()

    def __call__(self, query: str) -> list[Document]:
        return self.retriever.invoke(query)