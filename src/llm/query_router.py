"""Query understanding and routing logic."""

import json
import logging
from typing import Dict, Any, List
from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage

from src.config import config
from src.extraction.prompts import QUERY_UNDERSTANDING_PROMPT

logger = logging.getLogger(__name__)

@dataclass
class QueryAnalysis:
    """Query analysis result."""
    category: str  # FACTUAL, COMPARATIVE, RELATIONAL, EXPLORATORY, TREND_ANALYSIS
    key_entities: List[str]
    strategy: str  # VECTOR_ONLY, GRAPH_ONLY, HYBRID
    reasoning: str

class QueryRouter:
    """Analyze queries and determine optimal retrieval strategy."""

    def __init__(self, model_name: str = None):
        """
        Initialize query router.

        Args:
            model_name: LLM model to use
        """
        self.model_name = model_name or config.llm.model_name

        # Initialize LLM
        if "gpt" in self.model_name.lower():
            self.llm = ChatOpenAI(
                model=self.model_name,
                temperature=0.3,  # Lower temperature for more consistent routing
                api_key=config.llm.openai_api_key
            )
        elif "claude" in self.model_name.lower():
            self.llm = ChatAnthropic(
                model=self.model_name,
                temperature=0.3,
                api_key=config.llm.anthropic_api_key
            )
        else:
            raise ValueError(f"Unsupported model: {self.model_name}")

        logger.info(f"Initialized QueryRouter with model: {self.model_name}")

    def analyze_query(self, query: str) -> QueryAnalysis:
        """
        Analyze query and determine retrieval strategy.

        Args:
            query: User query

        Returns:
            QueryAnalysis with strategy recommendation
        """
        logger.info(f"Analyzing query: '{query}'")

        # Prepare prompt
        prompt = QUERY_UNDERSTANDING_PROMPT.format(query=query)

        try:
            # Call LLM
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)

            # Parse JSON response
            content = response.content.strip()

            # Extract JSON from response (handle markdown code blocks)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            analysis_dict = json.loads(content)

            analysis = QueryAnalysis(
                category=analysis_dict.get("category", "EXPLORATORY"),
                key_entities=analysis_dict.get("key_entities", []),
                strategy=analysis_dict.get("strategy", "HYBRID"),
                reasoning=analysis_dict.get("reasoning", "")
            )

            logger.info(
                f"Query analysis: category={analysis.category}, "
                f"strategy={analysis.strategy}"
            )

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing query: {str(e)}")
            # Fallback to hybrid strategy
            return QueryAnalysis(
                category="EXPLORATORY",
                key_entities=[],
                strategy="HYBRID",
                reasoning="Fallback to hybrid strategy due to analysis error"
            )

    def route_query(self, query: str) -> Dict[str, Any]:
        """
        Route query to appropriate retrieval strategy.

        Args:
            query: User query

        Returns:
            Dictionary with routing information
        """
        analysis = self.analyze_query(query)

        return {
            "query": query,
            "analysis": analysis,
            "retrieval_params": self._get_retrieval_params(analysis)
        }

    def _get_retrieval_params(self, analysis: QueryAnalysis) -> Dict[str, Any]:
        """
        Get retrieval parameters based on query analysis.

        Args:
            analysis: Query analysis result

        Returns:
            Dictionary with retrieval parameters
        """
        # Default parameters
        params = {
            "strategy": analysis.strategy.lower(),
            "n_results": 5,
            "graph_depth": 2
        }

        # Adjust based on category
        if analysis.category == "FACTUAL":
            params["n_results"] = 3
            params["strategy"] = "vector"

        elif analysis.category == "COMPARATIVE":
            params["n_results"] = 8
            params["strategy"] = "hybrid"
            params["graph_depth"] = 2

        elif analysis.category == "RELATIONAL":
            params["n_results"] = 5
            params["strategy"] = "hybrid"
            params["graph_depth"] = 3

        elif analysis.category == "EXPLORATORY":
            params["n_results"] = 10
            params["strategy"] = "hybrid"
            params["graph_depth"] = 2

        elif analysis.category == "TREND_ANALYSIS":
            params["n_results"] = 15
            params["strategy"] = "hybrid"
            params["graph_depth"] = 3

        return params

# Example usage
if __name__ == "__main__":
    router = QueryRouter()

    # Test different query types
    queries = [
        "What is a transformer model?",
        "How does GPT differ from BERT?",
        "What papers influenced the development of attention mechanisms?",
        "What are recent advances in language models?",
    ]

    # for query in queries:
    #     print(f"\nQuery: {query}")
    #     routing = router.route_query(query)
    #     print(f"Category: {routing['analysis'].category}")
    #     print(f"Strategy: {routing['analysis'].strategy}")
    #     print(f"Params: {routing['retrieval_params']}")
