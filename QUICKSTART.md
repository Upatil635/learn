# LearnEasy - Quick Start Guide

Get started with LearnEasy in just **3 minutes**!

## 1️⃣ Get API Key (1 minute)

```bash
# Open in browser:
https://ai.google.dev/gemini-api/docs/api-key

# Click "Create API Key" and copy it
```

## 2️⃣ Configure Environment (30 seconds)

```bash
# Edit .env file and add:
GEMINI_API_KEY=your_key_here
```

## 3️⃣ Initialize System (1-2 minutes)

```bash
python3 main.py setup
```

**That's it!** ✓ Your system is ready.

---

## 📚 Usage Examples

### Search for Notes
```bash
python3 main.py query "photosynthesis"
python3 main.py query "photosynthesis" --top-k 10
```

### Generate Quiz
```bash
python3 main.py quiz "Newton's laws"
python3 main.py quiz "evolution" --difficulty hard --num-questions 10
```

### Ask Questions
```bash
python3 main.py ask "What is photosynthesis?"
python3 main.py ask "Explain evolution" --subject "General Science"
```

### View Information
```bash
python3 main.py status          # Database info
python3 main.py chapters        # List chapters
python3 main.py chapters -s Math  # Chapters in Math
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| "GEMINI_API_KEY not set" | Add to `.env`: `GEMINI_API_KEY=your_key` |
| "No module named 'chromadb'" | Run: `python3 -m pip install -r requirements.txt` |
| "Connection error" | Check internet connection and API key validity |
| "No documents found" | Run: `python3 main.py setup` again |

---

## 📖 Full Documentation

- **Setup Guide:** See [SETUP.md](SETUP.md)
- **Full Features:** See [README.md](README.md)
- **CLI Reference:** `python3 main.py --help`

---

## ✨ What's Next?

1. ✅ Setup complete
2. 📚 Try searching: `python3 main.py query "your topic"`
3. 🎯 Generate quizzes: `python3 main.py quiz "your topic"`
4. 💡 Ask questions: `python3 main.py ask "your question"`
5. 🌐 Use web UI (coming soon!)

---

**Happy Learning! 🚀**
