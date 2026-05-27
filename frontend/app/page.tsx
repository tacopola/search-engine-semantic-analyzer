"use client";

import { ArrowRight, Database, Search, Sparkles } from "lucide-react";
import { useState } from "react";

type Result = {
  content: string;
  similarity: number;
};

type Metrics = {
  embedding_ms: number;
  vector_search_ms: number;
  dedupe_ms: number;
  total_ms: number;
};

type SearchResponse = {
  results: Result[];
  metrics: Metrics;
};

export default function Home() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Result[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(false);

  const search = async () => {
    if (!query.trim()) return;

    setLoading(true);

    try {
      const res = await fetch(
        `http://localhost:8000/search?query=${encodeURIComponent(
          query,
        )}&top_k=5`,
      );

      const data: SearchResponse = await res.json();

      setResults(data.results);
      setMetrics(data.metrics);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-white text-zinc-950">
      {/* Background Grid */}
      <div className="absolute inset-0 -z-10 bg-[linear-gradient(to_right,#f4f4f5_1px,transparent_1px),linear-gradient(to_bottom,#f4f4f5_1px,transparent_1px)] bg-[size:48px_48px]" />

      <div className="mx-auto flex max-w-6xl flex-col px-6 py-16">
        {/* Hero */}
        <section className="mb-24 max-w-4xl">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-zinc-200 bg-white px-3 py-1 text-xs text-zinc-600 shadow-sm">
            <Sparkles className="h-3.5 w-3.5" />
            Semantic retrieval pipeline
          </div>

          <h1 className="max-w-4xl text-5xl font-semibold leading-[1.05] tracking-tight md:text-7xl">
            Search by
            <span className="text-zinc-400"> meaning</span>,
            <br />
            not keywords.
          </h1>

          <p className="mt-8 max-w-2xl text-base leading-8 text-zinc-600">
            A semantic search engine built with vector embeddings, pgvector,
            HNSW indexing, and cross-encoder reranking. Designed to retrieve
            highly relevant results across hundreds of thousands of records in
            milliseconds.
          </p>

          <p className="max-w-2xl text-base leading-8 text-zinc-600">
            Dataset: MS MARCO (Microsoft MAchine Reading COmprehension)
          </p>

          <div className="mt-10 flex flex-wrap gap-3">
            {[
              "384D Embeddings",
              "410K Rows Indexed",
              "PGVector Integration",
              "HNSW Indexing",
              "Cross-Encoder Reranking",
              "Sub-100ms Retrieval",
            ].map((item) => (
              <div
                key={item}
                className="rounded-xl border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-700 shadow-sm"
              >
                {item}
              </div>
            ))}
          </div>
        </section>

        {/* Search */}
        <section className="mb-24">
          <div className="overflow-hidden rounded-3xl border border-zinc-200 bg-white shadow-[0_10px_40px_rgba(0,0,0,0.04)]">
            <div className="border-b border-zinc-100 px-6 py-4">
              <div className="flex items-center gap-2 text-sm text-zinc-500">
                <Database className="h-4 w-4" />
                Live semantic retrieval
              </div>
            </div>

            <div className="p-6">
              <div className="flex flex-col gap-3 md:flex-row">
                <div className="relative flex-1">
                  <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-400" />

                  <input
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && search()}
                    placeholder="e.g. cheap places to eat near universities"
                    className="h-14 w-full rounded-2xl border border-zinc-200 bg-zinc-50 pl-11 pr-4 text-sm outline-none transition focus:border-zinc-300 focus:bg-white"
                  />
                </div>

                <button
                  onClick={search}
                  disabled={loading}
                  className="inline-flex h-14 items-center justify-center gap-2 rounded-2xl bg-zinc-950 px-6 text-sm font-medium text-white transition hover:opacity-90 disabled:opacity-50"
                >
                  {loading ? "Searching..." : "Search"}
                  {!loading && <ArrowRight className="h-4 w-4" />}
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Results */}
        <section className="space-y-4">
          {results.length > 0 && (
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-medium text-zinc-900">
                Search Results
              </h2>

              <div className="text-right">
                <p className="text-sm text-zinc-500">
                  {results.length} matches · {metrics?.total_ms}ms
                </p>

                {metrics && (
                  <div className="mt-1 text-xs text-zinc-400">
                    Embed {metrics.embedding_ms}ms · Search{" "}
                    {metrics.vector_search_ms}ms · Process {metrics.dedupe_ms}ms
                  </div>
                )}
              </div>
            </div>
          )}

          {results.map((r, i) => (
            <div
              key={i}
              className="rounded-3xl border border-zinc-200 bg-white p-6 shadow-sm transition hover:border-zinc-300"
            >
              <div className="mb-5 flex items-center justify-between">
                <div className="rounded-full border border-zinc-200 bg-zinc-50 px-3 py-1 text-xs font-medium text-zinc-600">
                  Similarity {(r.similarity * 100).toFixed(1)}%
                </div>

                <div className="text-xs text-zinc-400">semantic match</div>
              </div>

              <p className="text-sm leading-7 text-zinc-700">{r.content}</p>
            </div>
          ))}

          {!loading && results.length === 0 && (
            <div className="rounded-[32px] border border-dashed border-zinc-200 bg-white py-24 text-center">
              <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl border border-zinc-200 bg-zinc-50">
                <Search className="h-5 w-5 text-zinc-500" />
              </div>

              <h3 className="text-lg font-medium tracking-tight">
                Semantic retrieval demo
              </h3>

              <p className="mx-auto mt-3 max-w-md text-sm leading-7 text-zinc-500">
                Enter a natural language query and the engine will retrieve the
                most semantically relevant results using vector similarity
                search and reranking.
              </p>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
