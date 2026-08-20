# neuro-skills — Windsurf rule

Drop-in rule so Windsurf (Cascade) discovers and uses the neuroscience skills in this repo.

## Install

Copy the rule below into your project as `.windsurf/rules/neuro-skills.md` (or append it to a
top-level `.windsurfrules` file), and make the neuro-skills repo available in your workspace — clone
it into the project or add it as an adjacent folder Cascade can read. Adjust the path if the repo
isn't at `./neuro-skills`.

## Rule content

```md
# Neuroscience skills

This workspace has validated neuroscience Agent Skills under `./neuro-skills/`.

When the task is a neuroscience methods or analysis question:

1. Read `./neuro-skills/registry.yaml` and pick the skill whose `description`/`tags` match the task.
2. Open that skill's `SKILL.md` and follow it. If it is a category router (has a "which leaf to load"
   table), also open the matching leaf `SKILL.md`.
3. Apply the skill's **Validation & Pitfalls** section and surface the relevant pitfalls to the user.
4. Do not write analysis code from memory when a skill covers the task; if none matches, say so.

These skills are knowledge, not tools — they assume a Python environment with the packages in
`./neuro-skills/requirements.txt`, plus network access for the dataset-access and lit-search skills.
```
