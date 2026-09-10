#!/usr/bin/env python3
"""Test script to verify LearnEasy setup"""
import sys
import os
from pathlib import Path

def print_status(status, message):
    symbol = "✓" if status else "✗"
    color = "\033[92m" if status else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{symbol} {message}{reset}")

def main():
    print("\n" + "="*60)
    print("LearnEasy Setup Verification")
    print("="*60 + "\n")

    all_good = True

    # 1. Check Python version
    print("1. Checking Python version...")
    if sys.version_info >= (3, 8):
        print_status(True, f"Python {sys.version_info.major}.{sys.version_info.minor}")
    else:
        print_status(False, f"Python {sys.version_info.major}.{sys.version_info.minor} (need 3.8+)")
        all_good = False

    # 2. Check dependencies
    print("\n2. Checking dependencies...")
    dependencies = [
        ("chromadb", "ChromaDB"),
        ("click", "Click"),
        ("colorama", "Colorama"),
        ("dotenv", "python-dotenv"),
    ]

    for module, name in dependencies:
        try:
            __import__(module)
            print_status(True, f"{name}")
        except ImportError:
            print_status(False, f"{name}")
            all_good = False

    # 3. Check .env file
    print("\n3. Checking configuration...")
    env_exists = Path(".env").exists()
    print_status(env_exists, ".env file exists")
    if env_exists:
        with open(".env") as f:
            content = f.read()
            has_key = "GEMINI_API_KEY" in content
            key_set = "GEMINI_API_KEY=" in content and "your_gemini_api_key_here" not in content
            print_status(has_key, "GEMINI_API_KEY is configured")
            if has_key and not key_set:
                print_status(False, "GEMINI_API_KEY is set to default (needs actual key)")
                all_good = False

    # 4. Check markdown files
    print("\n4. Checking markdown files...")
    pdf_dir = Path("PDFs/8th")
    if pdf_dir.exists():
        md_files = list(pdf_dir.glob("*.md"))
        print_status(len(md_files) > 0, f"Found {len(md_files)} markdown files")
        for md_file in sorted(md_files):
            print(f"  • {md_file.name}")
    else:
        print_status(False, "PDFs/8th directory not found")
        all_good = False

    # 5. Check project structure
    print("\n5. Checking project structure...")
    dirs_to_check = [
        ("src", "Source code"),
        ("config", "Configuration"),
        ("data", "Data directory (will be created on setup)")
    ]

    for dir_name, desc in dirs_to_check:
        exists = Path(dir_name).exists()
        if dir_name == "data":
            print_status(True, f"{desc} (optional)")
        else:
            print_status(exists, f"{desc} ({dir_name}/)")
            if not exists:
                all_good = False

    # 6. Test imports
    print("\n6. Testing module imports...")
    try:
        from config import Config
        print_status(True, "config.Config")
    except ImportError as e:
        print_status(False, f"config.Config: {e}")
        all_good = False

    try:
        from src.chunker import DocumentChunker
        print_status(True, "src.chunker.DocumentChunker")
    except ImportError as e:
        print_status(False, f"src.chunker: {e}")
        all_good = False

    try:
        from src.vector_db import VectorDB
        print_status(True, "src.vector_db.VectorDB")
    except ImportError as e:
        print_status(False, f"src.vector_db: {e}")
        all_good = False

    # Summary
    print("\n" + "="*60)
    if all_good:
        print("\033[92m✓ All checks passed! Ready to run:\033[0m")
        print("  python3 main.py setup\n")
    else:
        print("\033[91m✗ Some checks failed. Please fix issues above.\033[0m\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
