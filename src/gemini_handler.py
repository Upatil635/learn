"""LLM handler: LM Studio / OpenAI-compatible APIs, plus optional Gemini."""
import json
import os
import re
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

from config import Config


class LLMHandler:
    def __init__(self):
        Config.validate_llm()
        self._gemini_client = None

    @property
    def provider(self) -> str:
        return Config.llm_provider()

    @property
    def model_name(self) -> str:
        return Config.llm_model()

    def _generate(self, prompt: str, json_mode: bool = False) -> str:
        if self.provider == "gemini":
            return self._generate_gemini(prompt, json_mode=json_mode)
        return self._generate_openai(prompt, json_mode=json_mode)

    def _generate_openai(self, prompt: str, json_mode: bool = False) -> str:
        base = Config.llm_base_url().rstrip("/")
        url = f"{base}/chat/completions"
        messages = [{"role": "user", "content": prompt}]
        if json_mode:
            messages.insert(
                0,
                {
                    "role": "system",
                    "content": "Reply with valid JSON only. No markdown fences or extra text.",
                },
            )
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.3,
        }
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {Config.llm_api_key()}",
        }
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=Config.llm_timeout_seconds()) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:800]
            raise RuntimeError(f"LLM HTTP {e.code}: {detail}") from e
        choices = data.get("choices") or []
        if not choices:
            raise RuntimeError("LLM returned no choices")
        message = choices[0].get("message") or {}
        return (message.get("content") or "").strip()

    def _generate_gemini(self, prompt: str, json_mode: bool = False) -> str:
        os.environ.pop("GOOGLE_GENAI_USE_VERTEXAI", None)
        if self._gemini_client is None:
            from google import genai
            from google.genai import types as genai_types

            self._gemini_client = genai.Client(api_key=Config.gemini_api_key())
            self._genai_types = genai_types
        config = None
        if json_mode:
            config = self._genai_types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        response = self._gemini_client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=config,
        )
        return (response.text or "").strip()

    @staticmethod
    def _parse_json(response_text: str) -> Dict[str, Any]:
        text = response_text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        if text.startswith("{"):
            return json.loads(text)
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
        raise ValueError("Could not parse JSON from model response")

    def generate_quiz(self, context: str, num_questions: int = 5, difficulty: str = "medium") -> Dict[str, Any]:
        prompt = f"""Based on the following educational content, generate {num_questions} multiple-choice questions.

Difficulty Level: {difficulty}

Content:
{context}

Return JSON:
{{
    "quiz": [
        {{
            "question": "Question text?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": 0,
            "explanation": "Explanation of the correct answer"
        }}
    ]
}}

Rules:
1. Questions must be based on the content
2. correct_answer is the 0-based index of the right option
3. Include explanations
4. Return ONLY valid JSON"""

        try:
            quiz_data = self._parse_json(self._generate(prompt, json_mode=True))
            quiz = quiz_data.get("quiz", [])
            return {"success": True, "quiz": quiz, "num_questions": len(quiz)}
        except json.JSONDecodeError as e:
            print(f"✗ JSON parsing error: {e}")
            return {"success": False, "error": f"JSON parsing error: {e}"}
        except Exception as e:
            print(f"✗ Error generating quiz: {e}")
            return {"success": False, "error": str(e)}

    def generate_learning_pack(self, context: str, chapter: str) -> Dict[str, Any]:
        prompt = f"""You are a tutor for 8th-grade students in Maharashtra.
Using ONLY the chapter content below, create a study pack for "{chapter}".

Content:
{context}

Return JSON:
{{
  "summary": "A student-friendly summary of the chapter (paragraphs, not bullets only)",
  "eli5": "Explain the chapter as if to a curious 11-year-old, using the content",
  "mnemonics": ["memory trick 1", "memory trick 2"],
  "examples": ["real-life example 1", "real-life example 2"],
  "key_takeaways": ["takeaway 1", "takeaway 2"],
  "flashcards": [
    {{"question": "short question", "answer": "short answer"}}
  ]
}}

Rules:
- Invent mnemonics and flashcards from the content; do not copy copyright pages
- 3-5 mnemonics, 3-5 examples, 5 takeaways, 6 flashcards
- If the content is thin, say so inside the fields instead of making up textbook facts
- Return ONLY valid JSON"""

        try:
            data = self._parse_json(self._generate(prompt, json_mode=True))
            return {
                "success": True,
                "summary": data.get("summary", ""),
                "eli5": data.get("eli5", ""),
                "mnemonics": data.get("mnemonics") or [],
                "examples": data.get("examples") or [],
                "key_takeaways": data.get("key_takeaways") or [],
                "flashcards": data.get("flashcards") or [],
            }
        except Exception as e:
            print(f"✗ Error generating learning pack: {e}")
            return {"success": False, "error": str(e)}

    def answer_question(self, context: str, question: str) -> Dict[str, Any]:
        prompt = f"""You are an educational assistant helping students understand their studies.

Using the following educational content as reference:
{context}

Answer the student's question comprehensively:
Question: {question}

Please provide:
1. A clear and concise answer
2. Key concepts explained
3. Real-world examples if applicable
4. Any important points to remember

If the content does not cover the question, say so and answer only what you can from the content."""

        try:
            answer = self._generate(prompt)
            return {"success": True, "question": question, "answer": answer}
        except Exception as e:
            print(f"✗ Error answering question: {e}")
            return {"success": False, "error": str(e)}

    def summarize_content(self, context: str) -> Dict[str, Any]:
        prompt = f"""Provide a concise summary of the following educational content.
The summary should:
1. Cover the main points
2. Be suitable for students
3. Include key definitions
4. Highlight important concepts

Content:
{context}

Summary:"""
        try:
            summary = self._generate(prompt)
            return {"success": True, "summary": summary}
        except Exception as e:
            print(f"✗ Error summarizing content: {e}")
            return {"success": False, "error": str(e)}

    def explain_concept(
        self, concept: str, difficulty: str = "intermediate", context: Optional[str] = None
    ) -> Dict[str, Any]:
        context_block = f"\nUse this chapter content as the source of truth:\n{context}\n" if context else ""
        prompt = f"""Explain the concept of "{concept}" in detail.
{context_block}
Difficulty Level: {difficulty}

Please provide:
1. Definition
2. Key characteristics
3. Related concepts
4. Examples
5. Common misconceptions
6. Study tips

Keep the explanation at a {difficulty} level appropriate for students."""
        try:
            explanation = self._generate(prompt)
            return {"success": True, "concept": concept, "explanation": explanation}
        except Exception as e:
            print(f"✗ Error explaining concept: {e}")
            return {"success": False, "error": str(e)}


GeminiHandler = LLMHandler
