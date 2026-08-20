---
name: neuro-data-standards
description: The two dominant neuroscience data organization standards — BIDS (MRI/EEG/MEG/iEEG) and NWB (electrophysiology/calcium imaging/behavior) — what they are, how to validate/query a dataset against them, and practical code for fetching real public datasets that use them (DANDI, OpenNeuro, Allen Institute). Use this both to understand a dataset's structure and to actually get one.
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: References target pybids 0.16+, pynwb 2.x, dandi-cli/python 0.60+, openneuro-py 2024.x, allensdk 2.16+.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  category: neuro-data-standards
---

# Neuroscience Data Standards

## Overview

BIDS (Brain Imaging Data Structure) and NWB (Neurodata Without Borders) solve the same problem —
letting code query a dataset's structure without hand-coding a study's specific file-naming
conventions — for different modality families. BIDS covers MRI, EEG, MEG, and iEEG; NWB covers
electrophysiology, calcium imaging, and behavioral data. Neither is optional infrastructure to skip
past — nearly every acquisition and preprocessing skill in this repo assumes one or the other.

## When to use this skill

Activate when the request involves:
- BIDS, NWB, Neurodata Without Borders, dataset organization/validation, DANDI, OpenNeuro,
  Allen Institute, public dataset access
- File formats: `.nwb`, BIDS directory structure
- "Is this dataset BIDS-valid," "download data from DANDI/OpenNeuro/Allen," "query this NWB file's structure"

**Practical dataset-fetching code (DANDI, OpenNeuro, Allen Institute) is in
[references/dataset-access.md](references/dataset-access.md)** — this file covers the standards
themselves; the reference covers actually getting data that uses them.

## BIDS — querying structure

```python
from bids import BIDSLayout

layout = BIDSLayout("my_bids_dataset")
subjects = layout.get_subjects()
tasks = layout.get_tasks()
bold_files = layout.get(subject="01", task="pixar", suffix="bold", extension=".nii.gz")
```

## NWB — reading a file's structure and contents

```python
from pynwb import NWBHDF5IO

with NWBHDF5IO("session.nwb", "r") as io:
    nwbfile = io.read()
    units = nwbfile.units.to_dataframe()          # sorted spike units, if present
    print(list(nwbfile.acquisition.keys()))         # raw acquired signal streams, if present
```

## Validation & Pitfalls

Canonical references: Gorgolewski et al. (2016), "The brain imaging data structure, a format for
organizing and describing outputs of neuroimaging experiments," *Scientific Data*, for BIDS; Rübel et
al. (2022), "The Neurodata Without Borders ecosystem for neurophysiological data science," *eLife*,
for NWB.

- **"Valid" does not mean "complete."** A dataset can pass BIDS/NWB validation while still missing
  optional-but-useful fields (`events.tsv` for every run, full subject metadata) — check what's
  actually present for the subjects/data you need rather than assuming a field exists.
- **Schema version varies across datasets for both standards.** An NWB file from 2019 and one from
  2025 can use different schema versions with different field locations for the same concept; code
  written against one dataset's structure can silently return the wrong thing (or nothing) on
  another. Check the actual schema of the specific dataset in use.
- **A standard describing *how data is organized* says nothing about whether the data is
  preprocessed.** Raw BIDS/NWB data still needs modality-appropriate preprocessing (see the relevant
  modality skill) before analysis — don't conflate "the file is standards-compliant" with
  "the file is analysis-ready."
