# GraphRAG Research Assistant - Quick Start (5 Minutes)

Get up and running in 5 minutes with this streamlined guide.

## Prerequisites Checklist

- [ ] Python 3.9+ installed
- [ ] Neo4j account created (free at [neo4j.com/cloud/aura](https://neo4j.com/cloud/aura))
- [ ] OpenAI OR Anthropic API key

## Installation (2 minutes)

```bash
# Navigate to project
cd rag-project

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration (2 minutes)

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

**Required settings in .env:**
```bash
# Choose one LLM provider
OPENAI_API_KEY=sk-your-key-here
# OR
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Neo4j credentials (from Aura dashboard)
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
```

## Test & Run (1 minute)

```bash
# Verify setup
python scripts/test_system.py

# Ingest sample document (or add your own to data/raw/)
python scripts/ingest_documents.py

# Launch app
streamlit run app.py
```

The app opens at `http://localhost:8501` - try asking:
- "What is a transformer model?"
- "How does BERT differ from GPT?"

## What's Next?

1. **Add your documents** to `data/raw/`
2. **Run ingestion** again with your docs
3. **Explore the UI** - try different query types
4. **Read the full guides**:
   - [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed setup instructions
   - [README.md](README.md) - Complete documentation

## Troubleshooting

**Connection failed?**
```bash
python scripts/test_system.py
```
This will identify the issue.

**Need help?** See [SETUP_GUIDE.md](SETUP_GUIDE.md#troubleshooting)

---

**That's it! You're ready to go! 🚀**
