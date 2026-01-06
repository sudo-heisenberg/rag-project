"""Answer generation using LLM."""

import logging
from typing import List, Dict, Any

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, SystemMessage

from src.config import config
from src.extraction.prompts import ANSWER_SYNTHESIS_PROMPT
from src.retrieval.hybrid_retriever import RetrievalResult

logger = logging.getLogger(__name__)

class AnswerGenerator:
    """Generate answers using LLM with retrieved context."""

    def __init__(self, model_name: str = None):
        """
        Initialize answer generator.

        Args:
            model_name: LLM model to use
        """
        self.model_name = model_name or config.llm.model_name

        # Initialize LLM
        if "gpt" in self.model_name.lower():
            self.llm = ChatOpenAI(
                model=self.model_name,
                temperature=config.llm.temperature,
                max_tokens=config.llm.max_tokens,
                api_key=config.llm.openai_api_key
            )
        elif "claude" in self.model_name.lower():
            self.llm = ChatAnthropic(
                model=self.model_name,
                temperature=config.llm.temperature,
                max_tokens=config.llm.max_tokens,
                api_key=config.llm.anthropic_api_key
            )
        else:
            raise ValueError(f"Unsupported model: {self.model_name}")

        logger.info(f"Initialized AnswerGenerator with model: {self.model_name}")

    def generate_answer(
        self,
        query: str,
        retrieval_results: List[RetrievalResult],
        graph_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate answer from query and retrieved context.

        Args:
            query: User query
            retrieval_results: Retrieved documents
            graph_context: Optional graph context

        Returns:
            Dictionary with answer and metadata
        """
        logger.info(f"Generating answer for query: '{query}'")

        # Format context from retrieval results
        context = self._format_context(retrieval_results)

        # Format graph context
        graph_context_str = self._format_graph_context(graph_context) if graph_context else "No graph context available."

        # Prepare prompt
        prompt = ANSWER_SYNTHESIS_PROMPT.format(
            query=query,
            context=context,
            graph_context=graph_context_str
        )

        try:
            # Generate answer
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)

            answer = response.content.strip()

            # Extract sources
            sources = [result.source for result in retrieval_results]

            return {
                "answer": answer,
                "sources": sources,
                "query": query,
                "retrieval_count": len(retrieval_results),
                "model": self.model_name
            }

        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return {
                "answer": "I apologize, but I encountered an error generating the answer. Please try again.",
                "sources": [],
                "query": query,
                "error": str(e)
            }

    def _format_context(self, results: List[RetrievalResult]) -> str:
        """
        Format retrieval results into context string.

        Args:
            results: List of retrieval results

        Returns:
            Formatted context string
        """
        context_parts = []

        for i, result in enumerate(results, 1):
            context_parts.append(
                f"[Document {i}] (Source: {result.source}, Relevance: {result.relevance_score:.2f})\n"
                f"{result.content}\n"
            )

        return "\n".join(context_parts)

    def _format_graph_context(self, graph_context: Dict[str, Any]) -> str:
        """
        Format graph context into readable string.

        Args:
            graph_context: Graph context dictionary

        Returns:
            Formatted graph context string
        """
        if not graph_context or not graph_context.get('nodes'):
            return "No graph context available."

        parts = []

        # Format nodes
        nodes = graph_context.get('nodes', [])
        if nodes:
            parts.append("Related Entities:")
            for node in nodes[:10]:  # Limit to top 10
                parts.append(
                    f"  - {node.get('name')} ({node.get('type')}): {node.get('description', 'N/A')}"
                )

        # Format edges
        edges = graph_context.get('edges', [])
        if edges:
            parts.append("\nRelationships:")
            for edge in edges[:15]:  # Limit to top 15
                parts.append(
                    f"  - {edge.get('source')} -[{edge.get('type')}]-> {edge.get('target')}"
                )

        return "\n".join(parts)

# Example usage
if __name__ == "__main__":
    # from src.retrieval.hybrid_retriever import RetrievalResult
    #
    # generator = AnswerGenerator()
    #
    # # Mock retrieval results
    # results = [
    #     RetrievalResult(
    #         content="Transformers are a type of neural network architecture...",
    #         source="doc_1_chunk_0",
    #         relevance_score=0.95,
    #         metadata={},
    #         retrieval_method="hybrid"
    #     )
    # ]
    #
    # # Generate answer
    # answer_data = generator.generate_answer(
    #     query="What is a transformer?",
    #     retrieval_results=results
    # )
    #
    # print(f"Answer: {answer_data['answer']}")
    # print(f"Sources: {answer_data['sources']}")
    pass
