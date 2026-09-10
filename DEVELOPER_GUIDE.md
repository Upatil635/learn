# LearnEasy - Developer Guide

Advanced guide for developers who want to extend and customize the LearnEasy system.

## 🛠️ Development Environment Setup

### 1. Clone and Setup
```bash
cd /Users/umeshbhagvanpatil/POC/LearnEasy
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. IDE Setup (VS Code)
```bash
# Install extensions
# - Python
# - PyLance
# - Flask Snippets
# - ES7+ React/Redux/React-Native

# Create .vscode/settings.json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "editor.formatOnSave": true,
  "python.formatting.provider": "black"
}
```

## 📦 Code Architecture

### Backend Structure
```
src/
├── chunker.py          # DocumentChunker class
├── vector_db.py        # VectorDB class
├── ingester.py         # DocumentIngester class
├── rag_retriever.py    # RAGRetriever class
├── gemini_handler.py   # GeminiHandler class
└── cli.py              # CLI interface

web/backend/
└── app.py              # Flask REST API
```

### Key Classes

#### VectorDB
```python
from src.vector_db import VectorDB

db = VectorDB()
db.add_documents(documents, metadatas, ids)
results = db.query("search query", top_k=5)
stats = db.get_collection_stats()
```

#### RAGRetriever
```python
from src.rag_retriever import RAGRetriever

retriever = RAGRetriever()
results = retriever.retrieve_context("query", top_k=5)
results = retriever.retrieve_by_chapter("Chapter Name")
results = retriever.retrieve_by_subject("Subject")
```

#### GeminiHandler
```python
from src.gemini_handler import GeminiHandler

gemini = GeminiHandler()
quiz = gemini.generate_quiz(context, num_questions=5, difficulty="medium")
answer = gemini.answer_question(context, question)
summary = gemini.summarize_content(context)
explain = gemini.explain_concept("concept", difficulty="intermediate")
```

## 🔧 Extending the System

### 1. Add New Document Source

**Step 1: Create ingester for new format**
```python
# src/ingester_pdf.py
class PDFIngester:
    @staticmethod
    def load_pdf(filepath: str) -> str:
        # Extract text from PDF
        import pypdf
        with open(filepath, 'rb') as f:
            reader = pypdf.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text
```

**Step 2: Integrate with DocumentIngester**
```python
# In src/ingester.py
documents = DocumentIngester.load_documents_from_directory(
    directory="PDFs/",
    file_types=[".md", ".pdf", ".docx"]
)
```

### 2. Add New Embedding Model

**Step 1: Create custom embedding handler**
```python
# src/embeddings.py
from sentence_transformers import SentenceTransformer

class CustomEmbedding:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L12-v2')
    
    def embed(self, text: str) -> list:
        return self.model.encode(text).tolist()
```

**Step 2: Update ChromaDB configuration**
```python
# In src/vector_db.py
self.collection = self.client.get_or_create_collection(
    name="learnEasy",
    embedding_function=CustomEmbedding().embed
)
```

### 3. Add New AI Provider (Beyond Gemini)

**Step 1: Create provider handler**
```python
# src/ai_providers/openai_handler.py
import openai

class OpenAIHandler:
    def __init__(self):
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def generate_quiz(self, context: str, num_questions: int = 5):
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a teacher..."},
                {"role": "user", "content": f"Generate {num_questions} questions..."}
            ]
        )
        return response.choices[0].message.content
```

**Step 2: Use in RAG system**
```python
# In src/gemini_handler.py - create abstract base class
from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    def generate_quiz(self, context: str, num_questions: int):
        pass
```

### 4. Add Database Filter Capabilities

**Step 1: Extend retrieval methods**
```python
# In src/rag_retriever.py
def retrieve_by_date(self, date_range: tuple) -> Dict:
    results = self.vector_db.collection.get(
        where={
            "date": {"$gte": date_range[0], "$lte": date_range[1]}
        }
    )
    return results
```

### 5. Add User Authentication

**Step 1: Create user model**
```python
# web/backend/models.py
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Step 2: Add authentication endpoints**
```python
# web/backend/app.py
from flask_jwt_extended import JWTManager, create_access_token

jwt = JWTManager(app)

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    user = User(
        username=data['username'],
        password=generate_password_hash(data['password']),
        email=data['email']
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"token": create_access_token(identity=user.id)})
```

## 🧪 Testing

### Unit Tests
```python
# tests/test_chunker.py
import pytest
from src.chunker import DocumentChunker

def test_chunk_markdown():
    content = "# Title\n\nParagraph 1\n\nParagraph 2"
    chunks = DocumentChunker.chunk_markdown(content)
    assert len(chunks) > 0
    assert all(chunk for chunk in chunks)

def test_add_metadata():
    text = "# Chapter 1"
    text, metadata = DocumentChunker.add_metadata(text, "test.md")
    assert metadata["source"] == "test.md"
    assert "Chapter" in metadata["chapter"]
```

### Integration Tests
```python
# tests/test_integration.py
import pytest
from src.ingester import DocumentIngester
from src.rag_retriever import RAGRetriever

def test_end_to_end():
    # Ingest documents
    ingester = DocumentIngester()
    documents = ingester.load_md_files("test_files/")
    ingester.ingest_documents(documents)
    
    # Query
    retriever = RAGRetriever()
    results = retriever.retrieve_context("test query")
    
    assert results["total_retrieved"] > 0
```

### Run Tests
```bash
pytest tests/ -v
pytest tests/test_chunker.py::test_chunk_markdown -v
```

## 📊 Monitoring & Logging

### Add Logging
```python
# In any module
import logging

logger = logging.getLogger(__name__)

logger.info("Document ingestion started")
logger.warning("No results found for query")
logger.error("Failed to generate quiz", exc_info=True)
```

### Setup Logging Configuration
```python
# config/logging.py
import logging
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/learnEasy.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'DEBUG',
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
```

## 🚀 Performance Optimization

### 1. Caching Results
```python
# web/backend/app.py
from functools import lru_cache
import pickle

@lru_cache(maxsize=128)
def cached_query(query: str) -> dict:
    return retriever.retrieve_context(query)
```

### 2. Batch Processing
```python
# src/batch_processor.py
def batch_ingest(files: list, batch_size: int = 10):
    for i in range(0, len(files), batch_size):
        batch = files[i:i+batch_size]
        # Process batch
        vector_db.add_documents(batch_docs, batch_metadata, batch_ids)
```

### 3. Database Optimization
```bash
# Monitor database size
du -sh data/chroma_db/

# Vacuum ChromaDB for optimization
sqlite3 data/chroma_db/chroma.sqlite3 "VACUUM;"
```

## 🔐 Security Best Practices

### 1. Input Validation
```python
from pydantic import BaseModel, validator

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    
    @validator('query')
    def query_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()[:1000]
```

### 2. Rate Limiting
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/query', methods=['POST'])
@limiter.limit("10 per minute")
def query():
    # Rate limited to 10 per minute
    pass
```

### 3. CORS Security
```python
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})
```

## 📈 Scaling Strategies

### Horizontal Scaling
```python
# Use message queue for async processing
from celery import Celery

celery = Celery(app.name, broker='redis://localhost:6379')

@celery.task
def async_quiz_generation(context: str):
    return gemini.generate_quiz(context)
```

### Database Scaling
```python
# Migrate from ChromaDB to Pinecone for production
from pinecone import Pinecone

pc = Pinecone(api_key=Config.PINECONE_KEY)
index = pc.Index("learnEasy")

# Replace ChromaDB calls with Pinecone API
```

## 🐛 Debugging

### Debug Mode
```python
# web/backend/app.py
if Config.DEBUG:
    app.run(debug=True)
    app.logger.setLevel(logging.DEBUG)
```

### VSCode Debugging
Create `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Flask Backend",
            "type": "python",
            "request": "launch",
            "module": "flask",
            "env": {"FLASK_APP": "web/backend/app.py"},
            "args": ["run", "--port", "5000"],
            "jinja": true
        }
    ]
}
```

## 🎨 Frontend Development

### Component Structure
```jsx
// src/components/MyComponent.js
import React, { useState, useEffect } from 'react';
import { Box, Button, CircularProgress } from '@mui/material';

export default function MyComponent() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  
  useEffect(() => {
    loadData();
  }, []);
  
  const loadData = async () => {
    setLoading(true);
    try {
      // API call
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Box sx={{ p: 2 }}>
      {loading ? <CircularProgress /> : <div>{data}</div>}
    </Box>
  );
}
```

### State Management (Future)
```jsx
// For larger apps, consider Redux or Zustand
import { create } from 'zustand';

const useStore = create((set) => ({
  query: '',
  results: [],
  setQuery: (q) => set({ query: q }),
  setResults: (r) => set({ results: r }),
}));
```

## 📚 Adding Documentation

### Code Comments
```python
def retrieve_context(self, query: str, top_k: int = None) -> Dict[str, Any]:
    """
    Retrieve relevant context from vector database.
    
    Args:
        query: The search query string
        top_k: Number of results to return (default: Config.TOP_K_RESULTS)
    
    Returns:
        dict: Contains 'retrieved_documents' and 'context' string
    
    Raises:
        ConnectionError: If database connection fails
    """
    pass
```

### Generate Documentation
```bash
# Using Sphinx
sphinx-quickstart docs
cd docs
make html
```

## 🤝 Contributing

### Development Workflow
1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes and commit: `git commit -m "feat: add new feature"`
3. Push and create PR: `git push origin feature/my-feature`
4. Get review and merge

### Code Style
```bash
# Format code
black src/ web/backend/

# Lint
flake8 src/ web/backend/

# Type checking
mypy src/
```

## 📦 Deployment Configuration

### Docker Setup
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "web.backend.app:app"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "5000:5000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
  
  frontend:
    image: node:16
    working_dir: /app
    volumes:
      - ./web/frontend:/app
    ports:
      - "3000:3000"
    command: npm start
```

## 🎯 Performance Profiling

```python
# profile_app.py
import cProfile
import pstats
from src.ingester import DocumentIngester

profiler = cProfile.Profile()
profiler.enable()

# Run code to profile
ingester = DocumentIngester()
documents = ingester.load_md_files()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

## 📞 Getting Help

- Check existing documentation
- Review error logs
- Create GitHub issues
- Ask in development forums

---

**Happy Development! 🚀**
