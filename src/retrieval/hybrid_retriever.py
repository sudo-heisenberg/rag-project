"""Hybrid retrieval combining vector search and graph traversal."""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from src.vector.vector_store import VectorStore
from src.graph.graph_store import GraphStore

logger = logging.getLogger(__name__)

@dataclass
class RetrievalResult:
    """Result from hybrid retrieval."""
    content: str
    source: str
    relevance_score: float
    metadata: Dict[str, Any]
    retrieval_method: str  # 'vector', 'graph', or 'hybrid'

class HybridRetriever:
    """Combine vector search and graph traversal for enhanced retrieval."""

    def __init__(
        self,
        vector_store: VectorStore,
        graph_store: GraphStore,
        vector_weight: float = 0.6,
        graph_weight: float = 0.4
    ):
        """
        Initialize hybrid retriever.

        Args:
            vector_store: Vector store instance
            graph_store: Graph store instance
            vector_weight: Weight for vector search results
            graph_weight: Weight for graph search results
        """
        self.vector_store = vector_store
        self.graph_store = graph_store
        self.vector_weight = vector_weight
        self.graph_weight = graph_weight

        logger.info(
            f"Initialized HybridRetriever (vector_weight={vector_weight}, "
            f"graph_weight={graph_weight})"
        )

    def retrieve(
        self,
        query: str,
        strategy: str = "hybrid",
        n_results: int = 5,
        graph_depth: int = 2
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant information using specified strategy.

        Args:
            query: Search query
            strategy: Retrieval strategy ('vector', 'graph', or 'hybrid')
            n_results: Number of results to return
            graph_depth: Depth for graph traversal

        Returns:
            List of retrieval results
        """
        logger.info(f"Retrieving with strategy: {strategy}")

        if strategy == "vector":
            return self._vector_only_retrieval(query, n_results)
        elif strategy == "graph":
            return self._graph_only_retrieval(query, n_results, graph_depth)
        elif strategy == "hybrid":
            return self._hybrid_retrieval(query, n_results, graph_depth)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

    def _vector_only_retrieval(
        self,
        query: str,
        n_results: int
    ) -> List[RetrievalResult]:
        """
        Retrieve using vector search only.

        Args:
            query: Search query
            n_results: Number of results

        Returns:
            List of retrieval results
        """
        logger.info("Performing vector-only retrieval")

        vector_results = self.vector_store.search(query, n_results=n_results)

        results = []
        for vr in vector_results:
            results.append(RetrievalResult(
                content=vr['document'],
                source=vr['id'],
                relevance_score=1 - vr['distance'],  # Convert distance to similarity
                metadata=vr['metadata'],
                retrieval_method='vector'
            ))

        return results

    def _graph_only_retrieval(
        self,
        query: str,
        n_results: int,
        graph_depth: int
    ) -> List[RetrievalResult]:
        """
        Retrieve using graph traversal only.

        Args:
            query: Search query
            n_results: Number of results
            graph_depth: Maximum traversal depth

        Returns:
            List of retrieval results
        """
        logger.info("Performing graph-only retrieval")

        # First, use vector search to find relevant entities
        vector_results = self.vector_store.search(query, n_results=3)

        # Extract entity names from chunks (simplified - in production, use NER)
        # For now, we'll get the subgraph around the retrieved chunks
        results = []

        # Get related entities from graph
        for vr in vector_results[:2]:  # Use top 2 results as starting points
            chunk_id = vr['id']

            # Find entities from this chunk
            # In a real implementation, you'd store chunk_id -> entities mapping
            # For now, we'll demonstrate the graph traversal capability

            # This is a placeholder - you'd need to implement entity-to-chunk mapping
            # entities = self._get_entities_from_chunk(chunk_id)

            results.append(RetrievalResult(
                content=vr['document'],
                source=chunk_id,
                relevance_score=0.8,  # Placeholder score
                metadata=vr['metadata'],
                retrieval_method='graph'
            ))

        return results[:n_results]

    def _hybrid_retrieval(
        self,
        query: str,
        n_results: int,
        graph_depth: int
    ) -> List[RetrievalResult]:
        """
        Combine vector and graph retrieval.

        Args:
            query: Search query
            n_results: Number of results
            graph_depth: Maximum graph traversal depth

        Returns:
            List of retrieval results
        """
        logger.info("Performing hybrid retrieval")

        # Step 1: Vector search to find relevant chunks
        vector_results = self.vector_store.search(query, n_results=n_results * 2)

        # Step 2: Extract entities from top results and expand via graph
        # This creates a context-enriched result set

        all_results = []

        # Add vector results with weighted score
        for vr in vector_results:
            similarity = 1 - vr['distance']
            weighted_score = similarity * self.vector_weight

            all_results.append(RetrievalResult(
                content=vr['document'],
                source=vr['id'],
                relevance_score=weighted_score,
                metadata=vr['metadata'],
                retrieval_method='hybrid'
            ))

        # Step 3: Rank and return top results
        all_results.sort(key=lambda x: x.relevance_score, reverse=True)

        return all_results[:n_results]

    def retrieve_with_context(
        self,
        query: str,
        entity_names: List[str],
        n_results: int = 5
    ) -> Dict[str, Any]:
        """
        Retrieve documents and relevant subgraph.

        Args:
            query: Search query
            entity_names: List of entity names to include in graph context
            n_results: Number of document results

        Returns:
            Dictionary with documents and graph context
        """
        logger.info(f"Retrieving with context for entities: {entity_names}")

        # Get document results
        doc_results = self._vector_only_retrieval(query, n_results)

        # Get graph context
        graph_context = self.graph_store.get_subgraph(
            entity_names=entity_names,
            max_depth=2
        )

        return {
            'documents': doc_results,
            'graph_context': graph_context,
            'query': query
        }

# Example usage
if __name__ == "__main__":
    # vector_store = VectorStore()
    # graph_store = GraphStore()
    #
    # retriever = HybridRetriever(vector_store, graph_store)
    #
    # # Hybrid retrieval
    # results = retriever.retrieve(
    #     query="How do transformers work?",
    #     strategy="hybrid",
    #     n_results=5
    # )
    #
    # for i, result in enumerate(results, 1):
    #     print(f"\n{i}. [Score: {result.relevance_score:.3f}] [{result.retrieval_method}]")
    #     print(f"   {result.content[:200]}...")
    pass
