from __future__ import annotations

import io
import os
from pathlib import Path

from agent.models import Evidence
from ocr.base import OCROutput, OCRProvider


def _line_evidence(text: str, source: str, confidence: float) -> list[Evidence]:
    return [
        Evidence(f"ev-{index:04d}", source, line, page=1, confidence=confidence)
        for index, line in enumerate(text.splitlines(), start=1)
        if line.strip()
    ]


class SyntheticOCRProvider(OCRProvider):
    """Test-only provider for anonymous UTF-8 fixtures."""

    def extract(self, content: bytes, filename: str) -> OCROutput:
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise RuntimeError("SYNTHETIC_OCR_EXPECTED_UTF8_FIXTURE") from exc
        return OCROutput(text, _line_evidence(text, f"synthetic:{filename}", 1.0), "synthetic")


class EmbeddedPdfOCRProvider(OCRProvider):
    def extract(self, content: bytes, filename: str) -> OCROutput:
        if Path(filename).suffix.lower() != ".pdf":
            raise RuntimeError("EMBEDDED_PDF_PROVIDER_REQUIRES_PDF")
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(content))
        page_texts = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(page_texts)
        if not text.strip():
            raise RuntimeError("PDF_HAS_NO_EMBEDDED_TEXT; configure an image OCR provider")
        return OCROutput(text, _line_evidence(text, f"pdf:{filename}", 0.95), "embedded_pdf")


class TesseractOCRProvider(OCRProvider):
    def __init__(self, language: str = "eng") -> None:
        self.language = language

    def extract(self, content: bytes, filename: str) -> OCROutput:
        if Path(filename).suffix.lower() == ".pdf":
            raise RuntimeError("SCANNED_PDF_RENDERER_NOT_CONFIGURED")
        try:
            import pytesseract
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError("TESSERACT_PYTHON_DEPENDENCY_MISSING") from exc
        try:
            image = Image.open(io.BytesIO(content))
            text = pytesseract.image_to_string(image, lang=self.language)
        except Exception as exc:
            raise RuntimeError(f"TESSERACT_OCR_FAILED: {exc}") from exc
        return OCROutput(text, _line_evidence(text, f"tesseract:{filename}", 0.80), "tesseract")


def provider_from_env() -> OCRProvider:
    name = os.getenv("OCR_PROVIDER", "auto").lower()
    if name == "synthetic":
        return SyntheticOCRProvider()
    if name == "embedded_pdf":
        return EmbeddedPdfOCRProvider()
    if name == "tesseract":
        return TesseractOCRProvider(os.getenv("OCR_LANGUAGE", "eng"))
    if name != "auto":
        raise RuntimeError(f"Unknown OCR_PROVIDER: {name}")
    return AutoOCRProvider()


class AutoOCRProvider(OCRProvider):
    def extract(self, content: bytes, filename: str) -> OCROutput:
        if Path(filename).suffix.lower() == ".pdf":
            return EmbeddedPdfOCRProvider().extract(content, filename)
        return TesseractOCRProvider(os.getenv("OCR_LANGUAGE", "eng")).extract(content, filename)

