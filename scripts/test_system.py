"""Test script to verify system setup."""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

def test_imports():
    """Test if all required packages can be imported."""
    print("Testing imports...")
    try:
        import streamlit
        print("✓ Streamlit")
        import langchain
        print("✓ LangChain")
        import chromadb
        print("✓ ChromaDB")
        import neo4j
        print("✓ Neo4j")
        import sentence_transformers
        print("✓ Sentence Transformers")
        print("\n✓ All packages imported successfully!")
        return True
    except ImportError as e:
        print(f"\n✗ Import error: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def test_configuration():
    """Test configuration setup."""
    print("\nTesting configuration...")
    try:
        from src.config import config

        # Check API keys
        has_openai = bool(config.llm.openai_api_key and config.llm.openai_api_key != "your_openai_api_key_here")
        has_anthropic = bool(config.llm.anthropic_api_key and config.llm.anthropic_api_key != "your_anthropic_api_key_here")

        if has_openai:
            print("✓ OpenAI API key configured")
        if has_anthropic:
            print("✓ Anthropic API key configured")

        if not (has_openai or has_anthropic):
            print("⚠ No LLM API key configured. Add to .env file")
            return False

        # Check Neo4j
        if config.graph_db.uri and config.graph_db.password != "your_password_here":
            print("✓ Neo4j configured")
        else:
            print("⚠ Neo4j not configured. Update .env file")
            return False

        print("\n✓ Configuration looks good!")
        return True

    except Exception as e:
        print(f"\n✗ Configuration error: {e}")
        return False

def test_neo4j_connection():
    """Test Neo4j database connection."""
    print("\nTesting Neo4j connection...")
    try:
        from src.graph.graph_store import GraphStore

        graph_store = GraphStore()
        stats = graph_store.get_graph_stats()
        print(f"✓ Connected to Neo4j")
        print(f"  Entities: {stats['total_entities']}")
        print(f"  Relationships: {stats['total_relationships']}")
        graph_store.close()
        return True

    except Exception as e:
        print(f"✗ Neo4j connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check if Neo4j is running")
        print("2. Verify credentials in .env file")
        print("3. Test connection at http://localhost:7474 (if using local)")
        return False

def test_vector_store():
    """Test vector store."""
    print("\nTesting vector store...")
    try:
        from src.vector.vector_store import VectorStore

        vector_store = VectorStore()
        stats = vector_store.get_collection_stats()
        print(f"✓ Vector store initialized")
        print(f"  Total chunks: {stats['total_chunks']}")
        print(f"  Embedding model: {stats['embedding_model']}")
        return True

    except Exception as e:
        print(f"✗ Vector store error: {e}")
        return False

def test_directories():
    """Test required directories exist."""
    print("\nChecking directories...")
    dirs = [
        Path("data/raw"),
        Path("data/processed"),
        Path("data/chroma_db"),
    ]

    all_exist = True
    for dir_path in dirs:
        if dir_path.exists():
            print(f"✓ {dir_path}")
        else:
            print(f"✗ {dir_path} (will be created)")
            dir_path.mkdir(parents=True, exist_ok=True)
            all_exist = False

    return True

def main():
    """Run all tests."""
    print("="*60)
    print("GraphRAG System Test")
    print("="*60)

    tests = [
        ("Package Imports", test_imports),
        ("Directories", test_directories),
        ("Configuration", test_configuration),
        ("Vector Store", test_vector_store),
        ("Neo4j Connection", test_neo4j_connection),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ {name} failed with error: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n🎉 All tests passed! Your system is ready to use.")
        print("\nNext steps:")
        print("1. Add documents to data/raw/")
        print("2. Run: python scripts/ingest_documents.py")
        print("3. Launch app: streamlit run app.py")
    else:
        print("\n⚠ Some tests failed. Please fix the issues above.")

if __name__ == "__main__":
    main()
