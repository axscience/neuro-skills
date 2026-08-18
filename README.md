# neuro-skills

Open, plug-and-play [Agent Skills](https://github.com/anthropics/skills) for neuroscience research —
curated, validated knowledge that any AI agent (Claude Code, Cursor, a research-workspace platform's
own agent, etc.) can load to correctly analyze neural data, instead of generating analysis code from
parametric memory alone.

Clone the repo, point any agent at it, and it gains validated, ready-to-run neuroscience knowledge —
across recording modalities, preprocessing, analysis, statistics, and computational modeling.

## What makes this different from a generic skills catalog

Most agent-skill libraries are a flat, alphabetical list of "here's how to use library X." Three
things are different here:

1. **Modality-first for signal-level work, technique-first for everything downstream.** Acquisition
   and preprocessing are genuinely modality-specific (EEG filtering shares nothing with fMRI motion
   correction), so those live under a top-level folder named for the modality
   (`electrophysiology/`, `mri/`, `optical-imaging/`, ...). Statistics, connectivity, decoding, and
   computational modeling genuinely span modalities, so those live under a folder named for the
   technique (`neuro-stats/`, `neuro-connectivity/`, `neuro-decoding-encoding/`, ...) instead of
   being restated per modality.
2. **Every skill and reference carries a Validation & Pitfalls section.** A citation to the canonical
   methods reference, and the common failure modes an agent (or a researcher) actually hits — not
   just API usage, but where the usage goes wrong.
3. **Neuroscience only, deliberately narrow.** Depth in one domain instead of shallow breadth across
   many. No materials science, no genomics, no chemistry — those are different repos if they happen.

## Standalone by design

This repo has no dependency on any particular platform. Clone it and use it with anything that can
read Agent Skills:

```bash
git clone https://github.com/axscience/neuro-skills.git
```

- **Claude Code / Cursor / any Agent-Skills-compatible tool**: point it at this repo's root (or copy
  individual top-level skill folders into your tool's skills directory) and the agent picks up
  `SKILL.md` automatically.
- **A custom platform's own agent**: read `SKILL.md` frontmatter (see [CONTRIBUTING.md](CONTRIBUTING.md)
  for the schema) to retrieve and inject skill content into your own prompt/tool pipeline.

Nothing in the skill format assumes a specific execution environment, sandbox, or backend — that's a
decision for whatever's consuming the repo, not something this repo bakes in.

This repo is skills (knowledge), not tools (capability) — see [docs/getting-started.md](docs/getting-started.md)
for what that distinction means in practice, what environment/tool access you still need on top of
these skills, and setup notes for Claude Code, ChatGPT, and a self-hosted local LLM.

## Structure

```
<modality-or-technique>/
  SKILL.md               # frontmatter + overview + core usage + routing table + validation
  references/               # optional — one file per sub-topic, loaded on demand
    <sub-topic>.md
docs/
  skills.md               # full index, by modality and by technique
  getting-started.md       # skill-vs-tool distinction, environment setup per host
plugin.json                # agent-plugins.org manifest
requirements.txt             # consolidated pip dependencies across all skills
scan_skills.py                # validator — frontmatter schema, modality-folder consistency, dead links
```

## Status

25 top-level skills, 22 nested references — spanning EEG, MEG, intracranial (ECoG/sEEG/DBS-LFP),
fNIRS, sleep PSG, fMRI, structural and diffusion MRI, PET, spike recording, calcium imaging, fiber
photometry, voltage imaging, animal behavior tracking, human psychophysics, eye tracking,
psychophysiology (incl. EMG), experimental design, optogenetics/chemogenetics, human/clinical brain
stimulation, histology and anatomical tracing, EM connectomics, biophysical and cognitive
computational modeling, data standards (BIDS/NWB) and dataset access, statistics, connectivity,
decoding/encoding, clinical biomarker ML, literature search, and figures. See
[docs/skills.md](docs/skills.md) for the full index and ownership notes on where overlapping content
belongs. See [CONTRIBUTING.md](CONTRIBUTING.md) to add a skill — known remaining gaps are listed at
the bottom of the skill index.

## License

MIT — see [LICENSE.md](LICENSE.md).
