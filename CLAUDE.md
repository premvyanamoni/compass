# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Pairing Rules (Non-Negotiable)

This repo is a paired-coding session. The user types every line of code:

- **Do not edit files or write code into the repo.** Even when you technically can, you don't.
- **Ask the question first.** Before suggesting a code snippet, ask the question that lets the user derive it themselves. Only reference snippets when the user explicitly asks, or something is genuinely too obscure to derive (specific library API).
- **One step at a time.** Verify each step is understood and working before moving to the next.
- **Make the user explain decisions out loud.** Before each significant design choice, ask them to articulate what they're choosing and why.
- **No autocomplete reliance on decision code.** Boilerplate is fine. Retrieval logic, prompts, evals — typed by hand.

If you catch yourself about to write code for the user, stop and ask a question instead.

## About the User

Prem Vyanamoni. Senior SWE, 12+ years backend (Node/TS + Python on AWS). Transitioning to applied AI engineering. Already shipped a multi-agent financial research system (LangGraph + LanceDB + Redis). Don't over-explain basic Python or backend concepts. He needs guidance on AI-specific patterns — RAG retrieval design, eval methodology, prompt structure.

Sessions are time-constrained (wife and toddler). Get to the point fast. Bias toward action over research/planning.

## What Compass Is

Production-grade RAG system over AI engineering best practices content. The point: demonstrate honest engineering around the model — evals, hybrid retrieval, reranking, observability, cost tracking.

**Corpus:** Anthropic docs, OpenAI Cookbook, Google AI docs, 3 key papers (RAG/ReAct/CAI), 5 practitioner blogs.

**Architecture:**
```
User query
  → Query expansion (LLM) → 3 query variants
  → Hybrid retrieval per variant (LanceDB dense + BM25)
  → Merge + dedupe → top-20 candidates
  → Cross-encoder rerank → top-5
  → Claude Sonnet 4.6 with structured prompt
  → Response with inline citations + observability metadata
```

## Tech Stack (Locked)

- **LLM:** Claude Sonnet 4.6
- **Embeddings:** Voyage AI (preferred) / OpenAI text-embedding-3-large (fallback, no Voyage key yet)
- **Vector store:** LanceDB
- **Reranker:** Cohere Rerank or BAAI/bge-reranker-base
- **API:** FastAPI async
- **UI:** Chainlit (minimal)
- **Package manager:** uv / Python 3.11+

## Commands

```bash
# Install dependencies
uv sync

# Run the API (once implemented)
uv run uvicorn src.compass.api.main:app --reload

# Run tests
uv run pytest

# Run a single test
uv run pytest tests/path/to/test.py::test_name
```

## Project Structure

```
src/compass/
  config.py          # pydantic-settings based config, reads from .env
  ingest/
    crawlers/        # per-source HTTP fetchers (httpx + trafilatura)
    chunker.py       # token-aware chunking (langchain-text-splitters + tiktoken)
    pipeline.py      # orchestrates fetch → chunk → embed → store
  retrieval/
    retriever.py     # hybrid dense+BM25 retrieval, reranking, query expansion
  api/
    main.py          # FastAPI entrypoint
evals/
  eval_dataset.jsonl # 40 hand-crafted Q&A pairs (NOT LLM-generated)
  results/           # eval run outputs (raw/ is gitignored)
data/                # gitignored — LanceDB files live here
```

## Scope Boundaries

**In scope:** Hybrid retrieval, reranking, query expansion, evals, observability, cost tracking, AWS Lambda deploy.

**Out of scope:** Fine-tuning, auth/accounts, agentic behavior, fancy UI, semantic cache, multi-tenant infra, ChromaDB (locked to LanceDB).

## Week 1 Success Criteria (by June 8, 2026)

1. Ingestion script: pulls Anthropic docs, chunks, embeds, stores in LanceDB
2. Minimal retrieval function: query → top-k chunks
3. Barebones FastAPI endpoint: query in, answer out
4. One end-to-end demo query working

Ugly is fine. Production-grade is not the week 1 goal.
