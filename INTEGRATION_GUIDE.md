# LearnEasy - Complete Integration Guide

Complete step-by-step guide to set up and run the entire LearnEasy system (CLI + Web UI).

## 📋 Prerequisites

- Python 3.8+ 
- Node.js 14+ (for web UI)
- Git
- Google Gemini API Key

## 🎯 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    LearnEasy Platform                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────┐         ┌──────────────────┐    │
│  │   Web UI         │         │   CLI Interface  │    │
│  │  (React/MUI)     │         │  (Click/Python)  │    │
│  └────────┬─────────┘         └────────┬─────────┘    │
│           │                            │               │
│           └────────────┬───────────────┘               │
│                        │                               │
│           ┌────────────▼───────────────┐              │
│           │  Flask REST API Server     │              │
│           │  (5000)                    │              │
│           └────────────┬───────────────┘              │
│                        │                               │
│  ┌────────────────────┼────────────────────┐          │
│  │                    │                    │          │
│  ▼                    ▼                    ▼          │
│ RAG Retriever    Document Ingester    Gemini Handler  │
│                                                       │
│  └────────────┬──────────────────┬────────────────┘  │
│               │                  │                   │
│               ▼                  ▼                   │
│          ┌────────────────────────────┐             │
│          │   ChromaDB Vector DB       │             │
│          │  (Local Storage)           │             │
│          └────────────┬───────────────┘             │
│                       │                            │
│                       ▼                            │
│                  MD Files                          │
│             (PDFs/8th/*.md)                        │
│                                                    │
└────────────────────────────────────────────────────┘
```

## 🚀 Complete Setup (From Zero to Production)

### Phase 1: Environment Setup (5 minutes)

```bash
# 1. Navigate to project
cd /Users/umeshbhagvanpatil/POC/LearnEasy

# 2. Create .env file
cp .env.example .env

# 3. Edit .env and add your API key
# GEMINI_API_KEY=your_key_from_https://ai.google.dev/gemini-api
```

### Phase 2: Install Dependencies (10 minutes)

```bash
# 1. Python backend dependencies
python3 -m pip install -r requirements.txt

# 2. Web backend dependencies
python3 -m pip install -r web/requirements.txt

# 3. Web frontend dependencies
cd web/frontend
npm install
cd ../..
```

### Phase 3: Verify Setup (2 minutes)

```bash
# Test setup
python3 test_setup.py

# Should show: ✓ All checks passed! Ready to run
```

### Phase 4: Initialize Database (2-5 minutes)

```bash
# Using CLI
python3 main.py setup

# OR using Web UI (after starting server)
# Open http://localhost:3000 → Status tab → Setup Database
```

## 📚 Usage Examples

### Option A: Using CLI Interface

#### 1. Search for Notes
```bash
python3 main.py query "photosynthesis"
python3 main.py query "Newton's laws" --top-k 10 --subject "Physics"
```

#### 2. Generate Quiz
```bash
python3 main.py quiz "photosynthesis"
python3 main.py quiz "evolution" --difficulty hard --num-questions 10
```

#### 3. Ask Questions
```bash
python3 main.py ask "What is photosynthesis?"
python3 main.py ask "Explain quantum mechanics" --subject "Physics"
```

#### 4. View Information
```bash
python3 main.py status        # Database statistics
python3 main.py chapters      # All chapters
python3 main.py chapters -s "Mathematics"  # Math chapters
```

### Option B: Using Web Interface

#### Start Servers

**Terminal 1 - Backend Server:**
```bash
cd /Users/umeshbhagvanpatil/POC/LearnEasy
python3 web/backend/app.py
# Runs on http://localhost:5000
```

**Terminal 2 - Frontend Server:**
```bash
cd /Users/umeshbhagvanpatil/POC/LearnEasy/web/frontend
npm start
# Opens http://localhost:3000
```

#### Use the Web UI
1. **Search Tab**: Find chapter notes
2. **Quiz Tab**: Generate and take quizzes
3. **Ask Tab**: Get AI-powered answers
4. **Status Tab**: View database info & setup

## 🔑 API Reference

### Backend API Base URL
```
http://localhost:5000/api
```

### Key Endpoints

```bash
# Health Check
curl http://localhost:5000/api/health

# Search for content
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "photosynthesis",
    "top_k": 5,
    "subject": null
  }'

# Generate Quiz
curl -X POST http://localhost:5000/api/quiz \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "photosynthesis",
    "difficulty": "medium",
    "num_questions": 5,
    "subject": null
  }'

# Get Answer
curl -X POST http://localhost:5000/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is photosynthesis?",
    "subject": null
  }'

# Get Database Status
curl http://localhost:5000/api/status

# Get Chapters
curl http://localhost:5000/api/chapters

# Setup Database
curl -X POST http://localhost:5000/api/setup
```

## 📊 Available Subjects & Files

The system includes 6 8th-grade subjects:

1. **English** (english.md) - 175 KB
2. **Mathematics** (math.md) - 171 KB
3. **Marathi** (marathi.md) - 194 KB
4. **General Science** (GS.md) - 328 KB
5. **Geography** (Geo.md) - 174 KB
6. **History & Culture** (HC.md) - 248 KB
7. **Sanskrit** (sans.md) - Coming (being converted...)

Total: ~1,290 KB of educational content

## 🛠️ Configuration Options

### Environment Variables (.env)

```env
# API Configuration
GEMINI_API_KEY=your_api_key_here

# Database Configuration
CHROMA_DB_PATH=./data/chroma_db
CHROMA_COLLECTION_NAME=learnEasy_embeddings

# Document Processing
CHUNK_SIZE=1000              # Larger = more context
CHUNK_OVERLAP=200            # Overlap between chunks

# RAG Configuration
SIMILARITY_THRESHOLD=0.6     # 0-1, higher = stricter
MAX_CONTEXT_LENGTH=3000      # Max chars for LLM
TOP_K_RESULTS=5             # Default results count
```

### Optimization Tips

**For Better Context:**
```
CHUNK_SIZE=1500
CHUNK_OVERLAP=300
```

**For Faster Queries:**
```
CHUNK_SIZE=500
TOP_K_RESULTS=3
```

**For More Precise Answers:**
```
SIMILARITY_THRESHOLD=0.7
MAX_CONTEXT_LENGTH=5000
```

## 📈 Performance Tuning

### Database Performance
```bash
# Check database size
du -sh data/chroma_db/

# Check indexed documents
python3 -c "from src.vector_db import VectorDB; db=VectorDB(); print(db.get_collection_stats())"
```

### API Performance
- Backend queries typically < 2 seconds
- Quiz generation typically < 5 seconds
- Frontend page loads < 3 seconds

### Scaling Considerations
- Current setup handles ~10,000 documents
- For larger datasets, consider Pinecone or Qdrant
- Multi-GPU support available with specialized backends

## 🔐 Security Checklist

- [ ] Never commit `.env` to git
- [ ] Regenerate API key if exposed
- [ ] Use environment variables for secrets
- [ ] Enable CORS only for trusted domains
- [ ] Rate-limit API endpoints in production
- [ ] Use HTTPS in production
- [ ] Validate all user inputs
- [ ] Regular security audits

## 🐛 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'chromadb'"
```bash
python3 -m pip install chromadb
```

### Problem: "GEMINI_API_KEY not set"
```bash
# Check .env file
cat .env | grep GEMINI_API_KEY

# Add missing key
echo "GEMINI_API_KEY=your_key" >> .env
```

### Problem: "Connection refused localhost:5000"
```bash
# Ensure backend is running
cd web
python3 backend/app.py

# Check if port is in use
lsof -i :5000
```

### Problem: "npm ERR! no matching version"
```bash
# Update npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### Problem: "CORS error in frontend"
```python
# Check Flask app has CORS enabled
# In web/backend/app.py:
from flask_cors import CORS
CORS(app)
```

### Problem: "No documents indexed"
```bash
# Run setup
python3 main.py setup

# Or via API
curl -X POST http://localhost:5000/api/setup

# Or via Web UI: Status tab → Setup Database
```

## 🚢 Production Deployment

### Backend Deployment (AWS/Heroku/DigitalOcean)

```bash
# 1. Create Procfile
echo "web: gunicorn -w 4 web.backend.app:app" > Procfile

# 2. Install gunicorn
python3 -m pip install gunicorn

# 3. Create requirements for production
python3 -m pip freeze > requirements-prod.txt

# 4. Deploy
# Heroku: git push heroku main
# DigitalOcean: Use App Platform
# AWS: Use Elastic Beanstalk
```

### Frontend Deployment (Vercel/Netlify)

```bash
cd web/frontend

# 1. Build for production
npm run build

# 2. Deploy to Vercel
npm i -g vercel
vercel

# OR Deploy to Netlify
npm i -g netlify-cli
netlify deploy --prod --dir=build
```

### Environment Setup for Production

```env
# Production .env
GEMINI_API_KEY=production_key_here
CHROMA_DB_PATH=/var/lib/learnEasy/chroma_db
REACT_APP_API_URL=https://api.learnEasy.com/api
DEBUG=False
```

## 📊 Monitoring & Analytics

### Check System Health
```bash
# View logs
python3 web/backend/app.py 2>&1 | tee logs.txt

# Check database performance
sqlite3 data/chroma_db/chroma.sqlite3 "SELECT COUNT(*) FROM documents;"

# Monitor API usage
# Add logging to web/backend/app.py
```

## 🔄 Data Management

### Backup Database
```bash
# Backup ChromaDB
cp -r data/chroma_db data/chroma_db.backup

# Backup markdown files
cp -r PDFs/8th PDFs/8th.backup
```

### Reset Database
```bash
# Clear and reingest
python3 main.py reset
python3 main.py setup

# Or via API
curl -X POST http://localhost:5000/api/setup
```

### Update Content
```bash
# Add new markdown files to PDFs/8th/
# Then reingest
python3 main.py setup
```

## 📚 Learning Resources

### Understanding RAG
- [What is RAG?](https://docs.llamaindex.ai/guides/query_engine/retrieval_augmented_generation/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [Vector Databases Explained](https://www.youtube.com/watch?v=dN0lsF2cvm0)

### Development
- [React Documentation](https://react.dev)
- [Material-UI Docs](https://mui.com)
- [Flask Documentation](https://flask.palletsprojects.com)
- [Python Gemini API](https://ai.google.dev/tutorials/python_quickstart)

## 🎉 Success Indicators

Once fully set up, you should be able to:

✅ Run `python3 main.py status` and see > 0 documents
✅ Execute `python3 main.py query "any topic"` and get results
✅ Generate a quiz with `python3 main.py quiz "topic"`
✅ Ask questions with `python3 main.py ask "question"`
✅ Access web UI at http://localhost:3000
✅ See database stats in Status tab

## 🤝 Support

For issues:
1. Check this guide's troubleshooting section
2. Review error messages carefully
3. Check logs: `cat logs.txt`
4. Verify .env configuration
5. Ensure all dependencies installed

## 📝 Next Steps

1. ✅ Complete setup and initialization
2. ✅ Test with sample queries
3. ✅ Explore all features
4. ⭕ Deploy to production
5. ⭕ Monitor and optimize
6. ⭕ Gather user feedback
7. ⭕ Add more content
8. ⭕ Scale infrastructure

---

**You're all set! Happy Learning! 🚀📚**
