# neuro-skills — Cursor rule

Drop-in rule so Cursor discovers and uses the neuroscience skills in this repo.

## Install

Copy the rule below into your project as `.cursor/rules/neuro-skills.mdc` (Cursor's Project Rules
format), and make the neuro-skills repo available in your workspace — either clone it into the
project, or add it as a submodule/adjacent folder Cursor can read. Adjust the path in the rule if the
repo isn't at `./neuro-skills`.

## Rule content

```mdc
---
description: Use validated neuroscience Agent Skills for any neuroscience methods/analysis task
alwaysApply: true
---

# Neuroscience skills

This project has validated neuroscience Agent Skills under `./neuro-skills/`.

Before writing analysis code or answering a neuroscience methods question:

1. Consult `./neuro-skills/registry.yaml` — find the skill whose `description`/`tags` match the task.
2. Read that skill's `SKILL.md` and follow it. For a two-tier category (a `SKILL.md` with a
   "which leaf to load" table), read the matching leaf `SKILL.md` too.
3. Follow the skill's **Validation & Pitfalls** section — these are the common ways the analysis
   looks right but is wrong. Surface the relevant pitfalls to the user, don't just apply them silently.
4. Do NOT generate analysis code from memory when a skill covers the task. If no skill matches,
   say so rather than guessing.

Skills are knowledge, not tools: they assume you have a Python environment with the right packages
(`./neuro-skills/requirements.txt`) and, for the dataset-access and literature-search skills, network
access.
```
