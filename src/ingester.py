"""MD file ingestion pipeline"""
import os
import glob
from typing import List, Dict, Any
from pathlib import Path
from src.chunker import DocumentChunker
from src.vector_db import get_vector_db
from config import Config


class DocumentIngester:
    def __init__(self):
        self.vector_db = get_vector_db()
        self.chunker = DocumentChunker()

    def load_md_files(self, directory: str = None) -> List[Dict[str, Any]]:
        """Load all .md files from a directory"""
        if directory is None:
            directory = Config.MD_FILES_PATH

        md_files = glob.glob(os.path.join(directory, "*.md"))
        documents = []

        for file_path in sorted(md_files):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                filename = Path(file_path).stem

                documents.append({
                    "filename": filename,
                    "filepath": file_path,
                    "content": content
                })
                print(f"✓ Loaded {filename}.md")
            except Exception as e:
                print(f"✗ Error loading {file_path}: {e}")

        return documents

    def ingest_documents(self, documents: List[Dict[str, Any]]):
        """Process and ingest documents into vector DB"""
        all_chunks = []
        all_metadatas = []
        all_ids = []
        chunk_id = 0

        for doc in documents:
            filename = doc["filename"]
            content = doc["content"]

            # Chunk the document
            chunks = self.chunker.chunk_markdown(content)

            for chunk in chunks:
                # Add metadata
                text, metadata = self.chunker.add_metadata(chunk, filename)
                metadata["subject"] = self._infer_subject(filename)

                all_chunks.append(text)
                all_metadatas.append(metadata)
                all_ids.append(f"{filename}_{chunk_id}")
                chunk_id += 1

            print(f"  → Created {len(chunks)} chunks from {filename}")

        # Add to vector database
        if all_chunks:
            self.vector_db.add_documents(all_chunks, all_metadatas, all_ids)
            stats = self.vector_db.get_collection_stats()
            print(f"\n✓ Ingestion complete! Total documents in DB: {stats['total_documents']}")
            print(f"   Documents per subject:")
            results = self.vector_db.collection.get(limit=50000)
            subjects_count = {}
            for meta in results.get("metadatas", []):
                subj = meta.get("subject", "Unknown")
                subjects_count[subj] = subjects_count.get(subj, 0) + 1
            for subj, count in sorted(subjects_count.items()):
                print(f"   - {subj}: {count} chunks")

    @staticmethod
    def _infer_subject(filename: str) -> str:
        """Infer subject from filename"""
        subject_map = {
            "english": "English",
            "marathi": "Marathi",
            "math": "Mathematics",
            "GS": "General Science",
            "Geo": "Geography",
            "HC": "History & Culture",
            "sans": "Sanskrit"
        }
        return subject_map.get(filename, filename)

    def reingest_documents(self):
        """Clear and reingest all documents"""
        print("Reingesting documents...")
        self.vector_db.clear_collection()
        documents = self.load_md_files()
        self.ingest_documents(documents)
        try:
            from src.ai_cache import AiCache
            cleared = AiCache().clear()
            print(f"✓ Cleared {cleared} cached AI generations (they used the old chunks)")
        except Exception as e:
            print(f"⚠ Could not clear AI cache: {e}")
