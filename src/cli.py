"""Command-line interface for LearnEasy"""
import click
import json
from typing import Optional
from colorama import Fore, Style, init
from src.ingester import DocumentIngester
from src.rag_retriever import RAGRetriever
from src.gemini_handler import GeminiHandler
from src.vector_db import get_vector_db
from src.user_store import UserStore
from src.ai_cache import AiCache

init(autoreset=True)


@click.group()
def cli():
    """LearnEasy - AI-powered learning platform with RAG and quiz generation"""
    pass


@cli.command()
def setup():
    """Initialize and ingest all markdown files into vector database"""
    click.echo(f"\n{Fore.CYAN}{'='*60}")
    click.echo(f"{Fore.CYAN}LearnEasy Setup - Ingesting Documents{Style.RESET_ALL}")
    click.echo(f"{Fore.CYAN}{'='*60}\n")

    try:
        ingester = DocumentIngester()
        click.echo(f"{Fore.YELLOW}Clearing and re-ingesting markdown files...")
        ingester.reingest_documents()

        click.echo(f"\n{Fore.GREEN}✓ Setup complete!{Style.RESET_ALL}\n")

    except Exception as e:
        click.echo(f"{Fore.RED}✗ Setup failed: {e}{Style.RESET_ALL}")


@cli.command()
@click.option('--subject', '-s', type=str, help='Filter by subject (English, Math, etc.)')
@click.option('--top-k', '-k', type=int, default=5, help='Number of results to retrieve')
@click.argument('query', type=str)
def query(query: str, subject: Optional[str], top_k: int):
    """Query the knowledge base to fetch relevant notes"""
    click.echo(f"\n{Fore.CYAN}{'='*60}")
    click.echo(f"{Fore.CYAN}RAG Query{Style.RESET_ALL}")
    click.echo(f"{Fore.CYAN}{'='*60}\n")

    try:
        retriever = RAGRetriever()
        results = retriever.retrieve_context(query, top_k=top_k, subject_filter=subject)

        if results.get("error"):
            click.echo(f"{Fore.RED}✗ Error: {results['error']}{Style.RESET_ALL}")
            return

        click.echo(f"{Fore.YELLOW}Query:{Style.RESET_ALL} {query}")
        click.echo(f"{Fore.YELLOW}Retrieved:{Style.RESET_ALL} {results['total_retrieved']} documents\n")

        for i, doc in enumerate(results['retrieved_documents'], 1):
            click.echo(f"{Fore.GREEN}{i}. {doc['chapter']} (Similarity: {doc['similarity_score']:.2%}){Style.RESET_ALL}")
            click.echo(f"   Source: {doc['source']}")
            click.echo(f"   {doc['content'][:200]}...\n")

    except Exception as e:
        click.echo(f"{Fore.RED}✗ Query failed: {e}{Style.RESET_ALL}")


@cli.command()
@click.option('--difficulty', '-d', type=click.Choice(['easy', 'medium', 'hard']), default='medium')
@click.option('--num-questions', '-n', type=int, default=5)
@click.option('--subject', '-s', type=str, help='Subject to generate quiz from')
@click.argument('topic', type=str, required=False)
def quiz(topic: Optional[str], difficulty: str, num_questions: int, subject: Optional[str]):
    """Generate a quiz on a specific topic"""
    click.echo(f"\n{Fore.CYAN}{'='*60}")
    click.echo(f"{Fore.CYAN}Quiz Generation{Style.RESET_ALL}")
    click.echo(f"{Fore.CYAN}{'='*60}\n")

    try:
        retriever = RAGRetriever()
        gemini = GeminiHandler()
        cache = AiCache()
        cache_key = f"{topic}|{difficulty}|{num_questions}|{subject or ''}"
        hit = cache.get(AiCache.KIND_QUIZ, subject or "", "", cache_key)
        if hit:
            click.echo(f"{Fore.GREEN}Using saved quiz{Style.RESET_ALL}\n")
            quiz_data = hit.get("quiz", [])
        else:
            if topic:
                click.echo(f"{Fore.YELLOW}Searching for: {topic}{Style.RESET_ALL}")
                results = retriever.retrieve_context(topic, subject_filter=subject)
                context = results.get("context", "")
            else:
                click.echo(f"{Fore.YELLOW}No topic specified. Use --help for usage.{Style.RESET_ALL}")
                return

            if not context:
                click.echo(f"{Fore.RED}✗ No relevant content found for '{topic}'{Style.RESET_ALL}")
                return

            click.echo(f"{Fore.YELLOW}Generating {num_questions} {difficulty} questions...{Style.RESET_ALL}\n")
            quiz_result = gemini.generate_quiz(context, num_questions, difficulty)

            if not quiz_result.get("success"):
                click.echo(f"{Fore.RED}✗ Failed to generate quiz: {quiz_result.get('error')}{Style.RESET_ALL}")
                return
            quiz_data = quiz_result.get("quiz", [])
            cache.put(
                AiCache.KIND_QUIZ,
                subject or "",
                {"quiz": quiz_data, "num_questions": len(quiz_data)},
                prompt_key=cache_key,
            )

        for i, q in enumerate(quiz_data, 1):
            click.echo(f"{Fore.GREEN}Q{i}: {q.get('question', 'N/A')}{Style.RESET_ALL}")
            for j, option in enumerate(q.get('options', []), 1):
                prefix = f"{Fore.YELLOW}→{Style.RESET_ALL}" if j - 1 == q.get('correct_answer') else " "
                click.echo(f"  {prefix} {chr(64+j)}) {option}")
            click.echo(f"{Fore.CYAN}Explanation: {q.get('explanation', 'N/A')}{Style.RESET_ALL}\n")

    except Exception as e:
        click.echo(f"{Fore.RED}✗ Quiz generation failed: {e}{Style.RESET_ALL}")


@cli.command()
@click.argument('question', type=str)
@click.option('--subject', '-s', type=str, help='Filter context by subject')
def ask(question: str, subject: Optional[str]):
    """Ask a question and get an AI-powered answer"""
    click.echo(f"\n{Fore.CYAN}{'='*60}")
    click.echo(f"{Fore.CYAN}Ask a Question{Style.RESET_ALL}")
    click.echo(f"{Fore.CYAN}{'='*60}\n")

    try:
        retriever = RAGRetriever()
        gemini = GeminiHandler()
        cache = AiCache()
        hit = cache.get(AiCache.KIND_ASK, subject or "", "", question)
        if hit:
            click.echo(f"{Fore.GREEN}Using saved answer{Style.RESET_ALL}\n")
            click.echo(f"{Fore.YELLOW}Question:{Style.RESET_ALL} {question}\n")
            click.echo(f"{Fore.GREEN}Answer:{Style.RESET_ALL}\n{hit.get('answer', '')}\n")
            return

        click.echo(f"{Fore.YELLOW}Searching for relevant context...{Style.RESET_ALL}")
        results = retriever.retrieve_context(question, subject_filter=subject)
        context = results.get("context", "")

        if not context:
            click.echo(f"{Fore.YELLOW}No context found. Generating general answer...{Style.RESET_ALL}\n")

        click.echo(f"{Fore.YELLOW}Question:{Style.RESET_ALL} {question}\n")
        answer_result = gemini.answer_question(context, question)

        if not answer_result.get("success"):
            click.echo(f"{Fore.RED}✗ Failed to answer: {answer_result.get('error')}{Style.RESET_ALL}")
            return

        cache.put(
            AiCache.KIND_ASK,
            subject or "",
            {"answer": answer_result["answer"], "sources": results.get("total_retrieved", 0)},
            prompt_key=question,
        )
        click.echo(f"{Fore.GREEN}Answer:{Style.RESET_ALL}\n{answer_result['answer']}\n")

    except Exception as e:
        click.echo(f"{Fore.RED}✗ Failed to answer question: {e}{Style.RESET_ALL}")


@cli.command()
def status():
    """Show database status and statistics"""
    click.echo(f"\n{Fore.CYAN}{'='*60}")
    click.echo(f"{Fore.CYAN}Database Status{Style.RESET_ALL}")
    click.echo(f"{Fore.CYAN}{'='*60}\n")

    try:
        vector_db = get_vector_db()
        stats = vector_db.get_collection_stats()

        click.echo(f"{Fore.YELLOW}Collection Name:{Style.RESET_ALL} {stats['collection_name']}")
        click.echo(f"{Fore.YELLOW}Total Documents:{Style.RESET_ALL} {stats['total_documents']}")
        click.echo(f"{Fore.YELLOW}Database Path:{Style.RESET_ALL} {stats['path']}\n")

    except Exception as e:
        click.echo(f"{Fore.RED}✗ Failed to get status: {e}{Style.RESET_ALL}")


@cli.command()
def reset():
    """Reset and clear the vector database"""
    if click.confirm(f"{Fore.YELLOW}Are you sure you want to reset the database?{Style.RESET_ALL}"):
        try:
            vector_db = get_vector_db()
            vector_db.clear_collection()
            click.echo(f"{Fore.GREEN}✓ Database reset successfully{Style.RESET_ALL}\n")
        except Exception as e:
            click.echo(f"{Fore.RED}✗ Reset failed: {e}{Style.RESET_ALL}")


@cli.command()
@click.option('--subject', '-s', type=str)
def chapters(subject: Optional[str]):
    """List available chapters by subject"""
    click.echo(f"\n{Fore.CYAN}{'='*60}")
    click.echo(f"{Fore.CYAN}Available Chapters{Style.RESET_ALL}")
    click.echo(f"{Fore.CYAN}{'='*60}\n")

    try:
        vector_db = get_vector_db()
        results = vector_db.collection.get(limit=50000)

        chapters_by_subject = {}
        for metadata in results.get("metadatas", []):
            subj = metadata.get("subject", "Unknown")
            chapter = metadata.get("chapter", "Unknown")

            if subj not in chapters_by_subject:
                chapters_by_subject[subj] = set()
            chapters_by_subject[subj].add(chapter)

        for subj in sorted(chapters_by_subject.keys()):
            if subject is None or subject.lower() in subj.lower():
                click.echo(f"{Fore.YELLOW}{subj}:{Style.RESET_ALL}")
                for chapter in sorted(chapters_by_subject[subj]):
                    click.echo(f"  • {chapter}")
                click.echo()

    except Exception as e:
        click.echo(f"{Fore.RED}✗ Failed to list chapters: {e}{Style.RESET_ALL}")


@cli.command()
@click.argument("username")
def useradd(username: str):
    """Create a seeded student account (no public registration)."""
    password = click.prompt("Password", hide_input=True, confirmation_prompt=True)
    try:
        user = UserStore().create_user(username, password)
        click.echo(f"{Fore.GREEN}✓ Created user '{user['username']}'{Style.RESET_ALL}")
    except ValueError as e:
        click.echo(f"{Fore.RED}✗ {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    cli()
