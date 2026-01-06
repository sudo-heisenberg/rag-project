"""Text chunking strategies for document processing."""

from typing import List, Dict, Any
from dataclasses import dataclass
import logging

from src.ingestion.document_loader import Document
from src.config import config

logger = logging.getLogger(__name__)

@dataclass
class Chunk:
    """Text chunk data structure."""
    content: str
    metadata: Dict[str, Any]
    chunk_id: str
    doc_id: str

class DocumentChunker:
    """Chunk documents into smaller pieces for processing."""

    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
        chunking_strategy: str = "fixed_size"
    ):
        """
        Initialize document chunker.

        Args:
            chunk_size: Size of each chunk in characters
            chunk_overlap: Overlap between chunks
            chunking_strategy: Strategy to use (fixed_size, semantic, sentence)
        """
        self.chunk_size = chunk_size or config.document_processing.chunk_size
        self.chunk_overlap = chunk_overlap or config.document_processing.chunk_overlap
        self.chunking_strategy = chunking_strategy

    def chunk_document(self, document: Document) -> List[Chunk]:
        """
        Chunk a document into smaller pieces.

        Args:
            document: Document to chunk

        Returns:
            List of Chunk objects
        """
        logger.info(f"Chunking document: {document.doc_id}")

        if self.chunking_strategy == "fixed_size":
            chunks = self._fixed_size_chunking(document)
        elif self.chunking_strategy == "semantic":
            # TODO: Implement semantic chunking
            chunks = self._fixed_size_chunking(document)
        elif self.chunking_strategy == "sentence":
            # TODO: Implement sentence-based chunking
            chunks = self._fixed_size_chunking(document)
        else:
            raise ValueError(f"Unknown chunking strategy: {self.chunking_strategy}")

        logger.info(f"Created {len(chunks)} chunks from document {document.doc_id}")
        return chunks

    def chunk_documents(self, documents: List[Document]) -> List[Chunk]:
        """
        Chunk multiple documents.

        Args:
            documents: List of documents to chunk

        Returns:
            List of all chunks
        """
        all_chunks = []
        for doc in documents:
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)

        logger.info(f"Total chunks created: {len(all_chunks)}")
        return all_chunks

    def _fixed_size_chunking(self, document: Document) -> List[Chunk]:
        """
        Chunk document using fixed-size strategy with overlap.

        Args:
            document: Document to chunk

        Returns:
            List of chunks
        """
        text = document.content
        chunks = []
        start = 0
        chunk_index = 0

        while start < len(text):
            end = start + self.chunk_size

            # Extract chunk
            chunk_text = text[start:end]

            # Create chunk metadata
            chunk_metadata = {
                **document.metadata,
                "chunk_index": chunk_index,
                "start_char": start,
                "end_char": end,
            }

            # Create chunk ID
            chunk_id = f"{document.doc_id}_chunk_{chunk_index}"

            # Create chunk object
            chunk = Chunk(
                content=chunk_text,
                metadata=chunk_metadata,
                chunk_id=chunk_id,
                doc_id=document.doc_id
            )

            chunks.append(chunk)

            # Move to next chunk with overlap
            start += self.chunk_size - self.chunk_overlap
            chunk_index += 1

        return chunks

# Example usage
if __name__ == "__main__":
    from src.ingestion.document_loader import DocumentLoader
    from pathlib import Path

    # Load and chunk documents
    # loader = DocumentLoader()
    # docs = loader.load_directory(Path("data/raw"))
    #
    # chunker = DocumentChunker(chunk_size=500, chunk_overlap=50)
    # chunks = chunker.chunk_documents(docs)
    #
    # print(f"Total chunks: {len(chunks)}")
    # print(f"First chunk: {chunks[0].content[:100]}...")
