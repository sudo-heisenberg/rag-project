.PHONY: help install test ingest run clean setup

help:
	@echo "GraphRAG Research Assistant - Available Commands"
	@echo ""
	@echo "  make setup      - Complete first-time setup"
	@echo "  make install    - Install Python dependencies"
	@echo "  make test       - Run system tests"
	@echo "  make ingest     - Ingest documents from data/raw/"
	@echo "  make run        - Launch Streamlit application"
	@echo "  make clean      - Clear all data (vector DB and graph)"
	@echo "  make help       - Show this help message"
	@echo ""

setup:
	@echo "Setting up GraphRAG system..."
	@echo "Step 1: Creating virtual environment..."
	python3 -m venv venv
	@echo "Step 2: Installing dependencies..."
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	@echo "Step 3: Creating .env file..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo ".env file created. Please edit it with your API keys."; \
	else \
		echo ".env file already exists."; \
	fi
	@echo "Step 4: Creating data directories..."
	@mkdir -p data/raw data/processed data/chroma_db
	@echo ""
	@echo "✅ Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Edit .env with your API keys and Neo4j credentials"
	@echo "  2. Add documents to data/raw/"
	@echo "  3. Run: make test"
	@echo "  4. Run: make ingest"
	@echo "  5. Run: make run"

install:
	@echo "Installing dependencies..."
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	@echo "✅ Installation complete!"

test:
	@echo "Running system tests..."
	./venv/bin/python scripts/test_system.py

ingest:
	@echo "Ingesting documents..."
	@echo "This may take several minutes depending on document count."
	./venv/bin/python scripts/ingest_documents.py

run:
	@echo "Launching Streamlit application..."
	./venv/bin/streamlit run app.py

clean:
	@echo "⚠️  WARNING: This will delete all data!"
	@echo "Press Ctrl+C to cancel, or Enter to continue..."
	@read dummy
	@echo "Cleaning vector database..."
	rm -rf data/chroma_db/*
	@echo "⚠️  Remember to also clear Neo4j database:"
	@echo "    Run in Neo4j Browser: MATCH (n) DETACH DELETE n"
	@echo "✅ Cleanup complete!"
