from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from docx import Document
from pypdf import PdfReader


@dataclass
class ParsedDocument:
    text: str
    warnings: list[str]
    source: str
    filename: str | None = None


def normalize_text(text: str) -> str:
    lines = [line.strip() for line in text.replace("\r", "\n").split("\n")]
    cleaned = "\n".join(line for line in lines if line)
    return cleaned.strip()


def parse_text_payload(text: str, source: str) -> ParsedDocument:
    normalized = normalize_text(text)
    warnings = []
    if len(normalized) < 60:
        warnings.append(f"{source} text is very short; analysis confidence may be lower.")
    return ParsedDocument(text=normalized, warnings=warnings, source=source)


def parse_uploaded_file(filename: str, content: bytes, source: str) -> ParsedDocument:
    suffix = Path(filename).suffix.lower()
    warnings: list[str] = []
    if suffix == ".txt":
        text = content.decode("utf-8", errors="ignore")
        return ParsedDocument(
            text=normalize_text(text),
            warnings=warnings,
            source=source,
            filename=filename,
        )
    if suffix == ".pdf":
        try:
            reader = PdfReader(BytesIO(content))
            pages = [page.extract_text() or "" for page in reader.pages]
            text = normalize_text("\n".join(pages))
            if not text:
                warnings.append("PDF parsing returned limited text. Paste the content for the best result.")
            return ParsedDocument(text=text, warnings=warnings, source=source, filename=filename)
        except Exception as exc:  # pragma: no cover - defensive
            raise ValueError(
                "Unable to parse PDF. Use paste-text fallback or a TXT/DOCX file."
            ) from exc
    if suffix == ".docx":
        try:
            document = Document(BytesIO(content))
            text = normalize_text("\n".join(p.text for p in document.paragraphs))
            return ParsedDocument(text=text, warnings=warnings, source=source, filename=filename)
        except Exception as exc:  # pragma: no cover - defensive
            raise ValueError(
                "Unable to parse DOCX. Use paste-text fallback or a TXT file."
            ) from exc
    raise ValueError("Unsupported file type. Upload PDF, DOCX, or TXT, or paste text directly.")
