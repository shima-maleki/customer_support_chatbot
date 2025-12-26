from loguru import logger
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    A Pydantic-based settings class for managing application configurations.
    """
    # --- Pydantic Settings ---
    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
        case_sensitive=False,
    )

    # --- Comet ML & Opik Configuration ---
    COMET_API_KEY: str | None = Field(
        default=None, description="API key for Comet ML and Opik services."
    )
    COMET_PROJECT: str = Field(
        default="customer_support_agent",
        description="Project name for Comet ML and Opik tracking.",
    )
    COMET_WORKSPACE: str | None = Field(
        default=None, description="Optional Comet workspace name."
    )

    # --- Hugging Face Configuration ---
    HUGGINGFACE_ACCESS_TOKEN: str | None = Field(
        default=None, description="Access token for Hugging Face API authentication."
    )
    HUGGINGFACE_DEDICATED_ENDPOINT: str | None = Field(
        default=None,
        description="Dedicated endpoint URL for real-time inference."
    )

    # --- MongoDB Atlas Configuration ---
    QDRANT_DATABASE_NAME: str = Field(
        default="customer_support_klnowledge_base",
        description="Name of the QdrantDB database.",
    )
    COLLECTION_NAME: str = Field(
        default="customer_support_klnowledge_base",
        description="Name of the Qdrant collection for embeddings.",
    )
    QDRANT_URI: str | None = Field(
        default=None,
        description="Connection URI for the local MongoDB Atlas instance.",
    )
    QDRANT_URL: str | None = Field(
        default=None,
        description="Connection URL for hosted Qdrant.",
    )
    QDRANT_API_KEY: str | None = Field(
        default=None,
        description="API key for QdrantDB service authentication.",
    )
    KNOWLEDGE_DATASET_PATH: str = Field(
        default="knowledge_base",
        description="Directory containing JSON knowledge base files.",
    )

    # --- OpenAI API Configuration ---
    OPENAI_API_KEY: str = Field(
        description="API key for OpenAI service authentication.",
    )
    EMBEDDINGS_MODEL_ID: str = Field(
        default="text-embedding-3-small",
        description="Embedding model identifier for OpenAI embeddings.",
    )

    # --- Opik / Observability ---
    OPIK_API_KEY: str | None = Field(default=None, description="API key for Opik.")
    OPIK_PROJECT_NAME: str | None = Field(default=None, description="Project name for Opik.")
    OPIK_URL: str | None = Field(default=None, description="Base URL for Opik.")
    OPIK_ENABLED: bool = Field(default=False, description="Enable Opik instrumentation.")

    @field_validator("OPENAI_API_KEY")
    @classmethod
    def check_not_empty(cls, value: str, info) -> str:
        if not value or value.strip() == "":
            logger.error(f"{info.field_name} cannot be empty.")
            raise ValueError(f"{info.field_name} cannot be empty.")
        return value


try:
    settings = Settings()
except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    raise SystemExit(e)
