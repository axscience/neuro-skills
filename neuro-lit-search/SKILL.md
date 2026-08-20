---
name: neuro-lit-search
description: Formulating effective literature search queries for neuroscience questions, and synthesizing/citing search results responsibly. This skill is about the query-formulation and synthesis discipline — it requires an actual search tool (web search, PubMed API, or similar) to be available to the agent; it cannot substitute for one. See docs/getting-started.md for what tool access this needs.
license: MIT
allowed-tools: Read WebSearch WebFetch
compatibility: Assumes access to a search tool (PubMed E-utilities API, Semantic Scholar API, or general web search) — this skill provides no search capability itself.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  category: neuro-lit-search
---

# Neuroscience Literature Search

## Overview

This skill is knowledge about *how* to search and synthesize neuroscience literature well — it is
not itself a search capability. An agent following this skill still needs an actual tool (web search,
a PubMed API call, a Semantic Scholar query) to execute against; without one, the best this skill can
offer is documentation, not results. See the repo's [docs/getting-started.md](../docs/getting-started.md)
for what tool access different hosts (Claude Code, ChatGPT, a local LLM) provide by default.

## When to use this skill

Activate when the request involves:
- Literature search, prior work, related studies, PubMed, systematic review, meta-analysis discovery
- "What does the literature say about X," "find papers on...," "has this been studied before"

## Core usage

### Query formulation

```
Weak query:  "does meditation help anxiety"
Better:      "mindfulness-based intervention randomized controlled trial anxiety disorder outcome"
Best (PubMed-style, using MeSH terms and field tags):
             ("Mindfulness"[MeSH] OR "meditation"[tiab]) AND "Anxiety Disorders"[MeSH]
             AND "Randomized Controlled Trial"[pt]
```

Specific, field-appropriate terminology (MeSH terms for PubMed, precise technical vocabulary
generally) retrieves substantially more relevant results than a natural-language paraphrase of the
question — the gap between "weak" and "best" above is not stylistic, it materially changes recall
and precision.

### A systematic search checklist, not a single query

For anything beyond a quick sanity check, don't rely on one search — vary:
- **Terminology**: synonyms and both technical/lay terms (e.g. "electroconvulsive therapy" and "ECT")
- **Study type filters**: when the question calls for it, restrict to reviews, RCTs, or meta-analyses
  specifically rather than treating a single case report with the same evidentiary weight
- **Recency**: check whether a foundational older paper has since been contradicted, refined, or
  superseded — cite the current state of evidence, not just the most-cited historical paper

### Synthesis discipline

- State what search was actually performed (terms, date range, source) so a reader can assess
  coverage — "a survey of the literature suggests" without this is not verifiable.
- Distinguish a single study's finding from a literature consensus — one paper, even a well-cited
  one, is a data point, not a settled conclusion, unless framed as such explicitly.
- Note contradictory findings when they exist rather than selectively citing only supportive papers
  — a synthesis that doesn't mention a well-known contradicting result is misleading by omission.

## Validation & Pitfalls

- **A literature search is only as good as the search tool's actual coverage and the agent's actual
  ability to invoke it** — if the executing agent has no real search/API access, its output is
  recalled/memorized training data dressed as a search result, not a current search. This is a
  categorically different (and much less reliable) thing, and should never be presented as if a
  search was actually performed when it wasn't.
- **Citation fabrication is a known failure mode for language models operating without real
  retrieval** — a plausible-sounding author/year/journal citation is not evidence it's real. Any
  citation this skill (or any skill in this repo) produces should be verifiable against an actual
  source, not accepted on the model's confidence alone.
- **Publication bias means a literature search oversamples positive/significant findings relative to
  the true underlying effect** — this is a property of the published record itself, not a search
  methodology flaw, and no query refinement fixes it. For contested or small-effect-size questions,
  actively search for null results, preprints, and registered-report literature, which are less
  subject to this bias than the traditional published record.
- **A search restricted to abstracts (common when full-text access is unavailable) misses methods
  details that can change how a finding should be weighted** — an abstract-only synthesis should be
  labeled as such, not presented with the same confidence as a full-text-informed one.
