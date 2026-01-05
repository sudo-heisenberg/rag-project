# 🔍 GraphRAG Research Assistant

An intelligent research assistant that helps technical teams quickly find insights across their documentation using hybrid GraphRAG (Vector Search + Knowledge Graph) technology.

## 🌟 Features

- **Hybrid Retrieval**: Combines traditional vector search with graph-based knowledge retrieval
- **Smart Query Routing**: Automatically determines the best retrieval strategy based on query type
- **Knowledge Graph**: Discovers and visualizes relationships between entities
- **LLM-Powered**: Uses advanced language models for entity extraction and answer generation
- **Interactive UI**: Clean Streamlit interface with graph visualization
- **Extensible**: Modular architecture supporting multiple LLM providers (OpenAI, Anthropic)

## 🏗️ Architecture

```
GraphRAG System
├── Document Ingestion
│   ├── PDF, DOCX, Markdown, TXT support
│   └── Smart chunking with overlap
├── Entity Extraction
│   ├── LLM-powered entity recognition
│   └── Relationship identification
├── Dual Storage
│   ├── Vector Store (ChromaDB) for semantic search
│   └── Graph Database (Neo4j) for relationships
├── Hybrid Retrieval
│   ├── Query understanding & routing
│   ├── Vector similarity search
│   └── Graph traversal
└── Answer Generation
    ├── Context-aware synthesis
    └── Source citation
```

## 📋 Prerequisites

- Python 3.9+
- Neo4j Database (free tier available)
- OpenAI API key OR Anthropic API key
- 4GB+ RAM recommended

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd rag-project

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
# Required:
# - OPENAI_API_KEY or ANTHROPIC_API_KEY
# - NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
```

### 3. Setup Neo4j

**Option A: Neo4j Aura (Cloud - Free Tier)**
1. Go to [https://neo4j.com/cloud/aura/](https://neo4j.com/cloud/aura/)
2. Create a free account
3. Create a new database instance
4. Copy the connection URI, username, and password to your `.env` file

**Option B: Local Neo4j**
```bash
# Using Docker
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  neo4j:latest

# Update .env:
# NEO4J_URI=bolt://localhost:7687
# NEO4J_USERNAME=neo4j
# NEO4J_PASSWORD=your_password
```

### 4. Add Documents

Place your research documents in the `data/raw/` directory:

```bash
# Supported formats: .txt, .pdf, .md, .docx
cp your_documents/*.pdf data/raw/
```

### 5. Ingest Documents

```bash
# Run the ingestion pipeline
python scripts/ingest_documents.py
```

### 6. Launch the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📚 Step-by-Step Build Guide

Follow this 7-day guide to build and understand the system:

### Day 1-2: Foundation & Data Ingestion

**Goal**: Set up the project and implement document processing

1. **Setup Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Understand Document Loading** ([src/ingestion/document_loader.py](src/ingestion/document_loader.py))
   - Review supported document formats
   - Learn how metadata is extracted
   - Test with sample documents

3. **Implement Chunking** ([src/ingestion/chunker.py](src/ingestion/chunker.py))
   - Understand fixed-size chunking with overlap
   - Experiment with different chunk sizes (500-1500 chars)
   - Learn why overlap matters for context preservation

4. **Exercise**: Create a custom document loader for a new format

### Day 3-4: Entity Extraction & Knowledge Graph

**Goal**: Build the knowledge graph from extracted entities

1. **Study Prompt Engineering** ([src/extraction/prompts.py](src/extraction/prompts.py))
   - Review the entity extraction prompt template
   - Understand few-shot learning examples
   - Learn structured output formatting

2. **Implement Entity Extractor** ([src/extraction/entity_extractor.py](src/extraction/entity_extractor.py))
   - Connect to your chosen LLM (OpenAI or Anthropic)
   - Extract entities from sample chunks
   - Identify relationships between entities

3. **Build Graph Store** ([src/graph/graph_store.py](src/graph/graph_store.py))
   - Create entities as nodes in Neo4j
   - Add relationships as edges
   - Query the graph structure

4. **Exercise**:
   ```python
   # Test entity extraction
   from src.ingestion.document_loader import DocumentLoader
   from src.ingestion.chunker import DocumentChunker
   from src.extraction.entity_extractor import EntityExtractor

   loader = DocumentLoader()
   chunker = DocumentChunker()
   extractor = EntityExtractor()

   doc = loader.load_document(Path("data/raw/sample.pdf"))
   chunks = chunker.chunk_document(doc)
   entities, relationships = extractor.extract_from_chunks(chunks[:5])

   print(f"Found {len(entities)} entities and {len(relationships)} relationships")
   ```

### Day 5-6: Hybrid Retrieval System

**Goal**: Implement vector search + graph traversal

1. **Setup Vector Store** ([src/vector/vector_store.py](src/vector/vector_store.py))
   - Initialize ChromaDB
   - Generate embeddings using sentence-transformers
   - Perform similarity search

2. **Implement Query Router** ([src/llm/query_router.py](src/llm/query_router.py))
   - Analyze query types (factual, comparative, relational, etc.)
   - Route to appropriate retrieval strategy
   - Test with different query types

3. **Build Hybrid Retriever** ([src/retrieval/hybrid_retriever.py](src/retrieval/hybrid_retriever.py))
   - Combine vector search results
   - Expand context using graph traversal
   - Rank and merge results

4. **Implement Answer Generator** ([src/llm/answer_generator.py](src/llm/answer_generator.py))
   - Format retrieved context
   - Generate comprehensive answers with citations
   - Handle graph context in responses

5. **Exercise**: Compare retrieval strategies
   ```python
   from src.retrieval.hybrid_retriever import HybridRetriever

   retriever = HybridRetriever(vector_store, graph_store)

   query = "How do transformers work?"

   # Test different strategies
   vector_results = retriever.retrieve(query, strategy="vector")
   graph_results = retriever.retrieve(query, strategy="graph")
   hybrid_results = retriever.retrieve(query, strategy="hybrid")

   # Compare results
   ```

### Day 7: UI & Integration

**Goal**: Bring everything together in a polished interface

1. **Study the Streamlit App** ([app.py](app.py))
   - Understand component initialization
   - Learn state management
   - Review the query flow

2. **Test End-to-End**
   - Run full ingestion pipeline
   - Test various query types
   - Visualize knowledge graph

3. **Optimize & Tune**
   - Adjust chunk sizes for your domain
   - Tune retrieval parameters
   - Customize prompts for your use case

4. **Exercise**: Add a new feature
   - Export conversation history
   - Add document filtering by date
   - Implement user feedback collection

## 🎯 Usage Examples

### Basic Query
```
Query: "What is a transformer model?"
Strategy: Vector (FACTUAL)
Result: Direct answer from most relevant chunks
```

### Comparative Query
```
Query: "How does GPT differ from BERT?"
Strategy: Hybrid (COMPARATIVE)
Result: Multi-source comparison with graph relationships
```

### Relational Query
```
Query: "What technologies influenced the development of attention mechanisms?"
Strategy: Graph (RELATIONAL)
Result: Graph traversal showing influence relationships
```

## 🔧 Configuration

### Key Parameters

**Document Processing** ([src/config.py](src/config.py))
```python
CHUNK_SIZE = 1000  # Characters per chunk
CHUNK_OVERLAP = 200  # Overlap between chunks
```

**Embedding Model**
```python
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
# Alternatives:
# - "all-mpnet-base-v2" (better quality, slower)
# - "paraphrase-multilingual-MiniLM-L12-v2" (multilingual)
```

**LLM Configuration**
```python
LLM_MODEL = "gpt-4-turbo-preview"
# Alternatives:
# - "gpt-3.5-turbo" (faster, cheaper)
# - "claude-3-opus-20240229" (Anthropic)
# - "claude-3-sonnet-20240229" (faster Claude)

TEMPERATURE = 0.7  # 0.0 = deterministic, 1.0 = creative
MAX_TOKENS = 4000  # Maximum response length
```

## 📊 System Architecture Details

### Module Breakdown

**Ingestion Pipeline** (`src/ingestion/`)
- `document_loader.py`: Multi-format document parsing
- `chunker.py`: Text segmentation with overlap

**Extraction** (`src/extraction/`)
- `entity_extractor.py`: LLM-powered entity extraction
- `prompts.py`: Engineered prompt templates

**Storage** (`src/vector/`, `src/graph/`)
- `vector_store.py`: ChromaDB integration for embeddings
- `graph_store.py`: Neo4j integration for relationships

**Retrieval** (`src/retrieval/`)
- `hybrid_retriever.py`: Unified retrieval interface

**LLM Integration** (`src/llm/`)
- `query_router.py`: Query understanding and routing
- `answer_generator.py`: Context-aware answer synthesis

## 🐛 Troubleshooting

### Common Issues

**1. Neo4j Connection Failed**
```
Error: Failed to connect to Neo4j
```
**Solution**: Verify Neo4j is running and credentials are correct in `.env`

**2. OpenAI API Key Invalid**
```
Error: Invalid API key
```
**Solution**: Check your API key in `.env` and ensure billing is set up

**3. ChromaDB Permission Error**
```
Error: Permission denied: data/chroma_db
```
**Solution**:
```bash
mkdir -p data/chroma_db
chmod 755 data/chroma_db
```

**4. Out of Memory**
```
Error: MemoryError during embedding generation
```
**Solution**: Process documents in smaller batches or use a smaller embedding model

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🚀 Advanced Features

### Custom Entity Types

Edit [src/extraction/prompts.py](src/extraction/prompts.py) to add domain-specific entity types:

```python
ENTITY_EXTRACTION_PROMPT = """
Extract entities of these types:
- ALGORITHM
- DATASET
- METRIC
- ARCHITECTURE
...
"""
```

### Multi-hop Reasoning

Adjust graph traversal depth in the UI or programmatically:

```python
retriever.retrieve(query, strategy="graph", graph_depth=3)
```

### Custom Retrieval Strategies

Implement custom logic in [src/retrieval/hybrid_retriever.py](src/retrieval/hybrid_retriever.py):

```python
def _custom_retrieval(self, query, n_results):
    # Your custom logic here
    pass
```

## 📈 Performance Optimization

### Indexing
- Create indexes on frequently queried entity properties in Neo4j
- Use ChromaDB's built-in optimization features

### Caching
- Cache frequent queries
- Store entity-chunk mappings

### Batch Processing
- Process documents in parallel
- Use bulk operations for database writes

## 🤝 Contributing

This is a starter project for learning. Suggested improvements:

1. Add support for more document formats (HTML, XML)
2. Implement semantic chunking (sentence boundaries)
3. Add support for images and tables
4. Implement query caching
5. Add user authentication
6. Create REST API endpoints
7. Add automated testing

## 📝 License

MIT License - feel free to use this project for learning and commercial purposes.

## 🎓 Learning Resources

- **LangChain Documentation**: https://python.langchain.com/
- **ChromaDB Guide**: https://docs.trychroma.com/
- **Neo4j Cypher Tutorial**: https://neo4j.com/developer/cypher/
- **Prompt Engineering Guide**: https://www.promptingguide.ai/
- **GraphRAG Research**: Microsoft GraphRAG paper

## 📧 Support

For issues and questions:
1. Check the troubleshooting section
2. Review example notebooks in `notebooks/`
3. Open an issue on GitHub

---

**Happy Building! 🚀**

Built with ❤️ for the AI/ML community
