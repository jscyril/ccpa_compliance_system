"""
Vector Store

ChromaDB-based in-memory vector store for semantic search over CCPA
subsections. Uses bge-small-en-v1.5 for embeddings (loaded on CPU
to preserve GPU VRAM for the LLM).

Supports parent-document retrieval: search by subsection (child),
then retrieve full section (parent) via ccpa_knowledge.
"""

import logging
from typing import Optional

import chromadb
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
COLLECTION_NAME = "ccpa_subsections"


class VectorStore:
    """In-memory vector store for CCPA subsection retrieval."""

    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self._model_name = model_name
        self._embedding_model: Optional[SentenceTransformer] = None
        self._client = chromadb.Client()  # In-memory, no persistence
        self._collection = None
        self._built = False

    @property
    def is_ready(self) -> bool:
        """Check if the index has been built and is ready for search."""
        return self._built and self._collection is not None

    def _load_embedding_model(self) -> None:
        """Load the embedding model on CPU."""
        if self._embedding_model is None:
            logger.info(f"Loading embedding model: {self._model_name}")
            self._embedding_model = SentenceTransformer(
                self._model_name, device="cpu"
            )
            logger.info("Embedding model loaded on CPU")

    def build_index(self, subsections: list[dict]) -> None:
        """
        Build the vector index from CCPA subsections.

        Args:
            subsections: Output of ccpa_kb.get_all_subsections().
                Each dict has: id, text, parent_section_id
        """
        self._load_embedding_model()

        logger.info(f"Building index with {len(subsections)} subsections")

        # Create or reset collection
        try:
            self._client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
        self._collection = self._client.create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

        if not subsections:
            logger.warning("No subsections to index")
            self._built = True
            return

        # Prepare documents for embedding
        texts = [sub["text"] for sub in subsections]
        ids = [sub["id"] for sub in subsections]
        metadatas = [
            {"parent_section_id": sub["parent_section_id"]}
            for sub in subsections
        ]

        # Embed all texts in batch
        logger.info("Embedding subsections...")
        embeddings = self._embedding_model.encode(
            texts,
            show_progress_bar=True,
            batch_size=32,
            normalize_embeddings=True,
        ).tolist()

        # Add to ChromaDB
        self._collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )

        self._built = True
        logger.info(
            f"Index built: {self._collection.count()} documents indexed"
        )

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Search for relevant CCPA subsections by semantic similarity.

        Args:
            query: Natural language query describing a business practice.
            top_k: Number of results to return.

        Returns:
            List of dicts with: id, text, parent_section_id, distance
        """
        if not self.is_ready:
            raise RuntimeError("Index not built. Call build_index() first.")

        self._load_embedding_model()

        # Embed query
        query_embedding = self._embedding_model.encode(
            [query],
            normalize_embeddings=True,
        ).tolist()

        # Query ChromaDB
        results = self._collection.query(
            query_embeddings=query_embedding,
            n_results=min(top_k, self._collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        # Format results
        formatted = []
        for i in range(len(results["ids"][0])):
            formatted.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "parent_section_id": results["metadatas"][0][i][
                    "parent_section_id"
                ],
                "distance": results["distances"][0][i],
            })

        return formatted


# Module-level singleton
vector_store = VectorStore()
