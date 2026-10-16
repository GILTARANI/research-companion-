
import os
import re
import time
import arxiv
import requests
from config import PAPERS_DIR

# Category -> arXiv IDs
PAPERS = {
    "nlp": [
        "1706.03762",  # Attention Is All You Need
        "1810.04805",  # BERT
        "1907.11692",  # RoBERTa
        "1910.01108",  # DistilBERT
        "1910.10683",  # T5
        "2005.14165",  # GPT-3
        "2005.11401",  # RAG
        "2106.09685",  # LoRA
        "1908.10084",  # Sentence-BERT
    ],
    "medical_imaging": [
        "1505.04597",  # U-Net
        "1606.04797",  # V-Net
        "1711.05225",  # CheXNet
        "1804.03999",  # Attention U-Net
        "1807.10165",  # UNet++
        "1809.10486",  # nnU-Net
        "2102.04306",  # TransUNet
        "2201.01266",  # Swin UNETR
        "2304.12306",  # MedSAM
    ],
    "climate": [
        "1906.05433",  # Tackling Climate Change with ML
        "2002.00469",  # WeatherBench
        "2110.12010",  # ClimateBERT
        "2202.11214",  # FourCastNet
        "2211.02556",  # Pangu-Weather
        "2212.12794",  # GraphCast
        "2301.10343",  # ClimaX
        "2311.07222",  # NeuralGCM
        "2405.13063",  # Aurora
    ],
}

HEADERS = {
    "User-Agent": "research-companion-student-project/1.0"
}


def slugify(text, max_words=6):
    """Convert a paper title into a filename-friendly string."""
    words = re.sub(r"[^a-z0-9\s]", "", text.lower())
    return "-".join(words.split()[:max_words])


def download_file(url, dest_path, retries=3):
    """Download a PDF with retries and validate the response."""
    url = url.replace("http://", "https://")
    temp_path = dest_path + ".part"

    for attempt in range(1, retries + 1):
        try:
            # Make the actual HTTP request
            with requests.get(
                url,
                headers=HEADERS,
                timeout=60,
                stream=True,
            ) as resp:

                resp.raise_for_status()

                # Check that the response is a PDF
                content_type = resp.headers.get(
                    "Content-Type", ""
                ).lower()

                first_chunk = next(
                    resp.iter_content(chunk_size=8192), b""
                )

                if not first_chunk.startswith(b"%PDF"):
                    raise ValueError(
                        f"Response is not a PDF. "
                        f"Content-Type: {content_type}"
                    )

                # Save PDF data to a temporary file
                with open(temp_path, "wb") as file:
                    file.write(first_chunk)

                    for chunk in resp.iter_content(
                        chunk_size=8192
                    ):
                        if chunk:
                            file.write(chunk)

            # Rename only after the download completes
            os.replace(temp_path, dest_path)

            print(f"   SUCCESS: {dest_path}")
            return True

        except (
            requests.RequestException,
            OSError,
            ValueError,
        ) as error:
            print(
                f"   Attempt {attempt}/{retries} failed: "
                f"{error}"
            )

            # Remove any incomplete download
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass

            if attempt < retries:
                time.sleep(3)

    print(f"   FAILED: {dest_path}")
    return False


def main():
    client = arxiv.Client()
    failed = []

    for category, paper_ids in PAPERS.items():
        folder = os.path.join(PAPERS_DIR, category)
        os.makedirs(folder, exist_ok=True)

        print(f"\n--- Category: {category} ---")

        search = arxiv.Search(id_list=paper_ids)

        try:
            for result in client.results(search):
                year = result.published.year

                surname = re.sub(
                    r"[^a-z]",
                    "",
                    result.authors[0].name.split()[-1].lower(),
                )

                filename = (
                    f"{year}_{surname}_"
                    f"{slugify(result.title)}.pdf"
                )

                dest = os.path.join(folder, filename)

                if os.path.exists(dest):
                    print(f"SKIP: {category}/{filename}")
                    continue

                print(f"GET: {filename}")
                print(f"     Paper: {result.title}")

                if not download_file(result.pdf_url, dest):
                    failed.append(f"{category}/{filename}")

                # Pause between downloads
                time.sleep(3)

        except Exception as error:
            print(
                f"ERROR while processing {category}: {error}"
            )
            failed.append(
                f"{category}: paper search or API error"
            )

    print("\n========== DOWNLOAD SUMMARY ==========")

    if failed:
        print(f"Failed items: {len(failed)}")
        for item in failed:
            print(f" - {item}")
        print("\nRun the script again to retry missing PDFs.")
    else:
        print("All requested papers were downloaded or skipped.")

    print("\nDownload process finished.")


if __name__ == "__main__":
    main()
