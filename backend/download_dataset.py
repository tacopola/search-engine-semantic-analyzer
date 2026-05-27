import csv
import hashlib
from datasets import load_dataset
from pybloom_live import ScalableBloomFilter

print("Opening FULL MS MARCO corpus (Streaming mode)...")

dataset = load_dataset("BeIR/msmarco", "corpus", split="corpus", streaming=True)

seen = ScalableBloomFilter(mode=ScalableBloomFilter.SMALL_SET_GROWTH, error_rate=0.001)

kept_count = 0
skipped_count = 0

print("Processing and writing directly to disk...")

with open("marco_full.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["content", "category"])

    for i, item in enumerate(dataset):
        text = item["text"].strip()

        if "â" in text or "Ã" in text or "Ë" in text:
            skipped_count += 1
            continue

        if not text:
            skipped_count += 1
            continue

        if not (80 < len(text) < 600):
            skipped_count += 1
            continue

        if not text.isascii():
            skipped_count += 1
            continue

        special_char_ratio = sum(1 for c in text if not c.isalnum() and c not in " .,!?-'\"():;") / len(text)
        if special_char_ratio > 0.15:
            skipped_count += 1
            continue

        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
        if text_hash in seen:
            skipped_count += 1
            continue

        seen.add(text_hash)
        writer.writerow([text, "general"])
        kept_count += 1

        if i % 500000 == 0 and i > 0:
            f.flush()
            print(f"  Processed {i:,} rows | Kept {kept_count:,} | Skipped {skipped_count:,}")

print(f"\nDone! Saved {kept_count:,} passages to marco_full.csv")
print(f"Total skipped: {skipped_count:,}")