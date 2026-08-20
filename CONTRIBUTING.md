# Contributing a skill

A skill is one neuroscience modality or cross-cutting technique, documented so an AI agent can use
it correctly. This doc is the spec for adding or editing one.

## Design principle

**Modality-first for signal-level stages, technique-first for everything downstream of cleaned
data.** Acquisition and preprocessing are genuinely modality-specific (EEG filtering shares nothing
with fMRI motion correction) — those live under a top-level folder named for the modality
(`electrophysiology/`, `mri/`, `optical-imaging/`, ...). Statistics, connectivity, decoding, and
computational modeling genuinely span modalities — those live under a top-level folder named for the
technique (`neuro-stats/`, `neuro-connectivity/`, `neuro-decoding-encoding/`, ...).

**A technique used across three or more modalities becomes its own cross-cutting skill, referenced
from each modality skill rather than restated in each one.** If you're about to write about
multiple-comparison correction, permutation testing, or cross-validation leakage inside a modality
skill, stop — link to `neuro-stats` or `neuro-decoding-encoding` instead. Duplicated methodology
content drifts out of sync as one copy gets updated and the others don't.

## 1. Pick where the skill lives

- **New modality, not yet covered** (a new recording/imaging technique): new top-level folder named
  for the modality.
- **New sub-topic within an existing modality** (e.g. a new EEG technique): a new file under that
  modality's `references/`, not a new top-level folder. Check the existing skill's SKILL.md routing
  table first — your topic may already have a home.
- **New cross-cutting technique used across ≥3 modalities**: new top-level folder named for the
  technique, or a new reference under an existing cross-cutting skill (`neuro-stats`,
  `neuro-connectivity`, `neuro-decoding-encoding`, `clinical-biomarkers-ml`) if it fits one already.
- **Unsure**: open an issue before writing content — restructuring after the fact is more disruptive
  than getting placement right up front.

## 2. Folder layout

Most skills are **flat** — one `SKILL.md` plus optional `references/`:

```
<category>/
  SKILL.md              # required — overview + when-to-use + core usage + routing table (if references/) + validation
  references/             # optional — one file per sub-topic, loaded on demand
    <sub-topic>.md
```

A modality with **genuinely competing tools for the same job** (or a clean tool/method seam users
invoke independently) becomes **two-tier** — a category router `SKILL.md` over per-tool/per-method
leaf skills:

```
<category>/
  SKILL.md              # category router — includes a "Which leaf skill to load" table linking every leaf
  <leaf>/SKILL.md         # a per-tool or per-method leaf skill
```

Don't split a skill that has a single dominant tool (e.g. `electrophysiology` = MNE) or is genuinely
cross-cutting (e.g. `neuro-stats`) — that's churn for no gain. Split only when multiple real tools
compete (e.g. `optical-imaging` → suite2p / caiman) or there's a clean acquisition/analysis seam
(e.g. `spike-recording` → spikeinterface / spike-train-stats). All directory and file names are
kebab-case and match the `name`/filename.

## 3. `SKILL.md` frontmatter

```yaml
---
name: skill-name
description: What this covers and when to reach for it over a neighboring skill. This is what an agent uses to decide relevance, so be specific — name the neighbor explicitly if there's overlap (e.g. "for X use this skill; for Y use <other-skill> instead").
license: <license of the underlying library/technique, e.g. "BSD-3-Clause">
allowed-tools: Read Write Edit Bash   # only the tools this skill's workflow actually needs — don't default to a uniform list
compatibility: Version/environment notes for the underlying library, if relevant
metadata:
  version: "1.0"
  skill-author: <your name or handle>
  category: <the top-level category folder name — for a flat skill or category router, its own folder; for a leaf, its parent category>
---
```

`metadata.category` is required and validated. The older `metadata.modality` field is **rejected** —
use `category`.

## 3a. Register the skill

Every `SKILL.md` needs an entry in `registry.yaml` (the machine-readable discovery index agents and
the Claude Code / Cursor / ChatGPT integrations consume). Add:

```yaml
  - name: "skill-name"           # matches frontmatter name
    type: skill                    # "skill" for a flat skill or leaf; "category" for a router
    sub_type: tool                  # tool | method | cross-cutting | category
    category: "top-level-folder"     # the path's first segment
    path: "top-level-folder/.../SKILL.md"
    description: "Front-load tool/modality keywords — this is the discovery string."
    date_added: "YYYY-MM-DD"
    tags: ["..."]                     # optional
```

`scan_skills.py` cross-checks the registry against the filesystem (every SKILL.md has exactly one
entry, paths resolve, names/categories match), so a missing or drifted entry fails CI. Also add the
new top-level directory to `.claude-plugin/plugin.json`'s `skills` array if it's a new category/flat
skill (leaves are picked up automatically by their category directory).

## 4. `SKILL.md` body

Required sections:

1. **Overview** — what this covers and when to use it over a neighboring skill.
2. **When to use this skill** — a bulleted trigger list: keywords/terms, file extensions, and task
   phrases that should surface this skill. This is a separate, more concrete thing than the
   frontmatter `description` — the description is prose an agent weighs against a query; this list
   is scannable, literal trigger signal (a file extension, a library name, a phrase a researcher
   would actually type). Both matter; neither substitutes for the other.
3. **A routing table**, if this skill has a `references/` folder — a short "if you have X, read
   references/x.md" list right at the top of Core usage. This is not optional for multi-reference
   skills: it's what makes progressive disclosure work. A reader (human or agent) should never have
   to read every reference to find the right one.
4. **Core usage** — the shared/entry-point guidance, with real worked code. Modality- or
   technique-specific depth goes in `references/*.md`, each structured the same way (its own Core
   usage + a **Validation & Pitfalls** section).
5. **Validation & Pitfalls** — required, not optional, at both the top-level SKILL.md and in every
   reference file. At minimum:
   - A citation to the canonical methods paper or reference documentation.
   - The 3-5 most common ways this goes wrong in practice — things that make an agent-generated
     analysis *look* correct but aren't.

A skill or reference without a real Validation & Pitfalls section (not just "read the docs") won't
be merged.

## 5. Agent behavior when a skill is loaded

This applies once, repo-wide — don't restate it inside individual skills. Before writing code for
anything beyond a trivial, unambiguous request, an agent following any skill in this repo should:

1. State the research question or goal being addressed.
2. Justify why this skill/method fits the data and question (not just that it's available).
3. Declare the expected output (a plot, a fitted model, a statistic, a cleaned dataset).
4. Note assumptions and limitations — data quality, sample size, missing metadata, anything the
   Validation & Pitfalls section flags as relevant to this specific case.
5. Present the plan and confirm before executing, for anything with real analytic-choice
   consequences (a preprocessing parameter, a statistical test, a model specification) — not for
   read-only exploration or a request with only one reasonable interpretation.

This is a behavior convention for whatever's consuming the skill, not something `scan_skills.py`
can check — it's listed here so skill authors don't duplicate it as boilerplate in every `SKILL.md`.

## 6. Before opening a PR

Run the validator:

```bash
python scan_skills.py
```

It checks: frontmatter is present and well-formed, `metadata.modality` matches the top-level folder,
a routing table exists in `SKILL.md` when `references/` is non-empty, required body sections exist
in every `SKILL.md` and reference file, and internal links resolve to real files.

## 7. Scope

This repo is neuroscience only. If you have a great skill for a different domain, it likely belongs
in a different repo, not here.
