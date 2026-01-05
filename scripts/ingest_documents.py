"""Script to ingest documents into the GraphRAG system."""

import sys
from pathlib import Path
import logging

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.ingestion.document_loader import DocumentLoader
from src.ingestion.chunker import DocumentChunker
from src.extraction.entity_extractor import EntityExtractor
from src.vector.vector_store import VectorStore
from src.graph.graph_store import GraphStore
from src.config import config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main ingestion pipeline."""
    logger.info("Starting document ingestion pipeline...")

    # Initialize components
    logger.info("Initializing components...")
    loader = DocumentLoader()
    chunker = DocumentChunker()
    extractor = EntityExtractor()
    vector_store = VectorStore()
    graph_store = GraphStore()

    # Load documents
    logger.info(f"Loading documents from {config.raw_data_dir}")
    documents = loader.load_directory(config.raw_data_dir, recursive=True)

    if not documents:
        logger.warning("No documents found. Please add documents to data/raw/")
        return

    logger.info(f"Loaded {len(documents)} documents")

    # Chunk documents
    logger.info("Chunking documents...")
    chunks = chunker.chunk_documents(documents)
    logger.info(f"Created {len(chunks)} chunks")

    # Add chunks to vector store
    logger.info("Adding chunks to vector store...")
    vector_store.add_chunks(chunks)
    logger.info("✓ Vector store updated")

    # Extract entities and relationships
    logger.info("Extracting entities and relationships...")
    logger.warning("This step uses LLM and may take a while depending on document size...")

    # Process in batches to manage API calls
    batch_size = 10
    all_entities = []
    all_relationships = []

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}")

        entities, relationships = extractor.extract_from_chunks(batch)
        all_entities.extend(entities)
        all_relationships.extend(relationships)

    logger.info(f"Extracted {len(all_entities)} entities and {len(all_relationships)} relationships")

    # Add to graph store
    logger.info("Adding entities to graph database...")
    graph_store.add_entities(all_entities)
    logger.info("✓ Entities added")

    logger.info("Adding relationships to graph database...")
    graph_store.add_relationships(all_relationships)
    logger.info("✓ Relationships added")

    # Print statistics
    logger.info("\n" + "="*50)
    logger.info("INGESTION COMPLETE")
    logger.info("="*50)

    vector_stats = vector_store.get_collection_stats()
    graph_stats = graph_store.get_graph_stats()

    logger.info(f"Documents processed: {len(documents)}")
    logger.info(f"Chunks created: {vector_stats['total_chunks']}")
    logger.info(f"Entities extracted: {graph_stats['total_entities']}")
    logger.info(f"Relationships found: {graph_stats['total_relationships']}")

    logger.info("\nEntity type distribution:")
    for entity_type in graph_stats['entity_types'][:10]:
        logger.info(f"  - {entity_type['type']}: {entity_type['count']}")

    logger.info("\n✨ Your GraphRAG system is ready to use!")
    logger.info("Run: streamlit run app.py")

    # Close connections
    graph_store.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nIngestion interrupted by user")
    except Exception as e:
        logger.error(f"Error during ingestion: {str(e)}")
        raise
