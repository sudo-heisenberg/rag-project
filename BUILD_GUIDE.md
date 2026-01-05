# GraphRAG Research Assistant - 7-Day Build Guide

This guide walks you through building and understanding the GraphRAG system over one week. Each day focuses on specific components with hands-on exercises.

## Overview

**Project Goal**: Build an intelligent research assistant using GraphRAG (Graph + RAG) technology

**What You'll Learn**:
- Document processing and chunking strategies
- Prompt engineering for entity extraction
- Vector embeddings and semantic search
- Knowledge graph construction with Neo4j
- Hybrid retrieval strategies
- LLM integration and answer generation
- Building production-ready UI with Streamlit

## Day 1: Foundation & Document Ingestion

**Time**: 2-3 hours

### Morning: Setup & Architecture

1. **Review project structure**
   ```bash
   tree -L 2 src/
   ```

2. **Study the architecture**
   - Read [README.md](README.md) architecture section
   - Understand data flow: Documents → Chunks → Embeddings + Graph → Retrieval → Answer

3. **Run the system**
   ```bash
   python scripts/test_system.py
   streamlit run app.py
   ```

### Afternoon: Document Processing

1. **Study document loader** ([src/ingestion/document_loader.py](src/ingestion/document_loader.py))
   ```python
   # Try loading different document types
   from src.ingestion.document_loader import DocumentLoader
   from pathlib import Path

   loader = DocumentLoader()

   # Load a single document
   doc = loader.load_document(Path("data/raw/sample_document.txt"))
   print(f"Loaded: {doc.doc_id}")
   print(f"Content length: {len(doc.content)} chars")
   print(f"Metadata: {doc.metadata}")
   ```

2. **Experiment with chunking** ([src/ingestion/chunker.py](src/ingestion/chunker.py))
   ```python
   from src.ingestion.chunker import DocumentChunker

   # Try different chunk sizes
   chunker = DocumentChunker(chunk_size=500, chunk_overlap=50)
   chunks = chunker.chunk_document(doc)

   print(f"Created {len(chunks)} chunks")
   for i, chunk in enumerate(chunks[:3]):
       print(f"\nChunk {i}:")
       print(chunk.content[:100] + "...")
   ```

### Exercise 1: Custom Document Format

**Task**: Add support for HTML documents

**Steps**:
1. Add `.html` to supported formats in `document_loader.py`
2. Implement `_load_html()` method using BeautifulSoup
3. Test with an HTML file

**Solution hint**: Use `soup.get_text()` to extract plain text

### Day 1 Checkpoint
- [ ] Understand document loading flow
- [ ] Grasp chunking strategy
- [ ] Successfully load and chunk a document
- [ ] Complete Exercise 1

---

## Day 2: Prompt Engineering & Entity Extraction

**Time**: 3-4 hours

### Morning: Prompt Engineering

1. **Study prompt templates** ([src/extraction/prompts.py](src/extraction/prompts.py))
   - Review `ENTITY_EXTRACTION_PROMPT`
   - Understand few-shot examples
   - Learn structured output formatting

2. **Understand the pattern**:
   ```
   System Context
   → Few-shot Examples
   → Task Description
   → Input Text
   → Expected Output Format
   ```

### Afternoon: Entity Extraction

1. **Study entity extractor** ([src/extraction/entity_extractor.py](src/extraction/entity_extractor.py))

2. **Test entity extraction**:
   ```python
   from src.extraction.entity_extractor import EntityExtractor

   extractor = EntityExtractor()

   # Extract from a single chunk
   entities, relationships = extractor.extract_from_chunk(chunks[0])

   print(f"Found {len(entities)} entities:")
   for entity in entities:
       print(f"  {entity.name} ({entity.entity_type}): {entity.description}")

   print(f"\nFound {len(relationships)} relationships:")
   for rel in relationships:
       print(f"  {rel.source} -[{rel.relationship_type}]-> {rel.target}")
   ```

3. **Monitor API usage**:
   - Check your OpenAI/Anthropic dashboard
   - Understand token consumption
   - Learn to optimize prompts

### Exercise 2: Custom Entity Types

**Task**: Add domain-specific entity types

**Example**: For legal documents, add:
- STATUTE
- CASE
- LEGAL_PRINCIPLE
- PRECEDENT

**Steps**:
1. Edit `ENTITY_EXTRACTION_PROMPT` in `prompts.py`
2. Add new entity types to the list
3. Add few-shot examples for these types
4. Test with domain-specific documents

### Exercise 3: Relationship Extraction

**Task**: Improve relationship detection

**Steps**:
1. Add more relationship types (CONTRADICTS, SUPPORTS, EXTENDS)
2. Update the prompt to identify these relationships
3. Test on documents with conflicting information

### Day 2 Checkpoint
- [ ] Understand prompt engineering principles
- [ ] Grasp entity extraction process
- [ ] Successfully extract entities from documents
- [ ] Complete Exercises 2 & 3

---

## Day 3: Vector Store & Embeddings

**Time**: 2-3 hours

### Morning: Embedding Fundamentals

1. **Learn about embeddings**:
   - Read: What are text embeddings?
   - Understand semantic similarity
   - Learn about vector databases

2. **Study vector store** ([src/vector/vector_store.py](src/vector/vector_store.py))

3. **Test embeddings**:
   ```python
   from src.vector.vector_store import VectorStore
   from sentence_transformers import SentenceTransformer

   # Generate embeddings
   model = SentenceTransformer('all-MiniLM-L6-v2')

   sentences = [
       "The transformer architecture uses attention mechanisms",
       "Attention is all you need for sequence modeling",
       "Dogs are popular pets"
   ]

   embeddings = model.encode(sentences)

   # Compute similarity
   from sklearn.metrics.pairwise import cosine_similarity
   similarities = cosine_similarity(embeddings)
   print("Similarity matrix:")
   print(similarities)
   ```

### Afternoon: Vector Search

1. **Add documents to vector store**:
   ```python
   vector_store = VectorStore()
   vector_store.add_chunks(chunks)

   # Verify
   stats = vector_store.get_collection_stats()
   print(f"Total chunks in store: {stats['total_chunks']}")
   ```

2. **Perform searches**:
   ```python
   # Semantic search
   query = "How does attention mechanism work?"
   results = vector_store.search(query, n_results=5)

   for i, result in enumerate(results, 1):
       print(f"\n{i}. Relevance: {1 - result['distance']:.3f}")
       print(f"   Content: {result['document'][:200]}...")
   ```

### Exercise 4: Embedding Model Comparison

**Task**: Compare different embedding models

**Models to test**:
- `all-MiniLM-L6-v2` (fast, 384 dims)
- `all-mpnet-base-v2` (better quality, 768 dims)
- `paraphrase-multilingual-MiniLM-L12-v2` (multilingual)

**Metrics**:
- Embedding generation time
- Search quality (qualitative)
- Memory usage

### Day 3 Checkpoint
- [ ] Understand text embeddings
- [ ] Successfully add documents to vector store
- [ ] Perform semantic searches
- [ ] Complete Exercise 4

---

## Day 4: Knowledge Graph with Neo4j

**Time**: 3-4 hours

### Morning: Graph Database Concepts

1. **Learn Neo4j basics**:
   - Nodes (entities)
   - Relationships (edges)
   - Properties
   - Cypher query language

2. **Open Neo4j Browser**:
   - URL: `http://localhost:7474` or your Aura URL
   - Practice basic Cypher:
     ```cypher
     // Create a node
     CREATE (n:Entity {name: "GPT-4", type: "TECHNOLOGY"})

     // Find nodes
     MATCH (n:Entity) RETURN n LIMIT 10

     // Create relationship
     MATCH (a:Entity {name: "OpenAI"})
     MATCH (b:Entity {name: "GPT-4"})
     CREATE (a)-[r:DEVELOPED]->(b)
     ```

### Afternoon: Building the Knowledge Graph

1. **Study graph store** ([src/graph/graph_store.py](src/graph/graph_store.py))

2. **Add entities to graph**:
   ```python
   from src.graph.graph_store import GraphStore

   graph_store = GraphStore()

   # Add entities
   graph_store.add_entities(entities)

   # Add relationships
   graph_store.add_relationships(relationships)

   # Query
   stats = graph_store.get_graph_stats()
   print(f"Entities: {stats['total_entities']}")
   print(f"Relationships: {stats['total_relationships']}")
   ```

3. **Explore graph queries**:
   ```python
   # Find related entities
   related = graph_store.get_related_entities("GPT-4", max_depth=2)
   for entity in related:
       print(f"{entity['name']} - Distance: {entity['distance']}")

   # Find path between entities
   paths = graph_store.find_path("GPT-4", "Attention Mechanism")
   if paths:
       path = paths[0]
       print(f"Path: {' -> '.join(path['entities'])}")
       print(f"Relationships: {path['relationships']}")
   ```

### Exercise 5: Graph Visualization

**Task**: Visualize the knowledge graph in Neo4j Browser

**Steps**:
1. Run query: `MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 50`
2. Explore different visualization layouts
3. Filter by entity types: `MATCH (n:Entity {type: "TECHNOLOGY"}) RETURN n`
4. Find highly connected nodes (hubs)

### Exercise 6: Advanced Graph Queries

**Task**: Write Cypher queries for:
1. Most influential entities (highest degree centrality)
2. Entities that connect different domains (bridges)
3. Clusters of related concepts

**Example**:
```cypher
// Find most connected entities
MATCH (n:Entity)-[r]-()
RETURN n.name, n.type, count(r) as connections
ORDER BY connections DESC
LIMIT 10
```

### Day 4 Checkpoint
- [ ] Understand graph database concepts
- [ ] Successfully build knowledge graph
- [ ] Query graph using Cypher
- [ ] Complete Exercises 5 & 6

---

## Day 5: Hybrid Retrieval System

**Time**: 3-4 hours

### Morning: Query Understanding

1. **Study query router** ([src/llm/query_router.py](src/llm/query_router.py))

2. **Test query classification**:
   ```python
   from src.llm.query_router import QueryRouter

   router = QueryRouter()

   queries = [
       "What is a transformer?",  # FACTUAL
       "Compare GPT and BERT",    # COMPARATIVE
       "How did attention mechanisms influence modern NLP?",  # RELATIONAL
       "What are recent advances in language models?"  # EXPLORATORY
   ]

   for query in queries:
       analysis = router.analyze_query(query)
       print(f"\nQuery: {query}")
       print(f"Category: {analysis.category}")
       print(f"Strategy: {analysis.strategy}")
       print(f"Entities: {analysis.key_entities}")
   ```

### Afternoon: Hybrid Retrieval

1. **Study hybrid retriever** ([src/retrieval/hybrid_retriever.py](src/retrieval/hybrid_retriever.py))

2. **Compare retrieval strategies**:
   ```python
   from src.retrieval.hybrid_retriever import HybridRetriever

   retriever = HybridRetriever(vector_store, graph_store)

   query = "How do transformers use attention?"

   # Vector only
   vector_results = retriever.retrieve(query, strategy="vector", n_results=5)

   # Hybrid
   hybrid_results = retriever.retrieve(query, strategy="hybrid", n_results=5)

   print("Vector results:")
   for r in vector_results[:3]:
       print(f"  {r.relevance_score:.3f}: {r.content[:100]}...")

   print("\nHybrid results:")
   for r in hybrid_results[:3]:
       print(f"  {r.relevance_score:.3f}: {r.content[:100]}...")
   ```

### Exercise 7: Retrieval Strategy Comparison

**Task**: Quantitatively compare retrieval strategies

**Metrics**:
1. Relevance (manual evaluation)
2. Coverage (unique information retrieved)
3. Speed (retrieval time)

**Test queries**:
- 5 factual questions
- 5 comparative questions
- 5 relational questions

**Create a comparison table**:
```
| Query Type    | Vector | Graph | Hybrid |
|--------------|--------|-------|--------|
| Factual      | 4.2/5  | 3.1/5 | 4.5/5  |
| Comparative  | 3.8/5  | 4.0/5 | 4.7/5  |
| Relational   | 3.2/5  | 4.5/5 | 4.8/5  |
```

### Day 5 Checkpoint
- [ ] Understand query routing logic
- [ ] Compare retrieval strategies
- [ ] Identify when to use each strategy
- [ ] Complete Exercise 7

---

## Day 6: Answer Generation & LLM Integration

**Time**: 2-3 hours

### Morning: Answer Generation

1. **Study answer generator** ([src/llm/answer_generator.py](src/llm/answer_generator.py))

2. **Test answer generation**:
   ```python
   from src.llm.answer_generator import AnswerGenerator

   generator = AnswerGenerator()

   query = "How do transformers differ from RNNs?"

   # Get retrieval results
   results = retriever.retrieve(query, strategy="hybrid", n_results=5)

   # Get graph context
   graph_context = graph_store.get_subgraph(["Transformer", "RNN"], max_depth=2)

   # Generate answer
   answer_data = generator.generate_answer(
       query=query,
       retrieval_results=results,
       graph_context=graph_context
   )

   print(f"Answer:\n{answer_data['answer']}")
   print(f"\nSources: {answer_data['sources']}")
   ```

### Afternoon: Prompt Optimization

1. **Study answer synthesis prompt** ([src/extraction/prompts.py](src/extraction/prompts.py))

2. **Experiment with variations**:
   - Adjust temperature (0.3 vs 0.7 vs 0.9)
   - Modify system prompts
   - Change output format requirements

### Exercise 8: Prompt Engineering Challenge

**Task**: Improve answer quality through prompt engineering

**Test cases**:
1. Factual accuracy (cite sources correctly)
2. Synthesis (combine multiple sources)
3. Relationship awareness (use graph context)
4. Clarity (readable, well-structured)

**Modifications to try**:
1. Add chain-of-thought reasoning
2. Require confidence scores
3. Add answer verification step

### Day 6 Checkpoint
- [ ] Understand answer generation flow
- [ ] Successfully generate contextual answers
- [ ] Experiment with prompt variations
- [ ] Complete Exercise 8

---

## Day 7: UI & Production Polish

**Time**: 3-4 hours

### Morning: Streamlit UI

1. **Study the app** ([app.py](app.py))
   - Component initialization
   - Session state management
   - Query flow
   - Visualization

2. **Customize the UI**:
   ```python
   # Add custom CSS
   # Add new sidebar options
   # Modify visualization
   ```

### Afternoon: End-to-End Testing

1. **Full pipeline test**:
   ```bash
   # Clear existing data
   rm -rf data/chroma_db/*
   # In Neo4j: MATCH (n) DETACH DELETE n

   # Add new documents
   cp your-docs/* data/raw/

   # Ingest
   python scripts/ingest_documents.py

   # Launch
   streamlit run app.py
   ```

2. **Create test queries**:
   - Create 20 test queries
   - Evaluate quality
   - Document edge cases

### Exercise 9: Feature Addition

**Choose one to implement**:

**Option A: Export Conversation**
- Add button to export Q&A history to JSON/Markdown
- Include sources and metadata

**Option B: Document Filtering**
- Add UI controls to filter by document type or date
- Update retrieval to respect filters

**Option C: Feedback System**
- Add thumbs up/down for answers
- Store feedback in database
- Display feedback analytics

### Exercise 10: Performance Optimization

**Task**: Optimize the system for production

**Areas to optimize**:
1. Caching frequent queries
2. Batch processing for ingestion
3. Lazy loading for graph visualization
4. Connection pooling for databases

### Final Project: Domain Customization

**Task**: Customize the system for a specific domain

**Steps**:
1. Choose domain (e.g., medical, legal, technical docs)
2. Add domain-specific entity types
3. Customize prompts with domain examples
4. Test with domain documents
5. Create demo video

### Day 7 Checkpoint
- [ ] Understand full application flow
- [ ] Successfully customize UI
- [ ] Complete one feature addition (Exercise 9)
- [ ] Optimize for production (Exercise 10)

---

## Bonus: Advanced Topics

### Week 2: Advanced Features

1. **Multi-modal RAG**
   - Add image understanding
   - Extract text from images
   - Create visual entity nodes

2. **Agentic Workflows**
   - Multi-step reasoning
   - Tool use (calculators, APIs)
   - Self-reflection and refinement

3. **Fine-tuning**
   - Fine-tune embedding model on your domain
   - Fine-tune LLM for entity extraction
   - Evaluate improvements

4. **Production Deployment**
   - Docker containerization
   - FastAPI backend
   - Authentication & authorization
   - Rate limiting
   - Monitoring & logging

## Learning Resources

**Vector Search**:
- [Pinecone Learn](https://www.pinecone.io/learn/)
- [Weaviate Blog](https://weaviate.io/blog)

**Knowledge Graphs**:
- [Neo4j GraphAcademy](https://graphacademy.neo4j.com/)
- [Knowledge Graphs Book](https://www.manning.com/books/knowledge-graphs)

**RAG Systems**:
- [LangChain Documentation](https://python.langchain.com/docs/)
- [LlamaIndex Guide](https://docs.llamaindex.ai/)

**Prompt Engineering**:
- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Anthropic Prompt Library](https://docs.anthropic.com/claude/prompt-library)

## Project Milestones

- [ ] Day 1: Load and chunk documents
- [ ] Day 2: Extract entities with LLM
- [ ] Day 3: Implement vector search
- [ ] Day 4: Build knowledge graph
- [ ] Day 5: Create hybrid retrieval
- [ ] Day 6: Generate contextual answers
- [ ] Day 7: Polish UI and deploy

## Success Metrics

By the end of the week, you should be able to:
1. Process any collection of documents
2. Build a searchable knowledge graph
3. Answer complex queries using hybrid retrieval
4. Explain the architecture to others
5. Customize the system for different domains

---

**Congratulations on completing the build! You now have a production-ready GraphRAG system! 🎉**
