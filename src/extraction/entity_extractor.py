"""Entity extraction using LLM-powered analysis."""

import json
import logging
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, SystemMessage

from src.config import config
from src.extraction.prompts import ENTITY_EXTRACTION_PROMPT, FEW_SHOT_ENTITY_EXAMPLES
from src.ingestion.chunker import Chunk

logger = logging.getLogger(__name__)

@dataclass
class Entity:
    """Entity data structure."""
    name: str
    entity_type: str
    description: str
    source_chunk_id: str
    metadata: Dict[str, Any] = None

@dataclass
class Relationship:
    """Relationship data structure."""
    source: str
    target: str
    relationship_type: str
    context: str
    source_chunk_id: str

class EntityExtractor:
    """Extract entities and relationships from text using LLM."""

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize entity extractor.

        Args:
            model_name: LLM model to use (overrides config)
        """
        self.model_name = model_name or config.llm.model_name

        # Initialize LLM
        if "gpt" in self.model_name.lower():
            self.llm = ChatOpenAI(
                model=self.model_name,
                temperature=config.llm.temperature,
                api_key=config.llm.openai_api_key
            )
        elif "claude" in self.model_name.lower():
            self.llm = ChatAnthropic(
                model=self.model_name,
                temperature=config.llm.temperature,
                api_key=config.llm.anthropic_api_key
            )
        else:
            raise ValueError(f"Unsupported model: {self.model_name}")

        logger.info(f"Initialized EntityExtractor with model: {self.model_name}")

    def extract_from_chunk(self, chunk: Chunk) -> tuple[List[Entity], List[Relationship]]:
        """
        Extract entities and relationships from a text chunk.

        Args:
            chunk: Text chunk to process

        Returns:
            Tuple of (entities, relationships)
        """
        logger.info(f"Extracting entities from chunk: {chunk.chunk_id}")

        # Prepare prompt
        prompt = ENTITY_EXTRACTION_PROMPT.format(text=chunk.content)

        # Call LLM
        try:
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            content = response.content

            # Parse response
            entities, relationships = self._parse_extraction_response(
                content, chunk.chunk_id
            )

            logger.info(f"Extracted {len(entities)} entities and {len(relationships)} relationships")
            return entities, relationships

        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            return [], []

    def extract_from_chunks(
        self, chunks: List[Chunk]
    ) -> tuple[List[Entity], List[Relationship]]:
        """
        Extract entities from multiple chunks.

        Args:
            chunks: List of chunks to process

        Returns:
            Tuple of (all entities, all relationships)
        """
        all_entities = []
        all_relationships = []

        for chunk in chunks:
            entities, relationships = self.extract_from_chunk(chunk)
            all_entities.extend(entities)
            all_relationships.extend(relationships)

        # Deduplicate entities by name
        unique_entities = self._deduplicate_entities(all_entities)

        logger.info(
            f"Total extracted: {len(unique_entities)} unique entities, "
            f"{len(all_relationships)} relationships"
        )

        return unique_entities, all_relationships

    def _parse_extraction_response(
        self, response: str, chunk_id: str
    ) -> tuple[List[Entity], List[Relationship]]:
        """
        Parse LLM response to extract structured entities and relationships.

        Args:
            response: LLM response text
            chunk_id: Source chunk ID

        Returns:
            Tuple of (entities, relationships)
        """
        entities = []
        relationships = []

        # Split response into entities and relationships sections
        parts = response.split("RELATIONSHIPS:")
        entities_text = parts[0].replace("ENTITIES:", "").strip()

        if len(parts) > 1:
            relationships_text = parts[1].strip()
        else:
            relationships_text = ""

        # Parse entities
        entity_pattern = r"- Name: (.+?), Type: (.+?), Description: (.+?)(?=\n-|\n\n|$)"
        for match in re.finditer(entity_pattern, entities_text, re.DOTALL):
            name = match.group(1).strip()
            entity_type = match.group(2).strip()
            description = match.group(3).strip()

            entities.append(Entity(
                name=name,
                entity_type=entity_type,
                description=description,
                source_chunk_id=chunk_id,
                metadata={}
            ))

        # Parse relationships
        relationship_pattern = r"\((.+?)\) -\[(.+?)\]-> \((.+?)\)"
        for match in re.finditer(relationship_pattern, relationships_text):
            source = match.group(1).strip()
            rel_type = match.group(2).strip()
            target = match.group(3).strip()

            relationships.append(Relationship(
                source=source,
                target=target,
                relationship_type=rel_type,
                context="",
                source_chunk_id=chunk_id
            ))

        return entities, relationships

    def _deduplicate_entities(self, entities: List[Entity]) -> List[Entity]:
        """
        Deduplicate entities by name (case-insensitive).

        Args:
            entities: List of entities

        Returns:
            Deduplicated list
        """
        seen = {}
        unique = []

        for entity in entities:
            key = entity.name.lower()
            if key not in seen:
                seen[key] = True
                unique.append(entity)

        return unique

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
    # # Extract entities
    # extractor = EntityExtractor()
    # entities, relationships = extractor.extract_from_chunks(chunks[:5])  # Test on first 5 chunks
    #
    # print(f"\nEntities: {len(entities)}")
    # for entity in entities[:10]:
    #     print(f"  - {entity.name} ({entity.entity_type})")
    #
    # print(f"\nRelationships: {len(relationships)}")
    # for rel in relationships[:10]:
    #     print(f"  - {rel.source} -[{rel.relationship_type}]-> {rel.target}")
