"""RAG Retrieval System"""
from typing import List, Dict, Any
from src.vector_db import get_vector_db
from config import Config


class RAGRetriever:
    def __init__(self):
        self.vector_db = get_vector_db()

    def retrieve_context(self, query: str, top_k: int = None, subject_filter: str = None) -> Dict[str, Any]:
        if top_k is None:
            top_k = Config.TOP_K_RESULTS

        try:
            where = {"subject": {"$eq": subject_filter}} if subject_filter else None
            results = self.vector_db.query(query, top_k=top_k, where=where)

            retrieved_docs = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                    distance = results["distances"][0][i] if results["distances"] else 0
                    retrieved_docs.append({
                        "content": doc,
                        "metadata": metadata,
                        "similarity_score": 1 - distance,
                        "source": metadata.get("source", "Unknown"),
                        "chapter": metadata.get("chapter", "Unknown"),
                    })

            return {
                "query": query,
                "retrieved_documents": retrieved_docs,
                "total_retrieved": len(retrieved_docs),
                "context": self._format_context(retrieved_docs),
            }
        except Exception as e:
            print(f"✗ Error retrieving context: {e}")
            return {
                "query": query,
                "retrieved_documents": [],
                "total_retrieved": 0,
                "context": "",
                "error": str(e),
            }

    def retrieve_by_chapter(self, chapter: str, subject: str = None) -> Dict[str, Any]:
        try:
            where_clause = {
                "$and": [
                    {"chapter": {"$eq": chapter}},
                    {"subject": {"$eq": subject}},
                ]
            } if subject else {"chapter": {"$eq": chapter}}

            results = self.vector_db.collection.get(where=where_clause)

            docs = []
            if results["documents"]:
                for i, doc in enumerate(results["documents"]):
                    docs.append({
                        "content": doc,
                        "metadata": results["metadatas"][i] if results["metadatas"] else {},
                    })

            return {
                "chapter": chapter,
                "subject": subject,
                "documents": docs,
                "total_documents": len(docs),
                "context": self._format_context(docs),
            }
        except Exception as e:
            print(f"✗ Error retrieving by chapter: {e}")
            return {
                "chapter": chapter,
                "documents": [],
                "total_documents": 0,
                "context": "",
                "error": str(e),
            }

    def retrieve_in_chapter(
        self, query: str, chapter: str, subject: str, top_k: int = None
    ) -> Dict[str, Any]:
        if top_k is None:
            top_k = Config.TOP_K_RESULTS
        try:
            where = {
                "$and": [
                    {"chapter": {"$eq": chapter}},
                    {"subject": {"$eq": subject}},
                ]
            }
            results = self.vector_db.query(query, top_k=top_k, where=where)
            retrieved_docs = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                    distance = results["distances"][0][i] if results["distances"] else 0
                    retrieved_docs.append({
                        "content": doc,
                        "metadata": metadata,
                        "similarity_score": 1 - distance,
                        "source": metadata.get("source", "Unknown"),
                        "chapter": metadata.get("chapter", "Unknown"),
                    })
            return {
                "query": query,
                "retrieved_documents": retrieved_docs,
                "total_retrieved": len(retrieved_docs),
                "context": self._format_context(retrieved_docs),
            }
        except Exception as e:
            print(f"✗ Error retrieving in chapter: {e}")
            return {
                "query": query,
                "retrieved_documents": [],
                "total_retrieved": 0,
                "context": "",
                "error": str(e),
            }

    def retrieve_by_subject(self, subject: str) -> Dict[str, Any]:
        try:
            results = self.vector_db.collection.get(
                where={"subject": {"$eq": subject}}
            )
            docs = []
            if results["documents"]:
                for i, doc in enumerate(results["documents"]):
                    docs.append({
                        "content": doc,
                        "metadata": results["metadatas"][i] if results["metadatas"] else {},
                    })
            return {
                "subject": subject,
                "documents": docs,
                "total_documents": len(docs),
                "context": self._format_context(docs),
            }
        except Exception as e:
            print(f"✗ Error retrieving by subject: {e}")
            return {
                "subject": subject,
                "documents": [],
                "total_documents": 0,
                "context": "",
                "error": str(e),
            }

    @staticmethod
    def _format_context(documents: List[Dict[str, Any]]) -> str:
        if not documents:
            return "No relevant context found."

        context_parts = []
        for doc in documents:
            if not isinstance(doc, dict):
                continue
            content = doc.get("content") or str(doc)
            metadata = doc.get("metadata", {})
            source = metadata.get("source", "Unknown")
            chapter = metadata.get("chapter", "Unknown")
            context_parts.append(f"[Source: {source} - {chapter}]\n{content}\n")

        joined = "\n---\n".join(context_parts)
        limit = Config.MAX_CONTEXT_LENGTH
        if len(joined) > limit:
            return joined[:limit] + "\n[truncated]"
        return joined
