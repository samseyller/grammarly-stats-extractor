import email
import quopri
import re
import unicodedata
import csv
from pathlib import Path


def load_eml_and_get_plaintext(file_path: Path) -> str:
    """Load an EML file and return the decoded plain text body."""
    with open(file_path, 'rb') as f:
        msg = email.message_from_binary_file(f)

    for part in msg.walk():
        if part.get_content_type() == 'text/plain':
            payload = part.get_payload(decode=True)
            decoded = quopri.decodestring(payload).decode('utf-8', errors='replace')
            return decoded
    return ""


def normalize_whitespace(text: str) -> str:
    """Normalize Unicode whitespace and control characters."""
    return (
        unicodedata.normalize("NFKC", text)
        .replace('\u200c', '')
        .replace('\xa0', ' ')
    )


def extract(pattern, text, cast=str, default=None):
    match = re.search(pattern, text, re.IGNORECASE)
    return cast(match.group(1).replace(',', '')) if match else default


def extract_tones(text: str) -> dict:
    """Extract tone percentages from the normalized text."""
    tones = {}
    pattern = re.compile(r'([A-Z][a-z]+)\s*[\n\r]+(\d+)[%％]', re.IGNORECASE)

    for match in pattern.finditer(text):
        tone, percentage = match.groups()
        tone = "tone_"+tone.lower().strip()
        tones[tone] = int(percentage)

    return tones


def parse_grammarly_metrics(text: str) -> dict:
    """Extract structured Grammarly metrics from decoded email body."""
    metrics = {
        "1_date_range": extract(r"(\w+ \d+ - \w+ \d+)", text),
        "2_writing_streak": extract(r"Grammarly writing streak\s+(\d+)", text, int),
        "3_words_analyzed": extract(r"Grammarly analyzed ([\d,]+) words", text, int),
        "4_productivity_percentile": extract(r"more productive than (\d+)%", text, int),
        "5_alerts_shown": extract(r"Grammarly showed you (\d+) alerts", text, int),
        "6_accuracy_percentile": extract(r"more accurate than (\d+)%", text, int),
        "7_unique_words": extract(r"You used ([\d,]+) unique words", text, int),
        "8_vocab_percentile": extract(r"That.?.?.?s (\d+)% more unique words", text, int)
    }

    # Extract tones and include them
    tones = extract_tones(text)
    metrics.update(tones)

    return metrics


def process_eml_folder(folder_path: Path, output_csv: Path):
    """Process all .eml files in a folder and write results to CSV."""
    data = []
    all_fields = set()

    for eml_file in folder_path.glob("*.eml"):
        text = load_eml_and_get_plaintext(eml_file)
        if not text:
            print(f"[!] Skipped (no plain text found): {eml_file.name}")
            continue

        normalized = normalize_whitespace(text)
        metrics = parse_grammarly_metrics(normalized)
        metrics["0_filename"] = eml_file.name
        data.append(metrics)
        all_fields.update(metrics.keys())

    # Write to CSV
    fieldnames = sorted(all_fields)  # ensure consistent column order

    with open(output_csv, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    print(f"✅ Exported {len(data)} records to {output_csv}")


# ---- Run It ----
if __name__ == "__main__":
    eml_folder = Path(r"emails")  # Replace with your folder
    output_csv = Path("grammarly_metrics.csv")
    process_eml_folder(eml_folder, output_csv)
