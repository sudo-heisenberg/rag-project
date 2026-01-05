# GraphRAG Research Assistant - Complete Setup Guide

This guide will walk you through setting up the GraphRAG Research Assistant from scratch.

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation Steps](#installation-steps)
3. [Neo4j Setup](#neo4j-setup)
4. [API Keys Setup](#api-keys-setup)
5. [Testing Your Setup](#testing-your-setup)
6. [Adding Documents](#adding-documents)
7. [Running the Application](#running-the-application)
8. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements
- Python 3.9 or higher
- 4GB RAM
- 2GB free disk space
- Internet connection for API calls

### Recommended
- Python 3.10+
- 8GB+ RAM
- 5GB+ free disk space
- Dedicated GPU (optional, for faster embedding generation)

## Installation Steps

### Step 1: Install Python

**macOS:**
```bash
# Using Homebrew
brew install python@3.11

# Verify installation
python3 --version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# Verify installation
python3 --version
```

**Windows:**
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run installer (check "Add Python to PATH")
3. Verify: Open Command Prompt and run `python --version`

### Step 2: Clone or Navigate to Project

```bash
cd rag-project
```

### Step 3: Create Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### Step 4: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will take 5-10 minutes depending on your internet connection.

**If you encounter issues**, try installing in parts:
```bash
# Core dependencies first
pip install streamlit langchain langchain-openai langchain-anthropic

# Vector store
pip install chromadb sentence-transformers

# Graph database
pip install neo4j

# Document processing
pip install pypdf python-docx beautifulsoup4 markdown

# Utilities
pip install python-dotenv pydantic tenacity tqdm pandas numpy plotly pyvis
```

## Neo4j Setup

You have two options: Cloud (easier) or Local.

### Option A: Neo4j Aura Cloud (Recommended for Beginners)

1. **Create Account**
   - Go to [neo4j.com/cloud/aura](https://neo4j.com/cloud/aura/)
   - Click "Start Free"
   - Sign up with email or Google

2. **Create Database Instance**
   - Click "Create Instance"
   - Select "Free" tier
   - Choose a name (e.g., "graphrag-db")
   - Click "Create"

3. **Save Credentials**
   - Download the credentials text file (important!)
   - You'll see:
     - URI: `neo4j+s://xxxxx.databases.neo4j.io`
     - Username: `neo4j`
     - Password: `xxxxx`

4. **Configure .env**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and update:
   ```
   NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=your-password-here
   ```

### Option B: Local Neo4j with Docker

1. **Install Docker**
   - macOS: [Docker Desktop](https://www.docker.com/products/docker-desktop)
   - Linux: `sudo apt install docker.io`
   - Windows: [Docker Desktop](https://www.docker.com/products/docker-desktop)

2. **Run Neo4j Container**
   ```bash
   docker run -d \
     --name neo4j-graphrag \
     -p 7474:7474 -p 7687:7687 \
     -e NEO4J_AUTH=neo4j/password123 \
     -v $HOME/neo4j/data:/data \
     neo4j:latest
   ```

3. **Verify Installation**
   - Open browser: `http://localhost:7474`
   - Login with username: `neo4j`, password: `password123`
   - You should see the Neo4j Browser interface

4. **Configure .env**
   ```bash
   cp .env.example .env
   ```

   Edit `.env`:
   ```
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=password123
   ```

## API Keys Setup

You need at least ONE LLM provider (OpenAI or Anthropic).

### Option A: OpenAI (GPT)

1. **Get API Key**
   - Go to [platform.openai.com](https://platform.openai.com)
   - Sign up / Log in
   - Click "API Keys" in left sidebar
   - Click "Create new secret key"
   - Copy the key (starts with `sk-...`)

2. **Add to .env**
   ```
   OPENAI_API_KEY=sk-your-key-here
   LLM_MODEL=gpt-4-turbo-preview
   ```

   **Models available:**
   - `gpt-4-turbo-preview` - Best quality (recommended)
   - `gpt-3.5-turbo` - Faster and cheaper
   - `gpt-4` - High quality but slower

3. **Set up Billing**
   - Go to Settings > Billing
   - Add payment method
   - Set spending limit (recommended: $10-20 for testing)

### Option B: Anthropic (Claude)

1. **Get API Key**
   - Go to [console.anthropic.com](https://console.anthropic.com)
   - Sign up / Log in
   - Go to "API Keys"
   - Create new key
   - Copy the key (starts with `sk-ant-...`)

2. **Add to .env**
   ```
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   LLM_MODEL=claude-3-opus-20240229
   ```

   **Models available:**
   - `claude-3-opus-20240229` - Best quality
   - `claude-3-sonnet-20240229` - Balanced
   - `claude-3-haiku-20240307` - Fastest and cheapest

### Final .env Configuration

Your `.env` file should look like this:

```bash
# LLM API Keys (choose one or both)
OPENAI_API_KEY=sk-your-key-here
# ANTHROPIC_API_KEY=sk-ant-your-key-here

# Neo4j Configuration
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password-here

# Model Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=gpt-4-turbo-preview

# Vector Store Configuration
CHROMA_PERSIST_DIRECTORY=./data/chroma_db

# Application Settings
MAX_TOKENS=4000
TEMPERATURE=0.7
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

## Testing Your Setup

Run the test script to verify everything is configured correctly:

```bash
python scripts/test_system.py
```

**Expected output:**
```
Testing imports...
✓ Streamlit
✓ LangChain
✓ ChromaDB
✓ Neo4j
✓ Sentence Transformers

Testing configuration...
✓ OpenAI API key configured
✓ Neo4j configured

Testing vector store...
✓ Vector store initialized

Testing Neo4j connection...
✓ Connected to Neo4j

🎉 All tests passed! Your system is ready to use.
```

**If tests fail**, see [Troubleshooting](#troubleshooting) section.

## Adding Documents

### Supported Formats
- PDF (`.pdf`)
- Word (`.docx`)
- Markdown (`.md`)
- Plain text (`.txt`)

### Adding Your Documents

1. **Place files in data/raw/**
   ```bash
   cp ~/Documents/my-research-papers/*.pdf data/raw/
   cp ~/Documents/technical-docs/*.md data/raw/
   ```

2. **Or use the sample document**
   We've included a sample document about transformers:
   ```bash
   ls data/raw/sample_document.txt
   ```

### Document Recommendations

**For best results:**
- Use documents with clear structure (headings, paragraphs)
- 10-100 documents is a good starting size
- Each document should be 500-50,000 words
- Technical documentation works best (research papers, technical guides, documentation)

**Example use cases:**
- Company internal documentation
- Research paper collections
- Product documentation
- Technical blog posts
- Course materials

## Running the Application

### Step 1: Ingest Documents

Run the ingestion pipeline to process your documents:

```bash
python scripts/ingest_documents.py
```

**What happens during ingestion:**
1. Documents are loaded and parsed
2. Text is chunked into smaller pieces
3. Embeddings are generated and stored in ChromaDB
4. LLM extracts entities and relationships
5. Knowledge graph is built in Neo4j

**This will take:**
- Small collection (5-10 docs): 5-15 minutes
- Medium collection (20-50 docs): 30-60 minutes
- Large collection (100+ docs): 2-4 hours

**Cost estimate:**
- Using GPT-4: ~$0.10-0.50 per 10 documents
- Using GPT-3.5: ~$0.02-0.10 per 10 documents
- Using Claude: ~$0.15-0.40 per 10 documents

### Step 2: Launch the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Step 3: Try Some Queries

**Example queries to try:**

1. **Factual Query:**
   ```
   What is a transformer model?
   ```

2. **Comparative Query:**
   ```
   How does BERT differ from GPT?
   ```

3. **Relational Query:**
   ```
   What technologies influenced the development of attention mechanisms?
   ```

4. **Exploratory Query:**
   ```
   What are the key innovations in modern language models?
   ```

## Troubleshooting

### Issue: "Module not found" errors

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Reinstall requirements
pip install -r requirements.txt
```

### Issue: "Neo4j connection failed"

**Symptoms:**
```
Failed to connect to Neo4j
```

**Solutions:**

1. **Verify Neo4j is running:**
   ```bash
   # For Docker
   docker ps | grep neo4j

   # If not running
   docker start neo4j-graphrag
   ```

2. **Test connection manually:**
   - Open `http://localhost:7474` (local) or your Aura URL
   - Try logging in with your credentials

3. **Check .env credentials:**
   - Ensure no extra spaces
   - Password should not be in quotes
   - URI should match your Neo4j instance

### Issue: "Invalid API key"

**Solution:**
1. Verify key in `.env` file
2. Check that key is active on provider website
3. Ensure billing is set up (for OpenAI)
4. No extra spaces or quotes around the key

### Issue: "Out of memory" during ingestion

**Solution:**
```bash
# Process fewer documents at a time
# Edit scripts/ingest_documents.py line 54:
batch_size = 5  # Reduce from 10 to 5

# OR use a smaller embedding model
# Edit .env:
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Issue: ChromaDB permission errors

**Solution:**
```bash
# Create directory with correct permissions
mkdir -p data/chroma_db
chmod 755 data/chroma_db

# On Windows
mkdir data\chroma_db
```

### Issue: Streamlit won't start

**Solution:**
```bash
# Check if port 8501 is in use
# macOS/Linux:
lsof -i :8501

# Kill process if needed
kill -9 <PID>

# Windows:
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Try different port
streamlit run app.py --server.port 8502
```

### Issue: LLM API rate limits

**Symptoms:**
```
Rate limit exceeded
```

**Solution:**
1. Add delays between API calls (already implemented in code)
2. Upgrade your API plan
3. Process documents in smaller batches
4. Use a faster/cheaper model (gpt-3.5-turbo)

### Issue: Poor quality responses

**Solutions:**

1. **Adjust chunk size:**
   ```bash
   # Edit .env
   CHUNK_SIZE=1500  # Increase for more context
   CHUNK_OVERLAP=300  # Increase overlap
   ```

2. **Use better model:**
   ```bash
   # Edit .env
   LLM_MODEL=gpt-4-turbo-preview  # or claude-3-opus-20240229
   ```

3. **Improve prompts:**
   - Edit `src/extraction/prompts.py`
   - Add domain-specific examples
   - Customize entity types

## Next Steps

Once your system is running:

1. **Experiment with queries** - Try different question types
2. **Monitor usage** - Check API costs on provider dashboards
3. **Customize prompts** - Tailor entity extraction for your domain
4. **Add more documents** - The system improves with more data
5. **Explore the graph** - Use Neo4j Browser to visualize relationships

## Getting Help

1. **Check logs:** Look at `graphrag.log` for detailed error messages
2. **Run tests:** `python scripts/test_system.py`
3. **Review README:** See main README.md for architecture details
4. **Debug mode:** Set `logging.basicConfig(level=logging.DEBUG)` in scripts

## Useful Commands Reference

```bash
# Activate environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Test system
python scripts/test_system.py

# Ingest documents
python scripts/ingest_documents.py

# Run app
streamlit run app.py

# Check Neo4j (Docker)
docker ps
docker logs neo4j-graphrag
docker exec -it neo4j-graphrag cypher-shell -u neo4j -p password123

# Clear data and restart
rm -rf data/chroma_db/*
# Then in Neo4j Browser: MATCH (n) DETACH DELETE n
```

---

**You're all set! Happy researching! 🚀**
