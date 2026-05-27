import pandas as pd
from sentence_transformers import SentenceTransformer
from db import get_conn
from tqdm import tqdm
import torch
import sys

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")
if device == "cuda":
    print(f"GPU: {torch.cuda.get_device_name(0)}")

model = SentenceTransformer("all-MiniLM-L6-v2", device=device)

BATCH_SIZE = 512 if device == "cuda" else 256
CHECKPOINT_FILE = "insert_checkpoint.txt"

def load_checkpoint() -> int:
    """Returns the last successfully inserted row index."""
    try:
        with open(CHECKPOINT_FILE, "r") as f:
            val = int(f.read().strip())
            print(f"Resuming from checkpoint: row {val:,}")
            return val
    except FileNotFoundError:
        return 0

def save_checkpoint(row_index: int):
    with open(CHECKPOINT_FILE, "w") as f:
        f.write(str(row_index))

def bulk_insert(filepath: str):
    print(f"Loading {filepath}...")
    df = pd.read_csv(filepath)
    df["content"] = df["content"].str[:512]
    df = df.dropna(subset=["content", "category"])
    df = df.reset_index(drop=True)

    texts = df["content"].tolist()
    categories = df["category"].tolist()
    total = len(texts)
    start = load_checkpoint()
    if start >= total:
        print("Already fully inserted. Delete insert_checkpoint.txt to restart.")
        sys.exit(0)

    print(f"Total rows: {total:,} | Starting from: {start:,}")

    conn = get_conn()
    cur = conn.cursor()

    try:
        for i in tqdm(range(start, total, BATCH_SIZE), desc="Inserting"):
            batch_texts = texts[i:i+BATCH_SIZE]
            batch_cats = categories[i:i+BATCH_SIZE]

            # embed batch
            embeddings = model.encode(
                batch_texts,
                batch_size=BATCH_SIZE,
                show_progress_bar=False,
                convert_to_numpy=True
            )

            # batch insert
            cur.executemany(
                "INSERT INTO items (content, category, embedding) VALUES (%s, %s, %s)",
                [
                    (text, cat, emb.tolist())
                    for text, cat, emb in zip(batch_texts, batch_cats, embeddings)
                ]
            )
            conn.commit()

            # save checkpoint after every successful batch
            save_checkpoint(i + BATCH_SIZE)

    except KeyboardInterrupt:
        print(f"\nInterrupted! Progress saved at row {i:,}. Run again to resume.")
    except Exception as e:
        print(f"\nError at row {i:,}: {e}")
        print("Progress saved. Run again to resume.")
    finally:
        cur.close()
        conn.close()

    print(f"\nDone! Inserted {min(i + BATCH_SIZE, total):,}/{total:,} rows.")

if __name__ == "__main__":
    bulk_insert("marco_full.csv")