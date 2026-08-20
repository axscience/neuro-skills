---
name: fnirs
description: Functional near-infrared spectroscopy (fNIRS) preprocessing and analysis with MNE-NIRS — optode array handling, conversion to hemoglobin concentration (HbO/HbR), motion artifact correction, and GLM-based analysis. Use this for fNIRS specifically — it's optical, not electrical, and uses a different pipeline than EEG/MEG despite sharing scalp-mounted hardware conventions.
license: BSD-3-Clause
allowed-tools: Read Write Edit Bash
compatibility: Examples target MNE-NIRS 0.6+ (built on MNE-Python).
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  category: fnirs
---

# fNIRS

## Overview

fNIRS measures relative changes in oxygenated (HbO) and deoxygenated (HbR) hemoglobin concentration
via near-infrared light absorption — a hemodynamic signal, like fMRI's BOLD, but recorded optically
at the scalp with much better temporal resolution and much worse spatial resolution/depth
sensitivity than fMRI. It shares MNE-Python's ecosystem (via the MNE-NIRS extension) but the
processing pipeline — converting raw light intensity to hemoglobin concentration — is fNIRS-specific
and has no EEG/MEG equivalent.

## When to use this skill

Activate when the request involves:
- fNIRS, near-infrared spectroscopy, optode, HbO, HbR, hemoglobin concentration
- File formats: `.nirs`, `.snirf`
- Terms: MNE-NIRS, optical density, Beer-Lambert, scalp coupling index
- "Analyze my fNIRS recording," "convert to hemoglobin concentration," "check optode coupling"

## Core usage

### Load and convert raw intensity to optical density, then hemoglobin concentration

```python
import mne
from mne_nirs.preprocessing import peak_power

raw_intensity = mne.io.read_raw_nirx("nirs_recording", preload=True)
raw_od = mne.preprocessing.nirs.optical_density(raw_intensity)
raw_haemo = mne.preprocessing.nirs.beer_lambert_law(raw_od, ppf=6.0)
# raw_haemo now has channels split into hbo/hbr pairs per source-detector pair
```

### Motion artifact correction

```python
from mne.preprocessing.nirs import temporal_derivative_distribution_repair

raw_haemo_corrected = temporal_derivative_distribution_repair(raw_haemo)
```

### Channel-quality screening (scalp coupling index)

```python
sci = mne.preprocessing.nirs.scalp_coupling_index(raw_od)
raw_od.info["bads"] = list(raw_od.ch_names[i] for i, s in enumerate(sci) if s < 0.5)
```

### GLM analysis (same conceptual approach as fMRI's task GLM — see mri/references/fmri.md)

```python
from mne_nirs.statistics import run_glm
from mne_nirs.experimental_design import make_first_level_design_matrix

design_matrix = make_first_level_design_matrix(raw_haemo, stim_dur=5.0)
glm_est = run_glm(raw_haemo, design_matrix)
```

## Validation & Pitfalls

Canonical reference: Yücel et al. (2021), "Best practices for fNIRS publications," *Neurophotonics* —
a consensus methods paper specifically addressing the pitfalls below.

- **Scalp coupling index screening is required, not optional.** Poor optode-scalp contact (hair
  blocking light, poor fit) produces channels with no real physiological signal that can still look
  like data — always screen and exclude low-SCI channels before analysis, not just visually inspect
  traces.
- **The differential path length factor (`ppf` above) affects the absolute scale of derived
  concentration changes and varies by wavelength, age, and tissue — a default value is an
  approximation, not a measurement.** This matters most for claims about absolute concentration
  magnitude; relative/statistical comparisons within a study are more robust to this than absolute
  values compared across studies using different assumed PPF values.
- **fNIRS has poor depth sensitivity and cannot distinguish cortical signal from superficial
  scalp/skull hemodynamics without correction.** Short-separation channels (source-detector pairs a
  few mm apart, sensitive mainly to superficial tissue) should be used as a regressor to remove
  systemic/superficial contamination when available — a pipeline without this correction is prone to
  reporting scalp blood flow changes as cortical activity.
- **Motion artifacts are pervasive and distinct from EEG's artifact profile** — large, often
  non-physiological deflections from optode movement rather than eye blinks/muscle. Confirm a motion
  correction step (like the temporal derivative distribution repair above) is actually applied and
  effective, not just filtering as in EEG.
- **HbO and HbR often (not always) show opposite-signed responses to genuine neural activity** — a
  result reporting only one without checking the other misses a standard internal consistency check;
  discordant HbO/HbR direction is a common flag for a motion or systemic artifact rather than real
  activity.
