# LearnEasy Web Application

Professional Material-UI based web interface for LearnEasy with React frontend and Flask backend.

## 🏗️ Architecture

```
Frontend (React + Material-UI)
        ↓ (REST API)
Backend (Flask)
        ↓
Database (ChromaDB)
        ↓
AI Engine (Gemini API)
```

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd web
python3 -m pip install -r requirements.txt
```

### 2. Frontend Setup

```bash
cd web/frontend
npm install
```

### 3. Run Development Servers

**Terminal 1 - Backend:**
```bash
cd web
python3 app.py
# Server runs on http://localhost:5000
```

**Terminal 2 - Frontend:**
```bash
cd web/frontend
npm start
# App opens at http://localhost:3000
```

## 📁 Project Structure

```
web/
├── backend/
│   └── app.py              # Flask REST API
├── frontend/
│   ├── src/
│   │   ├── App.js          # Main app component
│   │   ├── components/     # React components
│   │   │   ├── QueryTab.js       # Search notes
│   │   │   ├── QuizTab.js        # Generate quizzes
│   │   │   ├── AskTab.js         # Ask questions
│   │   │   └── StatusTab.js      # Database status
│   │   ├── services/
│   │   │   └── api.js      # Axios API client
│   │   ├── index.js        # React entry point
│   │   └── index.css       # Global styles
│   ├── public/
│   │   └── index.html      # HTML template
│   ├── package.json        # npm dependencies
│   └── .env.example        # Environment template
├── requirements.txt        # Python dependencies
└── README.md
```

## 🎨 Features

### Search Notes (Query Tab)
- 🔍 Semantic search across all documents
- 📚 Filter by subject
- ⚡ Adjustable result count
- 🏷️ Topic suggestions
- 📊 Similarity scores

### Generate Quiz (Quiz Tab)
- 🎯 AI-powered quiz generation
- 📈 Three difficulty levels (Easy/Medium/Hard)
- ✍️ Multiple choice format
- 📝 Custom question count
- ✓ Instant scoring
- 💡 Detailed explanations

### Ask Questions (Ask Tab)
- 💭 Natural language Q&A
- 🎓 Subject-specific answers
- 🔗 Source references
- 📖 Context-aware responses

### Database Status (Status Tab)
- 📊 Real-time database statistics
- 📚 Documents indexed count
- 🏷️ Subjects and chapters overview
- ⚙️ One-click setup/refresh

## 🔧 API Endpoints

### Health & Status
- `GET /api/health` - System health check
- `GET /api/status` - Database statistics
- `POST /api/setup` - Initialize database

### Queries & Retrieval
- `POST /api/query` - Search knowledge base
- `GET /api/chapters` - List chapters by subject
- `GET /api/search/suggestions` - Search suggestions

### AI Features
- `POST /api/quiz` - Generate quiz
- `POST /api/ask` - Answer question
- `POST /api/explain-concept` - Explain concept

## 📱 Responsive Design

- ✅ Mobile-first approach
- ✅ Tablet optimized
- ✅ Desktop full-featured
- ✅ Touch-friendly UI
- ✅ Dark mode ready (Material-UI theme)

## 🛠️ Configuration

### Backend (.env)
```env
GEMINI_API_KEY=your_api_key_here
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:5000/api
```

## 🚢 Deployment

### Backend Deployment (Gunicorn)

```bash
cd web
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

### Frontend Deployment (Production Build)

```bash
cd web/frontend
npm run build
```

This creates an optimized production build in `build/` directory.

**Deploy to Vercel:**
```bash
npm install -g vercel
vercel
```

**Deploy to Netlify:**
```bash
npm install -g netlify-cli
netlify deploy --prod
```

## 📊 Performance Optimization

### Frontend
- Code splitting via React.lazy
- Memoization for heavy components
- Image optimization
- CSS-in-JS minification

### Backend
- Request caching
- Vector database indexing
- Connection pooling
- Response compression

## 🔐 Security

- ✅ CORS enabled for safe cross-origin requests
- ✅ API validation on all endpoints
- ✅ Input sanitization
- ✅ Environment variables for secrets
- ✅ Rate limiting (recommended for production)

## 🐛 Troubleshooting

### Backend Connection Failed
```
Error: Cannot connect to http://localhost:5000
Solution: Ensure backend is running (python3 app.py)
```

### CORS Errors
```
Error: Access to XMLHttpRequest blocked by CORS
Solution: Check CORS settings in backend/app.py
```

### Empty Database
```
No documents indexed
Solution: Run setup via UI or: curl -X POST http://localhost:5000/api/setup
```

### Port Already in Use
```
# Change port in backend
python3 -c "from backend.app import app; app.run(port=5001)"

# Change port in frontend
PORT=3001 npm start
```

## 📈 Performance Metrics

Target response times:
- Query search: < 2 seconds
- Quiz generation: < 5 seconds
- Question answering: < 5 seconds
- Page load: < 3 seconds

## 🧪 Testing

### Backend Tests
```bash
pytest web/backend/test_app.py -v
```

### Frontend Tests
```bash
npm test
```

## 📚 Technology Stack

**Frontend:**
- React 18
- Material-UI (MUI) v5
- Axios for HTTP
- React Router for navigation
- Notistack for notifications

**Backend:**
- Flask 3
- Flask-CORS
- ChromaDB
- Google Generative AI
- LangChain

## 🚀 Future Enhancements

- [ ] Dark mode toggle
- [ ] User authentication
- [ ] Save favorite quizzes
- [ ] Progress tracking
- [ ] Offline mode
- [ ] Mobile native app (React Native)
- [ ] Real-time collaboration
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Video embedding in notes

## 📖 Documentation

- [Backend API Docs](./backend/README.md)
- [Frontend Components](./frontend/src/components/README.md)
- [Deployment Guide](./DEPLOYMENT.md)

## 🤝 Contributing

Contributions welcome! Areas to improve:
- UI/UX enhancements
- Performance optimization
- New features
- Bug fixes
- Documentation

## 📝 License

MIT License - See LICENSE file

---

**Happy Learning! 🎓**
