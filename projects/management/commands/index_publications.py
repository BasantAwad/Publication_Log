import os
import re
import uuid
import json
from pathlib import Path
from pypdf import PdfReader
import fitz  # PyMuPDF
from django.conf import settings
from django.core.management.base import BaseCommand


def chunk_text(text: str, size: int, overlap: int):
    """Split text into overlapping chunks for RAG."""
    text = re.sub(r"\s+", " ", text).strip()
    chunks = []
    start = 0
    L = len(text)
    while start < L:
        end = min(L, start + size)
        chunks.append(text[start:end])
        start = end - overlap
        if start < 0:
            start = 0
    return [c for c in chunks if c.strip()]


def pdf_to_text(path: Path) -> str:
    """Extract text from a PDF file with fallback (pypdf → fitz)."""
    text = ""
    try:
        # First try with pypdf
        reader = PdfReader(str(path))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    except Exception as e:
        print(f"   ❌ [pypdf failed] {path}: {e}")

    # If empty or failed → fallback to fitz
    if not text.strip():
        try:
            doc = fitz.open(str(path))
            for page in doc:
                text += page.get_text()
            doc.close()
        except Exception as e:
            print(f"   ❌ [fitz failed] {path}: {e}")
            return ""

    return text


class Command(BaseCommand):
    help = "Build RAG index from Publication Log PDFs"

    def handle(self, *args, **kwargs):
        index_dir = Path(settings.RAG_INDEX_DIR)
        index_dir.mkdir(parents=True, exist_ok=True)

        media_root = Path(settings.MEDIA_ROOT)
        print(f"📂 Scanning PDFs inside: {media_root}")

        pdf_files = list(media_root.rglob("*.pdf"))
        print(f"🔎 Found {len(pdf_files)} PDF(s)")

        processed = 0
        total_chunks = 0

        for pdf in pdf_files:
            print(f"\n➡ Processing: {pdf}")
            doc_id = str(uuid.uuid4())
            title = pdf.stem

            raw = pdf_to_text(pdf)
            print(f"   ➡ Extracted {len(raw)} characters")

            if not raw:
                print("   ⚠ Skipped (empty or unreadable PDF)")
                continue

            parts = chunk_text(raw, settings.RAG_CHUNK_SIZE, settings.RAG_CHUNK_OVERLAP)
            print(f"   ➡ Split into {len(parts)} chunks")

            records = []
            for i, chunk in enumerate(parts):
                cid = f"{doc_id}::chunk::{i}"
                records.append({
                    "id": cid,
                    "doc_id": doc_id,
                    "title": title,
                    "source_path": str(pdf),
                    "published_at": None,  # TODO: extract date if available
                    "text": chunk,
                })

            # Save JSON for this PDF only
            index_file = index_dir / f"{doc_id}.json"
            with open(index_file, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)

            print(f"   💾 Saved {len(records)} chunks → {index_file}")

            processed += 1
            total_chunks += len(records)

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Indexed {processed} PDF(s) into {index_dir}, total {total_chunks} chunks."
        ))
