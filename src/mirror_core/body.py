"""Body layer: vector store for knowledge retrieval (RAG)."""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import chromadb

from mirror_core.models import Memory


class BodyManager:
    """Manages the Chroma vector store for knowledge chunks."""

    def __init__(self, data_dir: Path, collection_name: str = "mirror_core"):
        self.data_dir = data_dir
        db_path = str(data_dir / "body" / "chroma_db")
        self._client = chromadb.PersistentClient(path=db_path)
        self.collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def ingest(
        self,
        content: str,
        type: str,
        domain: str,
        tags: list[str],
        confidence: float,
        source: str,
        version: str,
    ) -> str:
        """Ingest a single knowledge chunk. Returns the chunk ID."""
        doc_id = str(uuid.uuid4())
        self.collection.add(
            ids=[doc_id],
            documents=[content],
            metadatas=[
                {
                    "type": type,
                    "domain": domain,
                    "tags": ",".join(tags),
                    "confidence": confidence,
                    "source": source,
                    "version": version,
                    "timestamp": datetime.now().isoformat(),
                }
            ],
        )
        return doc_id

    def ingest_batch(self, items: list[dict]) -> list[str]:
        """Ingest multiple knowledge chunks at once."""
        ids = [str(uuid.uuid4()) for _ in items]
        documents = [item["content"] for item in items]
        metadatas = [
            {
                "type": item["type"],
                "domain": item["domain"],
                "tags": ",".join(item["tags"]),
                "confidence": item["confidence"],
                "source": item["source"],
                "version": item["version"],
                "timestamp": datetime.now().isoformat(),
            }
            for item in items
        ]
        self.collection.add(ids=ids, documents=documents, metadatas=metadatas)
        return ids

    def search(
        self,
        query: str,
        top_k: int = 5,
        domain: Optional[str] = None,
    ) -> list[Memory]:
        """Search for relevant knowledge chunks."""
        if self.collection.count() == 0:
            return []

        where = {"domain": domain} if domain else None
        actual_k = min(top_k, self.collection.count())

        results = self.collection.query(
            query_texts=[query],
            n_results=actual_k,
            where=where,
        )

        memories = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i]
                try:
                    ts = datetime.fromisoformat(meta.get("timestamp", ""))
                except (ValueError, TypeError):
                    ts = datetime.now()

                memories.append(
                    Memory(
                        content=doc,
                        type=meta.get("type", ""),
                        domain=meta.get("domain", ""),
                        timestamp=ts,
                        version=meta.get("version", ""),
                        tags=meta.get("tags", "").split(",") if meta.get("tags") else [],
                        confidence=float(meta.get("confidence", 0.5)),
                        source=meta.get("source", ""),
                    )
                )
        return memories
