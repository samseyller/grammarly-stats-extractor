import email
import quopri
import re
from pathlib import Path
import unicodedata

def normalize_whitespace(text: str) -> str:
    """Clean and normalize whitespace and Unicode quirks."""
    return (
        unicodedata.normalize("NFKC", text)
        .replace('\u200c', '')  # remove zero-width non-joiners
        .replace('\xa0', ' ')   # non-breaking spaces
    )

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


def extract(pattern, text, cast=str, default=None):
    """Helper to extract the first regex group and optionally cast it."""
    match = re.search(pattern, text, re.IGNORECASE)
    return cast(match.group(1).replace(',', '')) if match else default

def extract_tones(text: str) -> dict:
    """Extract tone names and their percentages using a more resilient pattern."""
    tones = {}

    # Normalize text and look for blocks like: "Confident\n22%"
    cleaned_text = normalize_whitespace(text)

    # Match Tone followed by percentage on a separate line
    pattern = re.compile(r'([A-Z][a-z]+)\s*[\n\r]+(\d+)[%％]', re.IGNORECASE)

    for match in pattern.finditer(cleaned_text):
        tone, percentage = match.groups()
        tone = tone.lower().strip()
        tones[tone] = int(percentage)

    return tones

def parse_grammarly_metrics(text: str) -> dict:
    """Extract all Grammarly metrics."""
    metrics = {
        "date_range": extract(r"(\w+ \d+ - \w+ \d+)", text),
        "writing_streak": extract(r"Grammarly writing streak\s+(\d+)", text, int),
        "words_analyzed": extract(r"Grammarly analyzed ([\d,]+) words", text, int),
        "productivity_percentile": extract(r"more productive than (\d+)%", text, int),
        "alerts_shown": extract(r"Grammarly showed you (\d+) alerts", text, int),
        "accuracy_percentile": extract(r"more accurate than (\d+)%", text, int),
        "unique_words": extract(r"You used ([\d,]+) unique words", text, int),
        "vocab_percentile": extract(r"That.?.?.?s (\d+)% more unique words", text, int)
    }

    # Add tones as individual fields
    tones = extract_tones(text)
    metrics.update(tones)
    return metrics


# Example usage
eml_path = Path(r"emails/01.eml")
decoded_text = load_eml_and_get_plaintext(eml_path)
metrics = parse_grammarly_metrics(decoded_text)

print("📊 Grammarly Metrics Extracted:")
for key, value in metrics.items():
    print(f"- {key}: {value}")
