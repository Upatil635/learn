# LearnEasy - AI-Powered Learning Platform with RAG

LearnEasy is an intelligent learning assistant that combines **Retrieval-Augmented Generation (RAG)**, **ChromaDB Vector Database**, and **Google Gemini API** to help students fetch chapter-specific notes and generate custom quizzes.

## 🎯 Key Features

- **📚 Document Ingestion**: Automatically loads and chunks markdown files from your PDFs
- **🔍 Semantic Search**: Uses vector embeddings to find relevant content based on meaning
- **📝 Quiz Generation**: AI-powered quiz creation with multiple difficulty levels
- **❓ Q&A System**: Answer any question based on retrieved educational content
- **📊 Chapter-based Organization**: Browse by chapters and subjects
- **⚡ Fast Retrieval**: ChromaDB for efficient similarity search

## 🏗️ Architecture

```
┌─────────────────┐
│   MD Files      │ (Markdown textbooks)
└────────┬────────┘
         │
    ┌────▼────┐
    │ Chunker │ (Smart document segmentation)
    └────┬────┘
         │
    ┌────▼──────────┐
    │ ChromaDB      │ (Vector Database with embeddings)
    └────┬──────────┘
         │
    ┌────▼──────────┐
    │ RAG Retriever │ (Context retrieval)
    └────┬──────────┘
         │
    ┌────▼──────────┐
    │ Gemini API    │ (Quiz & Answer generation)
    └───────────────┘
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Create .env file
cp .env.example .env

# Edit .env and add your Gemini API key
GEMINI_API_KEY=your_api_key_here
```

> ⚠️ Get your Gemini API key from: https://ai.google.dev/gemini-api/docs/api-key

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize the System

```bash
python main.py setup
```

This will:
- Load all `.md` files from `PDFs/8th/`
- Chunk documents intelligently
- Create embeddings using ChromaDB
- Store them in vector database

## 📖 Usage

### Query Knowledge Base

```bash
# Search for relevant notes
python main.py query "photosynthesis"

# Filter by subject
python main.py query "photosynthesis" --subject "General Science"

# Get more results
python main.py query "photosynthesis" --top-k 10
```

### Generate Quiz

```bash
# Create 5 medium difficulty questions
python main.py quiz "photosynthesis"

# Custom difficulty and number
python main.py quiz "quantum mechanics" --difficulty hard --num-questions 10

# Quiz from specific subject
python main.py quiz "evolution" --subject "Biology"
```

### Ask Questions

```bash
# Get detailed answers
python main.py ask "What is photosynthesis?"

# Answers filtered by subject
python main.py ask "Explain evolution" --subject "General Science"
```

### View Database Status

```bash
# Check vector database statistics
python main.py status

# List available chapters
python main.py chapters

# List chapters by subject
python main.py chapters --subject "Mathematics"
```

### Reset Database

```bash
# Clear and reset
python main.py reset
```

## 🔧 Configuration

Edit `.env` to customize:

```env
# Chunk size for document splitting
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Similarity threshold for retrieval
SIMILARITY_THRESHOLD=0.6

# Maximum context length for LLM
MAX_CONTEXT_LENGTH=3000

# Number of results to retrieve
TOP_K_RESULTS=5
```

## 📁 Project Structure

```
LearnEasy/
├── src/
│   ├── chunker.py          # Document chunking strategies
│   ├── vector_db.py        # ChromaDB management
│   ├── ingester.py         # MD file ingestion
│   ├── rag_retriever.py    # RAG retrieval system
│   ├── gemini_handler.py   # Gemini API integration
│   └── cli.py              # Command-line interface
├── config/
│   └── config.py           # Configuration management
├── data/
│   └── chroma_db/          # Vector database storage
├── PDFs/8th/               # Markdown textbooks
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
├── .env.example            # Environment template
└── README.md              # This file
```

## 🧠 How RAG Works

### 1. **Document Chunking**
- Markdown files are split into logical chunks (by chapters, sections, paragraphs)
- Each chunk is ~1000 tokens with 200-token overlap to preserve context

### 2. **Embedding & Storage**
- ChromaDB converts chunks into vector embeddings
- Vectors capture semantic meaning, not just keywords
- Stored with metadata (source, chapter, subject)

### 3. **Retrieval**
- User query is converted to embedding
- System finds most similar chunks using cosine similarity
- Top 5 chunks returned as context

### 4. **Generation**
- Retrieved context + user request sent to Gemini
- Gemini generates quizzes, answers, summaries
- Grounded in actual textbook content

## 📊 Supported Subjects

- 📖 English
- 🌐 Marathi
- 🔢 Mathematics
- 🔬 General Science (GS)
- 🗺️ Geography (Geo)
- 🏛️ History & Culture (HC)
- 🇮🇳 Sanskrit (Sans)

## ⚙️ System Requirements

- Python 3.8+
- 2GB RAM minimum
- 500MB disk space for vector database
- Internet connection (for Gemini API)

## 🔐 Security Notes

- **NEVER commit `.env` file to git**
- Keep your Gemini API key confidential
- Regenerate API key if exposed

## 🐛 Troubleshooting

### "GEMINI_API_KEY not set"
```bash
# Make sure .env exists and has valid key
cat .env | grep GEMINI_API_KEY
```

### "No documents in database"
```bash
# Reingest all documents
python main.py setup

# Or check if MD files exist
ls PDFs/8th/*.md
```

### "Connection timeout to Gemini"
- Check internet connection
- Verify API key is valid
- Check rate limits: https://ai.google.dev/pricing

## 📈 Performance Optimization

### Chunking Strategy
- Larger chunks (2000+ tokens): Better context preservation, fewer documents
- Smaller chunks (500-1000 tokens): Better retrieval precision, more documents

### Embedding Quality
- ChromaDB uses all-MiniLM-L6-v2 by default
- For better quality: consider more powerful embedding models

### Database Optimization
- Regularly update vector database with new content
- Monitor chunk overlap for context preservation
- Use subject filters for faster queries

## 🚀 Advanced Usage

### Custom Chunking Strategy
```python
from src.chunker import DocumentChunker

chunker = DocumentChunker()
chunks = chunker.chunk_markdown(content, chunk_size=2000, overlap=500)
```

### Direct Vector Database Access
```python
from src.vector_db import VectorDB

db = VectorDB()
results = db.query("photosynthesis", top_k=10)
```

### Manual RAG Pipeline
```python
from src.rag_retriever import RAGRetriever
from src.gemini_handler import GeminiHandler

retriever = RAGRetriever()
context = retriever.retrieve_context("photosynthesis")

gemini = GeminiHandler()
quiz = gemini.generate_quiz(context["context"])
```

## 📚 Vector Databases Comparison

| Feature | ChromaDB | Pinecone | Qdrant | Weaviate |
|---------|----------|----------|--------|----------|
| Type | Local/Cloud | Cloud | Local/Cloud | Local/Cloud |
| Setup | Easy | Simple | Medium | Medium |
| Cost | Free | Paid | Free | Free |
| Best For | Local dev | Production | Enterprise | Enterprise |

**We use ChromaDB for:**
- ✅ Easy local setup
- ✅ No API key needed
- ✅ Perfect for development
- ✅ Fast for small-medium datasets

## 🤝 Contributing

Contributions welcome! Areas to improve:
- Additional embedding models
- Multi-language support
- Advanced filtering options
- Web UI interface
- Mobile app

## 📝 License

This project is open source and available under the MIT License.

## 🙋 Support

For issues and questions:
1. Check the troubleshooting section
2. Review configuration in `.env`
3. Check logs for error messages
4. Verify file paths are correct

---

**Built with ❤️ for students everywhere**
