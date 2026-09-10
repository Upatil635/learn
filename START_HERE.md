# 🎓 LearnEasy - START HERE

Welcome! This is your complete AI-powered learning platform. Get started in minutes.

## ⚡ 30-Second Quick Start

```bash
# 1. Add your API key
cp .env.example .env
# Edit .env and add: GEMINI_API_KEY=your_key_from_https://ai.google.dev/gemini-api

# 2. Install & initialize
python3 -m pip install -r requirements.txt
python3 main.py setup

# 3. Try it!
python3 main.py query "photosynthesis"
python3 main.py quiz "Newton's laws"
python3 main.py ask "What is gravity?"
```

## 🎯 What Would You Like to Do?

### 👤 I'm a Student
→ Use the **CLI** or **Web UI** to:
- 📚 Search for chapter notes
- 🎯 Generate practice quizzes
- ❓ Ask AI tutor questions

**Quick Start:**
```bash
python3 main.py query "your topic"
python3 main.py quiz "your topic"
```

### 👨‍🏫 I'm a Teacher
→ Use to create:
- 📝 Custom quizzes for assessments
- 📚 Supplementary materials
- 📊 Student review materials

**Example:**
```bash
python3 main.py quiz "evolution" --difficulty hard --num-questions 20
```

### 💻 I'm a Developer
→ Check out:
- `DEVELOPER_GUIDE.md` - Extend and customize
- `PROJECT_SUMMARY.md` - Architecture overview
- `src/` - Core modules to modify

## 📖 Documentation Map

```
START_HERE.md (You are here)
    ↓
Choose your path:
    ├─ QUICKSTART.md        (3-min setup)
    ├─ README.md            (Features guide)
    ├─ SETUP.md             (Detailed setup)
    ├─ INTEGRATION_GUIDE.md (Full integration)
    ├─ web/README.md        (Web UI guide)
    ├─ PROJECT_SUMMARY.md   (Architecture)
    └─ DEVELOPER_GUIDE.md   (Extend system)
```

## 🚀 Choose Your Interface

### Option 1: Command Line (Fast & Simple)
```bash
python3 main.py query "topic"      # Search
python3 main.py quiz "topic"       # Quiz
python3 main.py ask "question"     # Ask AI
python3 main.py chapters           # Browse
python3 main.py status             # Check DB
```

**When to use:** Quick queries, automation, server environments

### Option 2: Web UI (Beautiful & Interactive)
```bash
# Terminal 1: Start backend
python3 web/backend/app.py

# Terminal 2: Start frontend
cd web/frontend && npm start
# Open http://localhost:3000
```

**When to use:** Learning experience, quizzes, classroom settings

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] `python3 test_setup.py` shows all ✓
- [ ] `python3 main.py status` shows documents > 0
- [ ] `python3 main.py query "test"` returns results
- [ ] Web UI loads at http://localhost:3000 (if started)

## 📚 Available Subjects

The system includes content for:

1. **English** - Literature & Language
2. **Mathematics** - Algebra, Geometry, etc.
3. **General Science** - Biology, Physics, Chemistry
4. **Marathi** - Indian regional language
5. **Geography** - World & regional geography
6. **History & Culture** - Historical events
7. **Sanskrit** - Classical language

## 🎓 Educational Features

### 🔍 Smart Search
```bash
python3 main.py query "photosynthesis"
# Returns: 5+ relevant chapters with similarity scores
```

### 🎯 Quiz Generation
```bash
python3 main.py quiz "Newton's laws" --difficulty hard --num-questions 10
# Returns: 10 questions with multiple choices & explanations
```

### 💡 AI Tutor
```bash
python3 main.py ask "How does mitochondria work?"
# Returns: Detailed explanation using course materials
```

### 📊 Dashboard
Via Web UI: See database status, available chapters, topics

## 🔑 Get Your API Key

1. Visit: https://ai.google.dev/gemini-api/docs/api-key
2. Sign in with Google
3. Click "Create API Key"
4. Copy and paste into `.env`

**⚠️ IMPORTANT:** Never share your API key!

## ⚙️ System Requirements

- Python 3.8+ (use `python3 --version` to check)
- Node.js 14+ (for web UI - use `node --version`)
- 500 MB disk space
- Internet connection
- 1 GB RAM minimum

## 🐛 Troubleshooting

### "GEMINI_API_KEY not set"
```bash
# Fix: Add your API key to .env
echo "GEMINI_API_KEY=your_key_here" >> .env
```

### "No module named 'chromadb'"
```bash
# Fix: Install dependencies
python3 -m pip install -r requirements.txt
```

### "Connection refused 5000"
```bash
# Fix: Start backend
python3 web/backend/app.py
```

### "Module not found" errors
```bash
# Fix: Add to Python path
export PYTHONPATH=/Users/umeshbhagvanpatil/POC/LearnEasy:$PYTHONPATH
```

## 📊 Quick Reference

| Task | Command |
|------|---------|
| Search notes | `python3 main.py query "topic"` |
| Generate quiz | `python3 main.py quiz "topic"` |
| Ask question | `python3 main.py ask "question"` |
| View chapters | `python3 main.py chapters` |
| Database info | `python3 main.py status` |
| Reset DB | `python3 main.py reset` |

## 🎯 Next Steps

1. ✅ Setup complete? → Try: `python3 main.py query "photosynthesis"`
2. ✅ CLI working? → Try: `python3 main.py quiz "any topic"`
3. ✅ Ready for Web UI? → Start servers and visit http://localhost:3000
4. ✅ Ready to extend? → Read `DEVELOPER_GUIDE.md`

## 📞 Help & Support

- **Setup Issues?** → See `SETUP.md`
- **Want Quick Start?** → See `QUICKSTART.md`
- **Full Documentation?** → See `README.md`
- **Integration Help?** → See `INTEGRATION_GUIDE.md`
- **Development?** → See `DEVELOPER_GUIDE.md`

## 🚀 Ready?

```bash
# Get started right now!
python3 main.py setup
python3 main.py query "your favorite subject"
```

---

**Questions?** Check the guides above or read through the documentation files.

**Happy Learning! 🎓**
