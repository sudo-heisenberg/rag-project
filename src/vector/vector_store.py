"""Vector store implementation using ChromaDB."""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from src.config import config
from src.ingestion.chunker import Chunk

logger = logging.getLogger(__name__)

class VectorStore:
    """Vector store for semantic search using ChromaDB."""

    def __init__(
        self,
        collection_name: Optional[str] = None,
        persist_directory: Optional[str] = None,
        embedding_model: Optional[str] = None
    ):
        """
        Initialize vector store.

        Args:
            collection_name: Name of the collection
            persist_directory: Directory to persist the database
            embedding_model: Name of the embedding model
        """
        self.collection_name = collection_name or config.vector_store.collection_name
        self.persist_directory = persist_directory or config.vector_store.persist_directory
        self.embedding_model_name = embedding_model or config.embedding.model_name

        # Create persist directory if it doesn't exist
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )

        # Initialize embedding model
        logger.info(f"Loading embedding model: {self.embedding_model_name}")
        self.embedding_model = SentenceTransformer(self.embedding_model_name)

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Research documents collection"}
        )

        logger.info(f"Initialized VectorStore with collection: {self.collection_name}")

    def add_chunks(self, chunks: List[Chunk]) -> None:
        """
        Add text chunks to the vector store.

        Args:
            chunks: List of chunks to add
        """
        logger.info(f"Adding {len(chunks)} chunks to vector store")

        # Prepare data for insertion
        documents = [chunk.content for chunk in chunks]
        ids = [chunk.chunk_id for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]

        # Generate embeddings
        embeddings = self.embedding_model.encode(
            documents,
            show_progress_bar=True,
            convert_to_numpy=True
        ).tolist()

        # Add to collection in batches
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            end_idx = min(i + batch_size, len(documents))

            self.collection.add(
                documents=documents[i:end_idx],
                embeddings=embeddings[i:end_idx],
                ids=ids[i:end_idx],
                metadatas=metadatas[i:end_idx]
            )

        logger.info(f"Successfully added {len(chunks)} chunks")

    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.

        Args:
            query: Search query
            n_results: Number of results to return
            where: Metadata filter conditions

        Returns:
            List of search results with documents, distances, and metadata
        """
        logger.info(f"Searching vector store for: '{query}'")

        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0].tolist()

        # Search collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )

        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'id': results['ids'][0][i],
                'document': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
            })

        logger.info(f"Found {len(formatted_results)} results")
        return formatted_results

    def get_by_ids(self, ids: List[str]) -> List[Dict[str, Any]]:
        """
        Retrieve chunks by their IDs.

        Args:
            ids: List of chunk IDs

        Returns:
            List of chunks with their data
        """
        results = self.collection.get(ids=ids)

        formatted_results = []
        for i in range(len(results['ids'])):
            formatted_results.append({
                'id': results['ids'][i],
                'document': results['documents'][i],
                'metadata': results['metadatas'][i]
            })

        return formatted_results

    def delete_collection(self) -> None:
        """Delete the collection."""
        logger.warning(f"Deleting collection: {self.collection_name}")
        self.client.delete_collection(name=self.collection_name)

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "total_chunks": count,
            "embedding_model": self.embedding_model_name
        }

# Example usage
if __name__ == "__main__":
    from src.ingestion.document_loader import DocumentLoader
    from src.ingestion.chunker import DocumentChunker
    from pathlib import Path

    # Load and chunk documents
    # loader = DocumentLoader()
    # docs = loader.load_directory(Path("data/raw"))
    #
    # chunker = DocumentChunker()
    # chunks = chunker.chunk_documents(docs)
    #
    # # Create vector store and add chunks
    # vector_store = VectorStore()
    # vector_store.add_chunks(chunks)
    #
    # # Search
    # results = vector_store.search("What is a transformer model?", n_results=5)
    # for result in results:
    #     print(f"\nRelevance: {1 - result['distance']:.3f}")
    #     print(f"Content: {result['document'][:200]}...")
    #
    # # Get stats
    # stats = vector_store.get_collection_stats()
    # print(f"\nCollection stats: {stats}")
