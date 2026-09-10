"""ChromaDB Vector Database Manager"""
import os
import chromadb
from typing import List, Dict, Any, Optional
from config import Config

os.environ["ANONYMIZED_TELEMETRY"] = "False"

_instance = None


def get_vector_db():
    global _instance
    if _instance is None:
        _instance = VectorDB()
    return _instance


class VectorDB:
    def __init__(self):
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        os.makedirs(Config.CHROMA_DB_PATH, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=Config.CHROMA_DB_PATH,
            settings=chromadb.config.Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )
        self.collection = self.client.get_or_create_collection(
            name=Config.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str] = None):
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]

        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
            )
            print(f"✓ Added {len(documents)} documents to vector DB")
        except Exception as e:
            print(f"✗ Error adding documents: {e}")
            raise

    def query(self, query_text: str, top_k: int = None, where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if top_k is None:
            top_k = Config.TOP_K_RESULTS

        try:
            n_results = top_k
            if where:
                matched = self.collection.get(where=where)
                count = len(matched.get("ids") or [])
                if count == 0:
                    return {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]}
                n_results = min(top_k, count)
            kwargs = {
                "query_texts": [query_text],
                "n_results": n_results,
            }
            if where:
                kwargs["where"] = where
            return self.collection.query(**kwargs)
        except Exception as e:
            print(f"✗ Error querying vector DB: {e}")
            raise

    def get_collection_stats(self) -> Dict[str, Any]:
        count = self.collection.count()
        return {
            "total_documents": count,
            "collection_name": Config.CHROMA_COLLECTION_NAME,
            "path": Config.CHROMA_DB_PATH,
        }

    def clear_collection(self):
        self.client.delete_collection(name=Config.CHROMA_COLLECTION_NAME)
        self.collection = self.client.get_or_create_collection(
            name=Config.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        print("✓ Collection cleared")

    def delete_by_source(self, source: str):
        try:
            where = {"source": {"$eq": source}}
            results = self.collection.get(where=where)
            if results["ids"]:
                self.collection.delete(ids=results["ids"])
                print(f"✓ Deleted {len(results['ids'])} documents from {source}")
        except Exception as e:
            print(f"✗ Error deleting documents: {e}")
