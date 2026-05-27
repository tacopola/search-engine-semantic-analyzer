from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import CrossEncoder
from embedder import embed
from db import get_conn, setup_table
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

setup_table()

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    
class InsertRequest(BaseModel):
    content: str
    category: str = None

@app.post("/insert")
def insert(req: InsertRequest):
    vec = embed(req.content)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO items (content, category, embedding) VALUES (%s, %s, %s)",
        (req.content, req.category, vec)
    )
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "inserted"}

@app.get("/search")
def search(query: str, top_k: int = 5, threshold: float = 0.35):
    total_start = time.perf_counter()

    # Embedding stage
    embed_start = time.perf_counter()
    vec = embed(query)
    embedding_ms = round((time.perf_counter() - embed_start) * 1000, 2)

    conn = get_conn()
    cur = conn.cursor()

    # Vector search stage
    search_start = time.perf_counter()

    cur.execute("""
        SELECT content, category, 1 - (embedding <=> %s::vector) AS similarity
        FROM items
        WHERE 1 - (embedding <=> %s::vector) > %s
        AND content ~ '^[[:ascii:]]*$'
        ORDER BY embedding <=> %s::vector
        LIMIT 50
    """, (vec, vec, threshold, vec))

    rows = cur.fetchall()

    vector_search_ms = round(
        (time.perf_counter() - search_start) * 1000,
        2
    )
    dedupe_start = time.perf_counter()

    seen = set()
    results = []

    for row in rows:
        content = row[0]
        key = content[:80].strip()

        if key not in seen:
            seen.add(key)

            results.append({
                "content": content,
                "category": row[1],
                "similarity": round(row[2], 4)
            })
        if len(results) == top_k:
            break
    dedupe_ms = round(
        (time.perf_counter() - dedupe_start) * 1000,
        2
    )
    cur.close()
    conn.close()

    total_ms = round(
        (time.perf_counter() - total_start) * 1000,
        2
    )
    return {
        "results": results,
        "metrics": {
            "embedding_ms": embedding_ms,
            "vector_search_ms": vector_search_ms,
            "dedupe_ms": dedupe_ms,
            "total_ms": total_ms
        }
    }
    
@app.post("/seed")
def seed():
    samples = [
        ("budget restaurants in Manila", "food"),
        ("affordable places to eat", "food"),
        ("luxury fine dining experience", "food"),
        ("quick street food snacks", "food"),
        ("healthy salad bowls and smoothies", "food"),
        ("late night food delivery options", "food"),
        ("family friendly restaurants with kids menu", "food"),
        ("best coffee shops for studying", "cafe"),
    ]
    conn = get_conn()
    cur = conn.cursor()
    for content, category in samples:
        vec = embed(content)
        cur.execute(
            "INSERT INTO items (content, category, embedding) VALUES (%s, %s, %s)",
            (content, category, vec)
        )
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "seeded"}