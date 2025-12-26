from typing import Literal, Union

from langchain_openai import OpenAIEmbeddings
from assistant.config import settings

def get_openai_embedding_model(model_id: str = settings.RAG_TEXT_EMBEDDING_MODEL_ID) -> OpenAIEmbeddings:
    """Gets an OpenAI embedding model instance.

    Args:
        model_id (str): The ID/name of the OpenAI embedding model to use

    Returns:
        OpenAIEmbeddings: A configured OpenAI embeddings model instance with
            special token handling enabled
    """
    return OpenAIEmbeddings(
        model=model_id,
        allowed_special={"<|endoftext|>"},
        api_key = settings.OPENAI_API_KEY
    )