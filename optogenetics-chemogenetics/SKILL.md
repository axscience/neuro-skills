---
name: optogenetics-chemogenetics
description: Causal manipulation of neural circuits in animal research via optogenetics (light-gated opsins) and chemogenetics (DREADDs) — experimental design (opsin/promoter selection, viral targeting, light delivery parameters), and analysis of stimulation-locked effects on behavior or recorded activity. Sibling to brain-stimulation (which covers human/clinical non-invasive and invasive stimulation) — different tooling, different audience.
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: This skill is primarily experimental-design and analysis guidance rather than a specific software package — analysis code uses numpy/pandas/matplotlib/scipy, standard for the stimulation-locked analyses described.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  category: optogenetics-chemogenetics
---

# Optogenetics and Chemogenetics

## Overview

Optogenetics (light-gated ion channels/pumps expressed via viral or transgenic methods, activated
with fiber-coupled light) and chemogenetics (DREADDs — engineered receptors activated by an otherwise
inert ligand) are the dominant causal-manipulation tools in circuit neuroscience — enabling
cell-type-specific and (for optogenetics) millisecond-timescale activation or silencing that
electrical/pharmacological methods can't match. This skill covers the experimental-design choices
that determine whether a manipulation is interpretable, and the standard analyses for
stimulation-locked effects.

## When to use this skill

Activate when the request involves:
- Optogenetics, opsin, ChR2, halorhodopsin, chemogenetics, DREADD, CNO, DCZ, causal manipulation
- Terms: viral targeting, light delivery, fiber-coupled stimulation, sufficiency/necessity
- "Design an optogenetics experiment," "analyze stimulation-locked behavior," "pick a DREADD ligand"

## Core usage

### Choosing an approach

| | Optogenetics | Chemogenetics (DREADDs) |
|---|---|---|
| Temporal precision | Milliseconds | Minutes to hours (ligand pharmacokinetics) |
| Typical use | Testing a circuit's causal role in a specific behavioral epoch/event | Testing a circuit's role over a sustained period (e.g. an entire session) |
| Hardware needed | Fiber-coupled light source, implanted fiber/cannula | None beyond ligand delivery (injection or in drinking water) |
| Common failure mode | Light-induced tissue heating/artifact, insufficient opsin expression | Ligand off-target effects (older CNO-based DREADDs — see pitfalls), slow onset limiting temporal claims |

### Stimulation-locked behavioral effect analysis

```python
import numpy as np
from scipy import stats

def stimulation_effect(behavioral_measure, stim_epochs, control_epochs):
    """
    behavioral_measure: (n_trials,) e.g. time spent in a zone, response latency
    stim_epochs, control_epochs: boolean masks over trials
    """
    stim_values = behavioral_measure[stim_epochs]
    control_values = behavioral_measure[control_epochs]
    t_stat, p_value = stats.ttest_ind(stim_values, control_values)
    effect_size = (stim_values.mean() - control_values.mean()) / np.sqrt(
        (stim_values.var() + control_values.var()) / 2
    )
    return {"t": t_stat, "p": p_value, "cohens_d": effect_size}
```

### Stimulation-locked neural effect (if recording during stimulation — combine with `spike-recording`/`optical-imaging`)

```python
def peri_stimulation_response(spike_times, stim_onsets, window=(-1, 3)):
    """Same peri-event alignment pattern as spike-recording's PSTH — stimulation
    onset takes the role of the event."""
    return [
        spikes[(spikes >= onset + window[0]) & (spikes < onset + window[1])] - onset
        for onset in stim_onsets for spikes in [np.asarray(spike_times)]
    ]
```

## Validation & Pitfalls

Canonical references: Boyden et al. (2005), "Millisecond-timescale, genetically targeted optical
control of neural activity," *Nature Neuroscience*, for optogenetics; Roth (2016), "DREADDs for
Neuroscientists," *Neuron*, for chemogenetics and its pitfalls specifically.

- **Light delivery itself can produce behavioral/physiological artifacts independent of opsin
  activation** — heating, visible light leakage the animal can perceive, or the implant/tether itself
  affecting behavior. A no-opsin (or opsin-negative) light-delivery control condition is required to
  attribute an effect to the opsin's activity, not the light delivery procedure.
- **CNO (clozapine-N-oxide), the classic DREADD ligand, back-converts to clozapine in vivo at
  behaviorally relevant doses** — a well-documented confound (Gomez et al. 2017, *Science*) that can
  produce off-target effects mimicking or masking the DREADD-specific effect. Current best practice
  favors newer ligands (e.g. deschloroclozapine, DCZ) with cleaner pharmacokinetics, or at minimum
  requires a no-DREADD, ligand-only control group — don't run a DREADD study without this control.
- **Opsin/DREADD expression level and location vary across animals and need verification, not
  assumption.** Post-hoc histological confirmation of expression location and approximate density
  (see `histology-and-anatomical-tracing`) is standard practice, not optional — a "manipulation had no
  effect" result is uninterpretable without knowing the manipulation actually hit the intended
  circuit in that animal.
- **Off-target viral spread beyond the intended region is common and rarely zero** — report and, where
  possible, quantify the actual spread (from histology) rather than assuming injection coordinates
  guarantee targeting precision.
- **Silencing and activation are not symmetric manipulations for interpreting a circuit's function** —
  a behavioral effect from activating a circuit doesn't imply the same circuit is necessary for that
  behavior under normal conditions (sufficiency vs. necessity), and vice versa for silencing. State
  which claim the specific manipulation actually supports.
