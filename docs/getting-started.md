# Getting started

This repo provides **skills** — knowledge, not capability. Every skill here assumes the agent
reading it already has generic tools (execute code, read/write files, and for some skills, reach
the internet) and tells it how to use those tools correctly for a specific neuroscience task. It
doesn't add new abilities to an agent; it grounds abilities the agent already has in validated,
citation-backed practice instead of whatever the model happens to remember.

That means turning this repo into "Claude/ChatGPT/my local LLM actually helps me with neuro
analysis" requires two things, not one:

1. **The skills** (this repo) — what to do, and what goes wrong if you do it carelessly.
2. **The environment** — a code execution tool with the right packages installed, and for some
   skills, internet access. This repo doesn't provide this part; you have to set it up.

Skip either one and something breaks: skills without the right packages installed means correct
code that can't run; environment without skills means an agent generating plausible-looking but
uninformed analysis code from memory — the exact failure mode this repo exists to prevent.

## What needs internet access, and what doesn't

Most skills here (preprocessing, analysis, modeling) only need local code execution — once data is
in hand, nothing about spike-train statistics or an fMRI GLM requires network access. Two
categories are different:

- **Acquisition skills** (`dandi-archive-access`, `allen-brain-observatory-access`,
  `openneuro-bids-access`) call real external APIs. No network access, no data.
- **Literature/context-gathering work** (finding related papers, checking whether an approach has
  precedent) needs an actual search tool. A skill can teach an agent how to formulate a good query
  and synthesize results — it cannot substitute for the agent actually being able to reach a search
  API when the agent has none.

## Setup per host

### Claude Code

The closest thing to "just works." Claude Code already has code execution (`Bash`), file I/O, and
(if network isn't restricted in your environment) web access.

```bash
git clone https://github.com/axscience/neuro-skills.git
cd neuro-skills
pip install -r requirements.txt   # or a subset — see requirements.txt's comments
```

The repo ships a plugin manifest at `.claude-plugin/plugin.json` that lists every top-level skill
directory, so Claude Code auto-discovers all 37 skills (categories recurse into their leaves) — no
per-skill wiring. Install the clone as a local plugin, or point Claude Code at the repo directory.
Confirm network access if you need `neuro-data-standards/references/dataset-access.md` or
`neuro-lit-search` — some sandboxed/restricted environments block it.

### ChatGPT (Custom GPT)

Concrete setup, because "upload the skill files" is too vague when there are 37 of them:

**1. Which files to upload** (as Custom GPT Knowledge files):
- Always upload `registry.yaml` — it's the index the GPT uses to find the right skill.
- Upload the `SKILL.md` files for *your* domain, not all 37. For an EEG researcher that's
  `electrophysiology/SKILL.md` + the references you use (`electrophysiology/references/eeg.md`, etc.)
  + cross-cutting skills you'll hit (`neuro-stats/SKILL.md`, `neuro-figures/SKILL.md`). Knowledge-file
  limits (20 files on most tiers) mean you curate to a domain, not the whole repo.
- For a two-tier category (e.g. `optical-imaging`), upload the category `SKILL.md` **and** the leaf
  `SKILL.md` files you need (`optical-imaging/suite2p/SKILL.md`), since the router points to them.

**2. System-prompt snippet** (paste into the Custom GPT's Instructions):

> You have neuroscience Agent Skills in your Knowledge files. Before answering a neuroscience
> methods/analysis question, consult `registry.yaml` to identify the relevant skill by its
> `description` and `tags`, then read that skill's `SKILL.md` and follow it — especially its
> "Validation & Pitfalls" section. Do not generate analysis code from memory if a skill covers the
> task. If the matching skill isn't in your Knowledge files, say so rather than guessing.

**3. Known limitation:** Code Interpreter's execution sandbox is offline by default. Uploading skill
files gives the model the *knowledge*, not sandbox network access. A GLM or spike-train-stats skill
works fine (local computation only); the dataset-access and literature-search skills will not,
unless wired up separately through Actions (ChatGPT's tool-calling mechanism) pointed at a real API.

### A researcher's own local LLM

The skill files are portable — they're plain markdown, not tied to Claude specifically. But there's
no built-in skill-loader or tool-execution loop the way Claude Code has one. To get equivalent
behavior, the researcher needs an agent framework that can:

- retrieve the relevant `SKILL.md` (and its `references/`) into context for a given request —
  whether that's simple keyword matching, embedding-based retrieval, or just manually pointing the
  model at the right file, and
- actually execute code and, for the skills that need it, make real HTTP requests.

Without that scaffolding, the content is still useful as documentation a researcher reads and
adapts by hand — it just isn't "plug and play" the way it is inside an agent harness that already
does skill-loading and tool execution for you.

## A minimal test

Once set up, a reasonable first check: ask the agent to compute spike-train statistics on synthetic
data using the [spike-recording](../spike-recording/SKILL.md) skill (no network needed, no external
dataset needed — the ISI/firing-rate/PSTH/CV/Fano-factor code in that skill's Core usage section is
fully self-contained). If that runs and the agent's explanation matches the skill's Validation &
Pitfalls section (e.g. it flags refractory-period violations as a sorting problem, not biology), the
environment and skill-loading are both wired up correctly.
