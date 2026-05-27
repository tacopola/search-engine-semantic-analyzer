# Semantic Search Engine (Vector + HNSW + Reranking)

A full-stack semantic search system that retrieves results based on meaning, not keyword matching. Built with PostgreSQL + pgvector, HNSW indexing, transformer embeddings, and a reranking pipeline.

---

## What this project is

This is a two-layer semantic search engine that understands meaning instead of relying on keyword matching.

It combines:
- dense vector embeddings
- approximate nearest neighbor search (HNSW)
- neural reranking
- a streaming data ingestion pipeline

The system is designed to scale to large datasets while maintaining low-latency retrieval.

---

## Core Architecture

### Layer 1 — Embedding Model (all-MiniLM-L6-v2)

Each text entry is converted into a 384-dimensional vector that represents semantic meaning.

- “cheap food”
- “affordable restaurants”

These become mathematically close in vector space even without shared words.

This allows the system to understand intent, not just text overlap.

---

### Layer 2 — Vector Search (pgvector + HNSW)

Instead of scanning all rows, the system uses an HNSW (Hierarchical Navigable Small World) index.

- Builds a graph of nearest neighbors between vectors
- Enables approximate nearest neighbor search in logarithmic time
- Supports fast retrieval even at large scale

This replaces brute-force similarity search with efficient graph traversal.

---

### Layer 3 — Reranking (Cross-Encoder)

The initial retrieval stage is fast but approximate.

To improve accuracy, a cross-encoder model reranks the top candidates:

- Takes (query, document) pairs
- Computes deep contextual relevance
- Reorders results based on true semantic similarity

This is the same high-level strategy used in production search engines like Google and Bing.

---

## Data Pipeline (ETL System)

A production-style ingestion pipeline was built to handle large-scale datasets:

- Streams ~410,000+ rows from HuggingFace datasets
- Prevents memory overload using batch processing
- GPU-accelerated embedding generation
- Deduplication using hashing strategies (MD5 / Bloom-style filtering)
- Checkpoint-based recovery system for crash resilience
- Batch inserts into PostgreSQL with pgvector support

This ensures the system can recover from failures without restarting the entire process.

---

## Tech Stack

- **Backend:** FastAPI (Python)
- **Frontend:** Next.js
- **Database:** PostgreSQL + pgvector
- **Indexing:** HNSW (approximate nearest neighbor graph)
- **Embeddings:** sentence-transformers (MiniLM)
- **Reranking:** CrossEncoder (ms-marco-MiniLM)
- **Data Source:** HuggingFace MS MARCO dataset

---

## Key Features

- Semantic search (not keyword-based)
- Sub-100ms retrieval on indexed data
- ANN search using HNSW graph structure
- Neural reranking for result refinement
- GPU-accelerated embedding pipeline
- Fault-tolerant ingestion with checkpoint recovery
- Full-stack UI for live querying

---

## Why this matters

Traditional search systems rely on keyword matching (BM25 / inverted indexes).

This project demonstrates a modern retrieval pipeline:
