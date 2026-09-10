# LearnEasy Setup Instructions

## Step 1: Get Your Gemini API Key

1. Visit: https://ai.google.dev/gemini-api/docs/api-key
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

## Step 2: Create .env File

```bash
# Copy the example file
cp .env.example .env
```

## Step 3: Configure .env

Edit `.env` and add your API key:

```env
GEMINI_API_KEY=your_api_key_here
```

**⚠️ Important Security Notes:**
- Never commit `.env` to git
- Never share your API key publicly
- If exposed, regenerate it immediately at https://ai.google.dev/gemini-api/docs/api-key

## Step 4: Install Dependencies

```bash
python3 -m pip install -r requirements.txt
```

This installs:
- **chromadb**: Vector database (0.5.0+)
- **google-generativeai**: Gemini API client (0.8.0+)
- **langchain**: LLM framework (0.2.0+)
- **langchain-community**: LangChain integrations (0.2.0+)
- **langchain-core**: LangChain core (0.2.0+)
- **click**: CLI framework (8.1.7)
- **colorama**: Colored terminal output (0.4.6)
- **python-dotenv**: Environment variable management (1.0.0)

**Note:** If you see dependency warnings, they're normal. The system is compatible with the latest versions.

## Step 5: Initialize Database

```bash
python main.py setup
```

This will:
- Load all markdown files from `PDFs/8th/`
- Chunk documents intelligently (preserving context)
- Create vector embeddings using ChromaDB
- Store in local database (`data/chroma_db/`)
- Display ingestion progress

Expected output:
```
✓ Loaded english.md
✓ Loaded math.md
...
✓ Ingestion complete! Total documents in DB: 1250+
```

## Step 6: Verify Setup

Check if everything works:

```bash
# View database status
python main.py status

# List available chapters
python main.py chapters
```

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'chromadb'"
**Solution:** Run `pip install -r requirements.txt`

### Issue: "GEMINI_API_KEY not set in .env file"
**Solution:** 
1. Make sure `.env` exists
2. Add your API key to `.env`
3. Save and try again

### Issue: "No documents loaded"
**Solution:**
1. Check if markdown files exist: `ls PDFs/8th/*.md`
2. Ensure files are readable
3. Try setup again: `python main.py setup`

### Issue: "Connection error to Gemini API"
**Solution:**
1. Check internet connection
2. Verify API key is correct
3. Check rate limits at https://ai.google.dev/pricing

## Project Structure After Setup

```
LearnEasy/
├── data/
│   └── chroma_db/          # ← Created after setup
│       ├── chroma.sqlite3
│       ├── collections/
│       └── index/
├── PDFs/8th/
│   ├── english.md          # ← Converted from PDF
│   ├── math.md
│   └── ...
└── ...
```

## Next Steps

Try these commands:

```bash
# Search for notes
python main.py query "photosynthesis"

# Generate a quiz
python main.py quiz "Newton's laws"

# Ask a question
python main.py ask "What is gravity?"
```

## Troubleshooting Command Reference

```bash
# Check vector DB size
du -sh data/chroma_db/

# Verify markdown files
find PDFs/8th -name "*.md" | wc -l

# Test API connection (Python)
python -c "import google.generativeai; print('✓ API installed')"

# View detailed logs
python main.py setup --verbose
```

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | ✅ Yes | - | Google Gemini API key |
| `CHUNK_SIZE` | ❌ No | 1000 | Size of document chunks |
| `CHUNK_OVERLAP` | ❌ No | 200 | Overlap between chunks |
| `TOP_K_RESULTS` | ❌ No | 5 | Number of search results |
| `SIMILARITY_THRESHOLD` | ❌ No | 0.6 | Minimum similarity score |

## Performance Tips

### Faster Initialization
- Start with fewer documents to test: copy some MD files to a separate folder
- Run setup on that folder

### Faster Queries
- Use `--top-k 3` for quicker results
- Filter by `--subject` to narrow search

### Better Results
- Increase `CHUNK_SIZE` to 1500-2000 for better context
- Decrease `CHUNK_OVERLAP` to 100 for more documents

## API Rate Limits

Google Gemini API has:
- 60 requests/minute for free tier
- Check current status: https://ai.google.dev/pricing

If you hit rate limits:
- Wait 60 seconds before retrying
- Consider upgrading to paid tier

## Uninstall & Reset

```bash
# Remove vector database
rm -rf data/chroma_db/

# Remove Python packages
pip uninstall -r requirements.txt -y

# Start fresh
python main.py setup
```

## Need Help?

1. Check README.md for usage guide
2. Run `python main.py --help` for command reference
3. Check logs in terminal output
4. Review error messages carefully

---

**Ready to go!** Start with: `python main.py setup`
