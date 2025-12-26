from typing import Literal, Union

from langchain_openai import OpenAIEmbeddings

EmbeddingsModel = OpenAIEmbeddings

def get_openai_embedding_model(model_id: str) -> OpenAIEmbeddings:
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
    )