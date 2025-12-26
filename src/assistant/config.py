from pathlib import Path

from loguru import logger
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    A Pydantic-based settings class for managing application configurations.
    """
    # --- Pydantic Settings ---
    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )

    # --- Comet ML & Opik Configuration ---
    COMET_API_KEY: str | None = Field(
        default=None, description="API key for Comet ML and Opik services."
    )
    COMET_PROJECT: str = Field(
        default="customer_support_agent",
        description="Project name for Comet ML and Opik tracking.",
    )

    # --- MongoDB Configuration ---
    MONGO_URI: str = Field(
        default="mongodb+srv://saurabhbhardwaj:saurabh27@saurabh-cluster.cuixean.mongodb.net/",
        description="Connection URI for the local MongoDB Atlas instance.",
    )
    MONGO_DB_NAME: str = "saurabh-cluster"
    MONGO_STATE_CHECKPOINT_COLLECTION: str = "assistant_state_checkpoints"
    MONGO_STATE_WRITES_COLLECTION: str = "assistant_state_writes"
    MONGO_LONG_TERM_MEMORY_COLLECTION: str = "assistant_long_term_memory"

    # --- Agents Configuration ---
    TOTAL_MESSAGES_SUMMARY_TRIGGER: int = 30
    TOTAL_MESSAGES_AFTER_SUMMARY: int = 5

    # --- RAG Configuration ---
    RAG_TEXT_EMBEDDING_MODEL_ID: str = "text-embedding-3-small"
    RAG_TOP_K: int = 3

    # --- MongoDB Atlas Configuration ---
    QDRANT_DATABASE_NAME: str = Field(
        default="customer_support_klnowledge_base",
        description="Name of the QdrantDB database.",
    )
    QDRANT_URI: str = Field(
        description="Connection URI for the local MongoDB Atlas instance.",
    )
    
    QDRANT_API_KEY: str = Field(
        description="API key for QdrantDB service authentication.",
    )

    # --- OpenAI API Configuration ---
    OPENAI_API_KEY: str = Field(
        description="API key for OpenAI service authentication.",
    )

    EVALUATION_LLM: str = "gpt-4.1-mini"

    KNOWLEDGE_DATASET_PATH: Path = Path("knowledge_base")
    EVALUATION_DATASET_FILE_PATH: Path =Path("evaluation_data/evaluation_data.json")

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