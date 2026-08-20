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

- **Claude Code**: the repo ships a plugin manifest at [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json)
  that lists every top-level skill directory, so Claude Code auto-discovers all 37 skills. Install the
  local clone as a plugin, or point Claude Code at the repo directory.
- **Cursor / Windsurf**: drop-in rules files live in [`integration-templates/`](integration-templates/) —
  copy `cursor-rules.md` or `windsurf-rules.md` into your project so the editor knows to consult
  `registry.yaml` and load the matching `SKILL.md`.
- **ChatGPT (Custom GPT)**: see [docs/getting-started.md](docs/getting-started.md) for exactly which
  files to upload (`registry.yaml` + the SKILL.md files for your domain) and a system-prompt snippet.
- **A custom platform's own agent**: read [`registry.yaml`](registry.yaml) to discover skills, then
  read the matching `SKILL.md` (frontmatter schema in [CONTRIBUTING.md](CONTRIBUTING.md)) and inject
  it into your prompt/tool pipeline.

Nothing in the skill format assumes a specific execution environment, sandbox, or backend. This repo
is skills (knowledge), not tools (capability) — see [docs/getting-started.md](docs/getting-started.md)
for what that distinction means and what environment/tool access you still need on top of these skills.

## Structure

Skills are **modality/technique-first**. Most are flat (a single `SKILL.md` plus optional
`references/`); a few modalities with genuinely competing tools are **two-tier** — a category router
`SKILL.md` over per-tool/per-method leaf skills, each loaded on demand.

```
<category-or-skill>/
  SKILL.md               # flat skill, OR a category router with a "which leaf to load" table
  references/               # (flat skills) one file per sub-topic, loaded on demand
    <sub-topic>.md
  <leaf>/SKILL.md           # (two-tier categories) a per-tool/per-method leaf skill
docs/
  skills.md               # full index, by modality and technique, with ownership notes
  getting-started.md       # skill-vs-tool distinction; Claude Code / ChatGPT / local-LLM setup
registry.yaml              # machine-readable discovery index — one entry per skill (agent-consumable)
.claude-plugin/plugin.json # Claude Code plugin manifest (lists all skill directories)
integration-templates/      # drop-in Cursor / Windsurf rules
requirements.txt             # consolidated pip dependencies across all skills
scan_skills.py                # validator — frontmatter, sections, links, and registry consistency
```

Two-tier categories today: `optical-imaging` (suite2p / caiman / fiber-photometry / voltage-imaging),
`spike-recording` (spikeinterface / spike-train-stats), `animal-behavior-tracking` (deeplabcut /
sleap / kinematics), `cognitive-computational-modeling` (hbayesdm / ddm-python / pymc-cognitive).

## Status

**37 skills** (21 flat + 4 two-tier categories + 12 leaves) plus 22 nested references — spanning EEG,
MEG, intracranial (ECoG/sEEG/DBS-LFP), fNIRS, sleep PSG, fMRI, structural and diffusion MRI, PET,
spike recording, calcium imaging (suite2p/caiman), fiber photometry, voltage imaging, animal behavior
tracking (DeepLabCut/SLEAP), human psychophysics, eye tracking, psychophysiology (incl. EMG),
experimental design, optogenetics/chemogenetics, human/clinical brain stimulation, histology and
anatomical tracing, EM connectomics, biophysical and cognitive computational modeling, data standards
(BIDS/NWB) and dataset access, statistics, connectivity, decoding/encoding, clinical biomarker ML,
literature search, and figures. See [docs/skills.md](docs/skills.md) for the full index and ownership
notes. Run `python3 scan_skills.py` to validate structure + registry (also enforced in CI). See
[CONTRIBUTING.md](CONTRIBUTING.md) to add a skill — known gaps are listed at the bottom of the index.

## License

MIT — see [LICENSE.md](LICENSE.md).
