# Compass — Baseline Eval Results

**Date:** 06/08/2026
**Version:** Baseline v4(Semantic chunking)
**Generation model:** Sonnet 4.6
**Judge model:** Sonnet 4.6 — note: same model family as generation, possible self-preference bias

## Retrieval (hit@k, MRR)

- Hit rate: 0.65
- MRR: 0.41

**Methodology note:** I wanted to explicity check the substring match before moving to embedding-similarity matching it did improve my hit rate from 0.38 to 0.65 and MRR from 0.22 to 0.41

## Post-reanking

- Hit rate: 0.62
- MRR: 0.54

**Methodology note:** After implementing cross encoder after the retrieval using cohere API, MRR improved 30%, howevere the hit rate dropped, this helped me understand the tradeoff reranking improved the ranking quality but reduced recall/9fewer candidates survived to the final set)

## Post query expansion

Good numbers first — hit rate 0.70, MRR 0.59. That's meaningful improvement over reranking-only (0.62, 0.54). Query expansion is working.

Combined improvement over the original baseline:

Hit rate: 0.65 → 0.62 (reranking) → 0.70 (+ query expansion)
MRR: 0.41 → 0.54 (reranking) → 0.59 (+ query expansion)
Not where I wanted to be which is 0.75 for hit rate, I'll examine if my query variants can be improved by manually chec some samples.


## Semantic chunking

tried semantic chunking, hit rate dropped to 0.33, so reverted.
The likely cause: with only 1,216 chunks now that covers the same corpus, chunks are much larger and more diffuse. The embedding for a 3,000-token chunk representing multiple topics is a "blurred" vector so it doesn't match any single query as precisely as a focused 1,000-token chunk would.

## Voyage embeddings

switching from local sentence-transformers to Voyage AI embeddings improved retrieval hit rate from 0.70 to 0.88.

| Baseline | Hit Rate | MRR |
| --- | --- | --- |
| Baseline (hybrid only) | 0.65 | 0.41 |
| + Reranking | 0.62 | 0.54 |
| + Query expansion | 0.70 | 0.59 |
| + Semantic chunking | 0.33 | 0.25 |
| + Reverted to fixed-size | 0.70 | 0.64 |
| + Voyage embeddings + reranking| 0.88 | 0.81 |

## Faithfulness

- Faithful: 38/40
- Partial: 2/40
- Unfaithful: 0/40

**Spot-check finding:** I manually verified the partial eval verdicts to be too strict, this could be due to the questions being vague nature of the question, I decided to take another poke at it after adjusting the eval datset.

## Refusal correctness

- Refusal accuracy (on refusal-type questions): 9 out of 13 refusal-type questions correctly refused
- False refusal rate (on non-refusal questions): 3/27

**Interpretation:** about third of the time, when the corpus genuinely lacked the answer, the system answered anyway instead of saying "I don't know". That's the hallucination risk
roughly 1 in 9 times, the system refused when it actually should have answered. That's an over-caution problem — annoying UX, but less dangerous than hallucinating.

## Citation accuracy

Faithfulness rate: 108.5/205, Partial: 131, Unfaithful: 31

Citation accuracy: 108.5/205 weighted score (53%) — that meant across 205 individual citation checks, only 43 were fully faithful, 131 partial, 31 unfaithful.

When I Compare that to overall faithfulness from above (38/40 = 95%): the question-level check looked good, but citation-level checking is much stricter — it checks whether each specific [N] reference actually supports the adjacent claim, not just whether the answer as a whole is grounded.

The high partial count (131) — learned that citations aren't outright wrong, but the model is often citing a chunk that's loosely related rather than directly supporting the claim. This helped me understand the kind of subtle failure that question-level faithfulness misses entirely.

## Known issues / follow-ups

- source distribution skew
- vague eval questions
- rate limit handling(done)

## What I'd do differently next iteration

I would design my eval dataset more diverse from the corpus