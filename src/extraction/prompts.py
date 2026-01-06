"""Prompt templates for entity extraction and relationship identification."""

ENTITY_EXTRACTION_PROMPT = """You are an expert at extracting structured information from technical documents.

Your task is to extract entities and their relationships from the given text. Focus on:
- Technical concepts, frameworks, and methodologies
- People (authors, researchers, practitioners)
- Organizations and companies
- Technologies and tools
- Research papers and publications

For each entity, identify:
1. Entity name
2. Entity type (CONCEPT, PERSON, ORGANIZATION, TECHNOLOGY, PUBLICATION)
3. A brief description

Then, identify relationships between entities in the format:
(Entity1) -[RELATIONSHIP_TYPE]-> (Entity2)

Example Input:
"The transformer architecture, introduced by Vaswani et al. in the paper 'Attention is All You Need',
revolutionized natural language processing. Google developed this architecture, which later influenced
models like GPT and BERT."

Example Output:
ENTITIES:
- Name: Transformer Architecture, Type: CONCEPT, Description: A neural network architecture for sequence processing
- Name: Vaswani et al., Type: PERSON, Description: Researchers who introduced the transformer
- Name: Attention is All You Need, Type: PUBLICATION, Description: Seminal paper on transformer architecture
- Name: Natural Language Processing, Type: CONCEPT, Description: Field of AI focused on language understanding
- Name: Google, Type: ORGANIZATION, Description: Technology company that developed the transformer
- Name: GPT, Type: TECHNOLOGY, Description: Generative language model based on transformers
- Name: BERT, Type: TECHNOLOGY, Description: Bidirectional transformer-based model

RELATIONSHIPS:
- (Vaswani et al.) -[AUTHORED]-> (Attention is All You Need)
- (Attention is All You Need) -[INTRODUCES]-> (Transformer Architecture)
- (Google) -[DEVELOPED]-> (Transformer Architecture)
- (Transformer Architecture) -[INFLUENCES]-> (GPT)
- (Transformer Architecture) -[INFLUENCES]-> (BERT)
- (Transformer Architecture) -[USED_IN]-> (Natural Language Processing)

Now extract entities and relationships from this text:

{text}

Provide your answer in the same structured format as the example.
"""

RELATIONSHIP_EXTRACTION_PROMPT = """Given two entities from a technical document, identify the relationship between them.

Entity 1: {entity1}
Entity 1 Type: {entity1_type}

Entity 2: {entity2}
Entity 2 Type: {entity2_type}

Context: {context}

Determine the most appropriate relationship type from this list:
- AUTHORED: Person authored a publication
- DEVELOPED: Organization/person developed a technology
- INTRODUCES: Publication introduces a concept
- USES: Technology uses another technology
- INFLUENCES: One concept influences another
- PART_OF: One concept is part of another
- RELATED_TO: General relationship
- CITES: Publication cites another publication
- WORKS_AT: Person works at organization
- BUILDS_ON: Concept builds on another concept

Provide only the relationship type or "NONE" if no clear relationship exists.

Relationship type:"""

QUERY_UNDERSTANDING_PROMPT = """Analyze the user's query and determine the best retrieval strategy.

User Query: {query}

Classify this query into one of these categories:

1. FACTUAL: Simple fact lookup, can be answered with vector search
   Example: "What is a transformer model?"

2. COMPARATIVE: Comparing multiple concepts, requires multi-hop reasoning
   Example: "How does GPT differ from BERT?"

3. RELATIONAL: Understanding connections between entities, needs graph traversal
   Example: "What papers influenced the development of attention mechanisms?"

4. EXPLORATORY: Broad investigation, needs hybrid approach
   Example: "What are the recent advances in language models?"

5. TREND_ANALYSIS: Identifying patterns over time or across domains
   Example: "How has transfer learning evolved in the last 5 years?"

Provide:
1. Query Category: [FACTUAL/COMPARATIVE/RELATIONAL/EXPLORATORY/TREND_ANALYSIS]
2. Key Entities: List the main entities mentioned
3. Recommended Strategy: [VECTOR_ONLY/GRAPH_ONLY/HYBRID]
4. Reasoning: Brief explanation

Format your response as JSON:
{{
  "category": "...",
  "key_entities": [...],
  "strategy": "...",
  "reasoning": "..."
}}
"""

ANSWER_SYNTHESIS_PROMPT = """You are a research assistant helping technical teams find insights from documentation.

User Query: {query}

Retrieved Context:
{context}

Knowledge Graph Context:
{graph_context}

Based on the retrieved information, provide a comprehensive answer that:
1. Directly addresses the user's question
2. Synthesizes information from both vector search and graph relationships
3. Highlights important connections and relationships
4. Cites sources using [doc_id] format
5. Acknowledges if information is incomplete

Keep the answer concise but thorough. Use technical language appropriate for the audience.

Answer:"""

FEW_SHOT_ENTITY_EXAMPLES = [
    {
        "text": "BERT, developed by Google in 2018, uses bidirectional transformers for pre-training.",
        "entities": [
            {"name": "BERT", "type": "TECHNOLOGY", "description": "Bidirectional Encoder Representations from Transformers"},
            {"name": "Google", "type": "ORGANIZATION", "description": "Technology company"},
            {"name": "Bidirectional Transformers", "type": "CONCEPT", "description": "Transformer architecture that processes text in both directions"}
        ],
        "relationships": [
            {"source": "Google", "target": "BERT", "type": "DEVELOPED"},
            {"source": "BERT", "target": "Bidirectional Transformers", "type": "USES"}
        ]
    },
    {
        "text": "The paper 'Attention is All You Need' by Vaswani et al. revolutionized NLP.",
        "entities": [
            {"name": "Attention is All You Need", "type": "PUBLICATION", "description": "Seminal paper on transformers"},
            {"name": "Vaswani et al.", "type": "PERSON", "description": "Research team at Google"},
            {"name": "NLP", "type": "CONCEPT", "description": "Natural Language Processing field"}
        ],
        "relationships": [
            {"source": "Vaswani et al.", "target": "Attention is All You Need", "type": "AUTHORED"},
            {"source": "Attention is All You Need", "target": "NLP", "type": "INFLUENCES"}
        ]
    }
]
