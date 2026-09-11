"""Document chunking strategies for optimal embedding"""
import re
from typing import List, Tuple, Dict, Any
from config import Config

_FRONT_MATTER_MARKERS = (
    "permission is granted",
    "standard eight",
    "maharashtra state bureau",
    "the constitution of india",
    "fundamental duties",
)


class DocumentChunker:
    @staticmethod
    def chunk_markdown(content: str, chunk_size: int = None, overlap: int = None) -> List[Dict[str, Any]]:
        """
        Intelligently chunk markdown content while preserving structure and metadata.
        Returns list of dicts with 'text' and 'chapter' keys.
        """
        if chunk_size is None:
            chunk_size = Config.CHUNK_SIZE
        if overlap is None:
            overlap = Config.CHUNK_OVERLAP

        content = DocumentChunker._prepare_content(content)
        chapter_boundaries = DocumentChunker._extract_chapter_boundaries(content)

        def get_chapter_for_position(pos: int) -> str:
            for boundary_pos, boundary_title in reversed(chapter_boundaries):
                if pos >= boundary_pos:
                    return boundary_title
            return "General"

        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = ""
        chunk_start_pos = 0
        current_pos = 0

        for para in paragraphs:
            para_with_break = para + "\n\n"
            if len(current_chunk) > 0 and len(current_chunk) + len(para_with_break) >= chunk_size:
                if current_chunk.strip():
                    chunks.append({
                        "text": current_chunk.strip(),
                        "chapter": get_chapter_for_position(chunk_start_pos),
                    })
                if overlap > 0 and len(current_chunk) > overlap:
                    overlap_text = current_chunk[-overlap:]
                    chunk_start_pos = max(0, current_pos - overlap)
                    current_chunk = overlap_text.lstrip() + para_with_break
                else:
                    current_chunk = para_with_break
                    chunk_start_pos = current_pos
            else:
                if not current_chunk:
                    chunk_start_pos = current_pos
                current_chunk += para_with_break

            current_pos += len(para_with_break)

        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "chapter": get_chapter_for_position(chunk_start_pos),
            })

        return chunks

    @staticmethod
    def _prepare_content(content: str) -> str:
        content = content.replace("\x0c", "\n")
        if content.startswith("---"):
            end = content.find("\n---", 3)
            if end != -1:
                content = content[end + 4 :]
        content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)
        full_text_marker = "## Full textbook text"
        idx = content.find(full_text_marker)
        if idx != -1:
            content = content[idx + len(full_text_marker) :]
        lesson = re.search(r"^#\s+.+$", content, re.MULTILINE)
        if lesson:
            content = content[lesson.start() :]
        else:
            boundaries = DocumentChunker._extract_chapter_boundaries(content)
            if boundaries and boundaries[0][0] > 400:
                content = content[boundaries[0][0] :]
            else:
                head = content[:3500].lower()
                if any(marker in head for marker in _FRONT_MATTER_MARKERS):
                    cut = 2500
                    for start_marker in ("Let's recall", "Let us learn", "Can you recall", "1.1 "):
                        found = content.find(start_marker)
                        if found != -1 and found < 12000:
                            cut = min(cut, found) if cut != 2500 else found
                            if found >= 400:
                                content = content[found:]
                                break
                    else:
                        if len(content) > cut:
                            content = content[cut:]
        content = re.sub(r"\n{4,}", "\n\n\n", content)
        return content.strip()

    @staticmethod
    def _extract_chapter_boundaries(content: str) -> List[Tuple[int, str]]:
        """Extract chapter boundaries and names from content"""
        h1_boundaries = []
        for m in re.finditer(r"^#\s+(.+?)\s*$", content, re.MULTILINE):
            title = m.group(1).strip()
            lowered = title.lower()
            if "standard eight" in lowered:
                continue
            if lowered.startswith(("about this file", "document metadata", "full textbook")):
                continue
            if len(title) < 2 or len(title) > 160:
                continue
            h1_boundaries.append((m.start(), title))
        if h1_boundaries:
            return h1_boundaries

        boundaries = []
        contents_start = content.find("Contents")
        contents_end = 0
        if contents_start >= 0 and contents_start < 8000:
            contents_end = contents_start + 2000
            match = re.search(
                r"\n(?=[A-Z]{2,}|#{1,3}|\n\n[A-Z][A-Za-z]{10,})",
                content[contents_start:],
            )
            if match:
                contents_end = contents_start + match.start()

        for m in re.finditer(r"^(\d+\.\d+)\s+([A-Z][A-Za-z\s\-\&']+)$", content, re.MULTILINE):
            pos = m.start()
            if pos < contents_end:
                continue
            title = m.group(2).strip()
            text_before = content[max(0, pos - 100):pos]
            lines_before = text_before.split("\n")[-2:]
            is_indented = any(
                line.startswith(("  ", "\t", "-", "•", "◆", "("))
                for line in lines_before
                if line.strip()
            )
            looks_like_lesson = len(title) < 100 and not any(
                marker in title for marker in ["(a)", "(b)", "(c)", "Read", "Write", "Discuss", "Think"]
            )
            if len(title) >= 4 and not is_indented and looks_like_lesson:
                boundaries.append((pos, f"{m.group(1)} {title}"))

        if len(boundaries) == 0:
            for m in re.finditer(
                r"^(\d+)\.\s+([A-Z][A-Za-z\s\-\&']+?)(?:\s+and.*)?$",
                content,
                re.MULTILINE,
            ):
                pos = m.start()
                if pos < contents_end:
                    continue
                title = m.group(2).strip()
                text_before = content[max(0, pos - 100):pos]
                lines_before = text_before.split("\n")[-2:]
                is_indented = any(line.startswith(("  ", "\t")) for line in lines_before if line.strip())
                if len(title) >= 4 and not is_indented:
                    boundaries.append((pos, f"{m.group(1)}. {title}"))

        if len(boundaries) == 0:
            for m in re.finditer(r"^#{1,3}\s+(.+?)$", content, re.MULTILINE):
                pos = m.start()
                if pos < contents_end:
                    continue
                boundaries.append((pos, m.group(1).strip()))

        boundaries.sort(key=lambda x: x[0])
        return boundaries

    @staticmethod
    def add_metadata(chunk: Dict[str, Any], filename: str) -> Tuple[str, dict]:
        metadata = {
            "source": filename,
            "chapter": chunk.get("chapter", "General"),
            "section": chunk.get("chapter", "General"),
        }
        return chunk.get("text", ""), metadata
