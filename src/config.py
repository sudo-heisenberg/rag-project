"""Configuration management for GraphRAG system."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

class LLMConfig(BaseModel):
    """LLM configuration."""
    openai_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    anthropic_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    model_name: str = Field(default_factory=lambda: os.getenv("LLM_MODEL", "gpt-4-turbo-preview"))
    temperature: float = Field(default_factory=lambda: float(os.getenv("TEMPERATURE", "0.7")))
    max_tokens: int = Field(default_factory=lambda: int(os.getenv("MAX_TOKENS", "4000")))

class EmbeddingConfig(BaseModel):
    """Embedding configuration."""
    model_name: str = Field(
        default_factory=lambda: os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    )

class VectorStoreConfig(BaseModel):
    """Vector store configuration."""
    persist_directory: str = Field(
        default_factory=lambda: os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/chroma_db")
    )
    collection_name: str = "research_documents"

class GraphDBConfig(BaseModel):
    """Graph database configuration."""
    uri: str = Field(default_factory=lambda: os.getenv("NEO4J_URI", "bolt://localhost:7687"))
    username: str = Field(default_factory=lambda: os.getenv("NEO4J_USERNAME", "neo4j"))
    password: str = Field(default_factory=lambda: os.getenv("NEO4J_PASSWORD", "password"))

class DocumentProcessingConfig(BaseModel):
    """Document processing configuration."""
    chunk_size: int = Field(default_factory=lambda: int(os.getenv("CHUNK_SIZE", "1000")))
    chunk_overlap: int = Field(default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "200")))
    supported_extensions: list[str] = [".txt", ".pdf", ".md", ".docx"]

class Config(BaseModel):
    """Main application configuration."""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    vector_store: VectorStoreConfig = Field(default_factory=VectorStoreConfig)
    graph_db: GraphDBConfig = Field(default_factory=GraphDBConfig)
    document_processing: DocumentProcessingConfig = Field(default_factory=DocumentProcessingConfig)

    # Project paths
    project_root: Path = Path(__file__).parent.parent
    data_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent / "data")
    raw_data_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent / "data" / "raw")
    processed_data_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent / "data" / "processed")

# Global config instance
config = Config()
