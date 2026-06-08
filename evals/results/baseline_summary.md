# Compass — Baseline Eval Results

**Date:** 06/07/2026
**Generation model:** Sonnet 4.6
**Judge model:** Sonnet 4.6 — note: same model family as generation, possible self-preference bias

## Retrieval (hit@k, MRR)

- Hit rate: 0.65
- MRR: 0.41

**Methodology note:** I wanted to explicity check the substring match before moving to embedding-similarity matching it did improve my hit rate from 0.38 to 0.65 and MRR from 0.22 to 0.41

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

status — e.g., "Run incomplete due to API rate limits; harness built and validated on
partial data, full run pending"

## Known issues / follow-ups

- source distribution skew
- vague eval questions
- rate limit handling

## What I'd do differently next iteration

I would design my eval dataset more diverse from the corpus