"""Streamlit application for GraphRAG Research Assistant."""

import streamlit as st
import plotly.graph_objects as go
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.vector.vector_store import VectorStore
from src.graph.graph_store import GraphStore
from src.retrieval.hybrid_retriever import HybridRetriever
from src.llm.query_router import QueryRouter
from src.llm.answer_generator import AnswerGenerator
from src.config import config

# Page configuration
st.set_page_config(
    page_title="GraphRAG Research Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .source-box {
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 10px;
        margin: 5px 0;
    }
    .metric-card {
        background-color: #e8f4f8;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.vector_store = None
    st.session_state.graph_store = None
    st.session_state.retriever = None
    st.session_state.query_router = None
    st.session_state.answer_generator = None
    st.session_state.query_history = []

def initialize_system():
    """Initialize the GraphRAG system."""
    try:
        with st.spinner("Initializing GraphRAG system..."):
            # Initialize components
            st.session_state.vector_store = VectorStore()
            st.session_state.graph_store = GraphStore()
            st.session_state.retriever = HybridRetriever(
                st.session_state.vector_store,
                st.session_state.graph_store
            )
            st.session_state.query_router = QueryRouter()
            st.session_state.answer_generator = AnswerGenerator()
            st.session_state.initialized = True
        return True
    except Exception as e:
        st.error(f"Error initializing system: {str(e)}")
        st.info("Please check your configuration in .env file")
        return False

def visualize_graph(graph_context):
    """Visualize knowledge graph using Plotly."""
    if not graph_context or not graph_context.get('nodes'):
        return None

    # Create network graph
    nodes = graph_context['nodes']
    edges = graph_context['edges']

    # Create node trace
    node_x = []
    node_y = []
    node_text = []

    # Simple circular layout
    import math
    n = len(nodes)
    for i, node in enumerate(nodes):
        angle = 2 * math.pi * i / n
        node_x.append(math.cos(angle))
        node_y.append(math.sin(angle))
        node_text.append(f"{node['name']}<br>({node['type']})")

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="top center",
        marker=dict(size=20, color='lightblue', line=dict(width=2, color='darkblue')),
        hoverinfo='text'
    )

    # Create edge traces
    edge_traces = []
    for edge in edges:
        # Find source and target positions
        source_idx = next((i for i, n in enumerate(nodes) if n['name'] == edge['source']), None)
        target_idx = next((i for i, n in enumerate(nodes) if n['name'] == edge['target']), None)

        if source_idx is not None and target_idx is not None:
            edge_trace = go.Scatter(
                x=[node_x[source_idx], node_x[target_idx]],
                y=[node_y[source_idx], node_y[target_idx]],
                mode='lines',
                line=dict(width=1, color='gray'),
                hoverinfo='none'
            )
            edge_traces.append(edge_trace)

    # Create figure
    fig = go.Figure(data=edge_traces + [node_trace])
    fig.update_layout(
        title="Knowledge Graph Context",
        showlegend=False,
        hovermode='closest',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=400
    )

    return fig

def main():
    """Main application."""
    # Header
    st.markdown('<div class="main-header">🔍 GraphRAG Research Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Intelligent research tool combining vector search and knowledge graphs</div>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        # Initialize button
        if not st.session_state.initialized:
            if st.button("Initialize System", type="primary"):
                initialize_system()

        if st.session_state.initialized:
            st.success("✅ System Ready")

            # Retrieval strategy
            strategy = st.selectbox(
                "Retrieval Strategy",
                ["auto", "hybrid", "vector", "graph"],
                help="Auto: Let the system decide based on query analysis"
            )

            # Number of results
            n_results = st.slider("Number of Results", 3, 15, 5)

            # Advanced settings
            with st.expander("Advanced Settings"):
                graph_depth = st.slider("Graph Traversal Depth", 1, 4, 2)
                show_graph = st.checkbox("Show Knowledge Graph", value=True)
                show_analysis = st.checkbox("Show Query Analysis", value=True)

            st.divider()

            # System stats
            if st.button("Show System Stats"):
                try:
                    vector_stats = st.session_state.vector_store.get_collection_stats()
                    graph_stats = st.session_state.graph_store.get_graph_stats()

                    st.metric("Documents", vector_stats['total_chunks'])
                    st.metric("Entities", graph_stats['total_entities'])
                    st.metric("Relationships", graph_stats['total_relationships'])
                except Exception as e:
                    st.error(f"Error fetching stats: {str(e)}")

    # Main content
    if st.session_state.initialized:
        # Query input
        query = st.text_input(
            "Enter your research question:",
            placeholder="e.g., How do transformers differ from RNNs?",
            key="query_input"
        )

        if st.button("Search", type="primary") and query:
            with st.spinner("Analyzing query and retrieving information..."):
                try:
                    # Route query
                    routing_info = st.session_state.query_router.route_query(query)
                    analysis = routing_info['analysis']

                    # Override strategy if not auto
                    if strategy != "auto":
                        routing_info['retrieval_params']['strategy'] = strategy
                    else:
                        routing_info['retrieval_params']['strategy'] = analysis.strategy.lower()

                    # Show query analysis
                    if show_analysis:
                        with st.expander("📊 Query Analysis", expanded=True):
                            col1, col2, col3 = st.columns(3)
                            col1.metric("Category", analysis.category)
                            col2.metric("Strategy", analysis.strategy)
                            col3.metric("Entities Found", len(analysis.key_entities))

                            if analysis.key_entities:
                                st.write("**Key Entities:**", ", ".join(analysis.key_entities))
                            st.write("**Reasoning:**", analysis.reasoning)

                    # Retrieve
                    results = st.session_state.retriever.retrieve(
                        query=query,
                        **routing_info['retrieval_params']
                    )

                    # Get graph context if entities found
                    graph_context = None
                    if analysis.key_entities and show_graph:
                        graph_context = st.session_state.graph_store.get_subgraph(
                            entity_names=analysis.key_entities[:5],
                            max_depth=graph_depth
                        )

                    # Generate answer
                    answer_data = st.session_state.answer_generator.generate_answer(
                        query=query,
                        retrieval_results=results,
                        graph_context=graph_context
                    )

                    # Display answer
                    st.divider()
                    st.subheader("💡 Answer")
                    st.markdown(answer_data['answer'])

                    # Display sources
                    st.divider()
                    st.subheader("📚 Sources")
                    for i, result in enumerate(results, 1):
                        with st.expander(f"Source {i}: {result.source} (Relevance: {result.relevance_score:.2%})"):
                            st.markdown(f"**Method:** {result.retrieval_method}")
                            st.markdown(result.content)

                    # Display graph visualization
                    if show_graph and graph_context and graph_context.get('nodes'):
                        st.divider()
                        st.subheader("🕸️ Knowledge Graph")
                        fig = visualize_graph(graph_context)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)

                    # Add to history
                    st.session_state.query_history.append({
                        'query': query,
                        'category': analysis.category,
                        'strategy': routing_info['retrieval_params']['strategy']
                    })

                except Exception as e:
                    st.error(f"Error processing query: {str(e)}")
                    st.exception(e)

        # Query history
        if st.session_state.query_history:
            st.divider()
            with st.expander("📜 Query History"):
                for i, item in enumerate(reversed(st.session_state.query_history[-10:]), 1):
                    st.write(f"{i}. **{item['query']}** - {item['category']} ({item['strategy']})")

    else:
        # Welcome screen
        st.info("👈 Click 'Initialize System' in the sidebar to get started")

        # Feature showcase
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### 🎯 Smart Routing")
            st.write("Automatically determines the best retrieval strategy based on your query type")

        with col2:
            st.markdown("### 🔗 Knowledge Graph")
            st.write("Discovers relationships and connections between concepts")

        with col3:
            st.markdown("### 🚀 Hybrid Search")
            st.write("Combines vector similarity and graph traversal for better results")

if __name__ == "__main__":
    main()
