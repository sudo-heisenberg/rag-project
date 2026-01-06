"""Graph store implementation using Neo4j."""

import logging
from typing import List, Dict, Any, Optional

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

from src.config import config
from src.extraction.entity_extractor import Entity, Relationship

logger = logging.getLogger(__name__)

class GraphStore:
    """Graph store for knowledge graph using Neo4j."""

    def __init__(
        self,
        uri: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        Initialize graph store.

        Args:
            uri: Neo4j connection URI
            username: Neo4j username
            password: Neo4j password
        """
        self.uri = uri or config.graph_db.uri
        self.username = username or config.graph_db.username
        self.password = password or config.graph_db.password

        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password)
            )
            # Test connection
            self.driver.verify_connectivity()
            logger.info("Successfully connected to Neo4j")
        except ServiceUnavailable as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            raise

        self._create_indexes()

    def close(self) -> None:
        """Close the database connection."""
        if self.driver:
            self.driver.close()
            logger.info("Closed Neo4j connection")

    def _create_indexes(self) -> None:
        """Create indexes for better performance."""
        with self.driver.session() as session:
            # Create index on entity name
            session.run(
                "CREATE INDEX entity_name_index IF NOT EXISTS FOR (e:Entity) ON (e.name)"
            )
            logger.info("Created/verified database indexes")

    def add_entities(self, entities: List[Entity]) -> None:
        """
        Add entities to the graph.

        Args:
            entities: List of entities to add
        """
        logger.info(f"Adding {len(entities)} entities to graph")

        with self.driver.session() as session:
            for entity in entities:
                session.run(
                    """
                    MERGE (e:Entity {name: $name})
                    SET e.type = $type,
                        e.description = $description,
                        e.source_chunk_id = $source_chunk_id
                    """,
                    name=entity.name,
                    type=entity.entity_type,
                    description=entity.description,
                    source_chunk_id=entity.source_chunk_id
                )

        logger.info(f"Successfully added {len(entities)} entities")

    def add_relationships(self, relationships: List[Relationship]) -> None:
        """
        Add relationships to the graph.

        Args:
            relationships: List of relationships to add
        """
        logger.info(f"Adding {len(relationships)} relationships to graph")

        with self.driver.session() as session:
            for rel in relationships:
                # Create relationship between entities
                session.run(
                    """
                    MATCH (source:Entity {name: $source_name})
                    MATCH (target:Entity {name: $target_name})
                    MERGE (source)-[r:RELATES_TO {type: $rel_type}]->(target)
                    SET r.context = $context,
                        r.source_chunk_id = $source_chunk_id
                    """,
                    source_name=rel.source,
                    target_name=rel.target,
                    rel_type=rel.relationship_type,
                    context=rel.context,
                    source_chunk_id=rel.source_chunk_id
                )

        logger.info(f"Successfully added {len(relationships)} relationships")

    def find_entity(self, entity_name: str) -> Optional[Dict[str, Any]]:
        """
        Find an entity by name.

        Args:
            entity_name: Name of the entity

        Returns:
            Entity data or None if not found
        """
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (e:Entity {name: $name})
                RETURN e.name as name, e.type as type, e.description as description
                """,
                name=entity_name
            )

            record = result.single()
            if record:
                return dict(record)
            return None

    def get_related_entities(
        self,
        entity_name: str,
        max_depth: int = 2,
        relationship_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get entities related to a given entity.

        Args:
            entity_name: Name of the source entity
            max_depth: Maximum depth for traversal
            relationship_types: Filter by specific relationship types

        Returns:
            List of related entities with their relationships
        """
        logger.info(f"Finding entities related to '{entity_name}' (depth: {max_depth})")

        with self.driver.session() as session:
            if relationship_types:
                rel_filter = f"{{type: {relationship_types}}}"
            else:
                rel_filter = ""

            query = f"""
            MATCH path = (source:Entity {{name: $name}})-[r:RELATES_TO*1..{max_depth}]-(target:Entity)
            RETURN target.name as name,
                   target.type as type,
                   target.description as description,
                   [rel in relationships(path) | rel.type] as relationship_path,
                   length(path) as distance
            ORDER BY distance
            LIMIT 20
            """

            result = session.run(query, name=entity_name)
            return [dict(record) for record in result]

    def find_path(
        self,
        source_entity: str,
        target_entity: str,
        max_depth: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Find shortest path between two entities.

        Args:
            source_entity: Source entity name
            target_entity: Target entity name
            max_depth: Maximum path length

        Returns:
            List of paths with nodes and relationships
        """
        logger.info(f"Finding path from '{source_entity}' to '{target_entity}'")

        with self.driver.session() as session:
            query = f"""
            MATCH path = shortestPath(
                (source:Entity {{name: $source}})-[r:RELATES_TO*1..{max_depth}]-(target:Entity {{name: $target}})
            )
            RETURN [node in nodes(path) | node.name] as entities,
                   [rel in relationships(path) | rel.type] as relationships,
                   length(path) as path_length
            """

            result = session.run(
                query,
                source=source_entity,
                target=target_entity
            )

            return [dict(record) for record in result]

    def get_subgraph(
        self,
        entity_names: List[str],
        max_depth: int = 2
    ) -> Dict[str, Any]:
        """
        Get subgraph around specified entities.

        Args:
            entity_names: List of entity names
            max_depth: Maximum depth for expansion

        Returns:
            Subgraph with nodes and edges
        """
        logger.info(f"Retrieving subgraph for {len(entity_names)} entities")

        with self.driver.session() as session:
            query = f"""
            MATCH (source:Entity)
            WHERE source.name IN $names
            OPTIONAL MATCH path = (source)-[r:RELATES_TO*1..{max_depth}]-(connected:Entity)
            WITH collect(distinct source) + collect(distinct connected) as nodes,
                 collect(distinct r) as rels
            UNWIND nodes as node
            UNWIND rels as rel
            RETURN collect(distinct {{
                name: node.name,
                type: node.type,
                description: node.description
            }}) as nodes,
            collect(distinct {{
                source: startNode(rel).name,
                target: endNode(rel).name,
                type: rel.type
            }}) as edges
            """

            result = session.run(query, names=entity_names)
            record = result.single()

            if record:
                return {
                    'nodes': record['nodes'],
                    'edges': record['edges']
                }
            return {'nodes': [], 'edges': []}

    def clear_graph(self) -> None:
        """Clear all nodes and relationships from the graph."""
        logger.warning("Clearing all data from graph")

        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

        logger.info("Graph cleared")

    def get_graph_stats(self) -> Dict[str, Any]:
        """Get statistics about the graph."""
        with self.driver.session() as session:
            # Count entities
            entity_count = session.run("MATCH (e:Entity) RETURN count(e) as count").single()['count']

            # Count relationships
            rel_count = session.run("MATCH ()-[r:RELATES_TO]->() RETURN count(r) as count").single()['count']

            # Get entity types distribution
            type_dist = session.run(
                "MATCH (e:Entity) RETURN e.type as type, count(e) as count ORDER BY count DESC"
            )

            return {
                'total_entities': entity_count,
                'total_relationships': rel_count,
                'entity_types': [dict(record) for record in type_dist]
            }

# Example usage
if __name__ == "__main__":
    # graph_store = GraphStore()
    #
    # # Add some test entities
    # entities = [
    #     Entity("GPT-4", "TECHNOLOGY", "Large language model", "chunk_1"),
    #     Entity("OpenAI", "ORGANIZATION", "AI research company", "chunk_1"),
    #     Entity("Transformer", "CONCEPT", "Neural network architecture", "chunk_2")
    # ]
    # graph_store.add_entities(entities)
    #
    # # Add relationships
    # relationships = [
    #     Relationship("OpenAI", "GPT-4", "DEVELOPED", "", "chunk_1"),
    #     Relationship("GPT-4", "Transformer", "USES", "", "chunk_2")
    # ]
    # graph_store.add_relationships(relationships)
    #
    # # Query
    # related = graph_store.get_related_entities("GPT-4", max_depth=2)
    # print(f"Entities related to GPT-4: {related}")
    #
    # # Stats
    # stats = graph_store.get_graph_stats()
    # print(f"Graph stats: {stats}")
    #
    # graph_store.close()
    pass
