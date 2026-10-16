
# extract_metadata.py
# Extract metadata from downloaded PDFs and save metadata/papers.json

import os
import re
import json
import fitz  # PyMuPDF

from config import PAPERS_DIR, METADATA_DIR


ARXIV_STAMP = re.compile(
    r"arXiv:(\d{4}\.\d{4,5})(?:v\d+)?\s*\["
)

FILENAME_RE = re.compile(r"^(\d{4})_([a-z]+)_")


def title_from_layout(page):
    """Estimate the paper title using the largest font on page 1."""
    spans = []

    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                text = span["text"].strip()

                if len(text) > 2:
                    spans.append(
                        (round(span["size"], 1), text)
                    )

    if not spans:
        return None

    biggest = max(size for size, _ in spans)

    title_parts = [
        text for size, text in spans
        if size >= biggest - 0.5
    ]

    title = " ".join(title_parts)
    return " ".join(title.split()) or None


def extract_record(category, filename):
    """Read metadata from one local PDF."""
    path = os.path.join(PAPERS_DIR, category, filename)

    match = FILENAME_RE.match(filename)

    year = int(match.group(1)) if match else None
    authors = [match.group(2).title()] if match else []

    title = None
    arxiv_id = None

    try:
        with fitz.open(path) as doc:
            if len(doc) == 0:
                raise ValueError("PDF contains no pages")

            page1 = doc[0]
            page_text = page1.get_text()

            stamp = ARXIV_STAMP.search(page_text)

            if stamp:
                arxiv_id = stamp.group(1)

            title = title_from_layout(page1)

    except Exception as error:
        print(f"WARNING: Could not read {filename}: {error}")

    # Use filename as a fallback if title extraction fails.
    if not title:
        title = os.path.splitext(filename)[0]
        title = re.sub(r"^\d{4}_[a-z]+_", "", title)
        title = title.replace("-", " ").title()

    return {
        "file": filename,
        "category": category,
        "path": f"{category}/{filename}",
        "arxiv_id": arxiv_id,
        "title": title,
        "authors": authors,
        "year": year,
        "source": "local_pdf"
    }


def main():
    records = []

    if not os.path.isdir(PAPERS_DIR):
        print(f"ERROR: Papers directory not found: {PAPERS_DIR}")
        return

    # Read every downloaded PDF without making API requests.
    for category in sorted(os.listdir(PAPERS_DIR)):
        folder = os.path.join(PAPERS_DIR, category)

        if not os.path.isdir(folder):
            continue

        pdf_files = sorted(
            name for name in os.listdir(folder)
            if name.lower().endswith(".pdf")
        )

        for filename in pdf_files:
            print(f"Extracting: {category}/{filename}")

            record = extract_record(category, filename)
            records.append(record)

    # Create the metadata directory.
    os.makedirs(METADATA_DIR, exist_ok=True)

    out_path = os.path.join(METADATA_DIR, "papers.json")

    # Save even when some PDFs could not be read.
    with open(out_path, "w", encoding="utf-8") as file:
        json.dump(
            records,
            file,
            indent=2,
            ensure_ascii=False
        )

    print("\n========== METADATA SUMMARY ==========")
    print(f"PDF records processed: {len(records)}")
    print(f"Metadata saved to: {out_path}")
    print("arXiv API requests: 0")
    print("Metadata extraction completed.")


if __name__ == "__main__":
    main()
