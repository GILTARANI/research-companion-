# check_papers.py - audits the papers folder: counts, page counts, extractable text
import os
import fitz  # PyMuPDF (the package is pymupdf, the import name is fitz)
from config import PAPERS_DIR

MIN_CHARS = 200  # fewer characters than this on page 1 -> probably scanned/broken

total, problems = 0, []

for category in sorted(os.listdir(PAPERS_DIR)):
    folder = os.path.join(PAPERS_DIR, category)
    if not os.path.isdir(folder):
        continue
    pdfs = sorted(f for f in os.listdir(folder) if f.lower().endswith(".pdf"))
    print(f"\n=== {category}: {len(pdfs)} PDFs ===")
    for name in pdfs:
        total += 1
        try:
            with fitz.open(os.path.join(folder, name)) as doc:
                pages = len(doc)
                chars = len(doc[0].get_text().strip())
            status = "OK" if chars >= MIN_CHARS else "NO TEXT"
        except Exception as e:  # corrupted or truncated download
            pages, chars, status = 0, 0, f"BROKEN ({type(e).__name__})"
        if status != "OK":
            problems.append(f"{category}/{name}")
        print(f"  [{status:7}] {pages:3} pages  {chars:5} chars  {name}")

print(f"\nTotal PDFs: {total} | Problems: {len(problems)}")
for p in problems:
    print("  FIX:", p)