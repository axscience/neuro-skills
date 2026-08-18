# TMS-EEG

Modality-specific detail for [../SKILL.md](../SKILL.md). Combining transcranial magnetic stimulation
with simultaneous EEG lets researchers measure a stimulated region's immediate electrophysiological
response (TMS-evoked potentials) — but the TMS pulse itself produces a massive artifact in the EEG
that dominates the standard preprocessing pipeline here.

## The TMS artifact problem

A TMS pulse induces a large electromagnetic artifact in EEG electrodes that can saturate amplifiers
for several milliseconds and produce decaying artifact for tens to hundreds of milliseconds after —
far larger than the neural signal of interest. TESA (a EEGLAB/MATLAB toolbox) is the standard tool
for the specific artifact-removal pipeline this requires.

## Core artifact-removal pipeline (TESA, conceptual — MATLAB/EEGLAB based)

```matlab
% Remove the pulse artifact window itself (amplifier saturation period)
EEG = pop_tesa_removedata(EEG, [-2, 10]);  % ms relative to pulse

% Interpolate across the removed window
EEG = pop_tesa_interpdata(EEG, 'cubic', [1, 1]);

% First-round ICA to remove the large, TMS-specific decay artifact component
EEG = pop_tesa_fastica(EEG, 'approach', 'symm');
EEG = pop_tesa_compselect(EEG, 'compCheck', 'on', 'remove', 'TMS-muscle');

% Filter (after artifact removal, not before — see pitfalls)
EEG = pop_tesa_filtbutter(EEG, 1, 100, 4, 'bandpass');

% Second-round ICA for remaining physiological artifacts (blink, muscle)
EEG = pop_tesa_fastica(EEG, 'approach', 'symm');
EEG = pop_tesa_compselect(EEG, 'compCheck', 'on');
```

## TMS-evoked potential (TEP) analysis

```python
# After TESA cleaning (typically done in MATLAB), TEPs are analyzed like any
# ERP (see electrophysiology/references/eeg.md) — trial-averaged response
# time-locked to the TMS pulse, with specific attention to early components
# (~within 50ms) reflecting more local cortical response and later components
# reflecting network-level propagation.
```

## Validation & Pitfalls

Canonical reference: Rogasch et al. (2017), "Analysing concurrent transcranial magnetic stimulation
and electroencephalographic data: A review and introduction to the open-source TESA software,"
*NeuroImage*.

- **The two-round ICA structure (before and after filtering) is specifically designed around TMS
  artifact characteristics — skipping either round or reordering the pipeline typically leaves
  residual artifact that can masquerade as an early TEP component.** Don't substitute a generic EEG
  ICA pipeline (like the standard one in `electrophysiology/references/eeg.md`) without the
  TMS-specific pulse-removal and two-stage structure.
- **Filtering before removing the pulse-artifact window can spread the artifact in time** (filter
  ringing around a sharp, large-amplitude event) — the pulse-window removal/interpolation step must
  happen before filtering, not after.
- **Auditory and somatosensory artifacts from the TMS click and scalp sensation are real confounds,
  not just electrical pickup** — a proper TMS-EEG control condition (e.g. sham stimulation, or a
  matched click sound without cortical stimulation) is needed to attribute a TEP to cortical response
  specifically rather than to the sensory experience of being stimulated.
- **Coil positioning consistency across a session (and across sessions, for longitudinal designs)
  directly determines what's actually being stimulated** — neuronavigation-guided targeting, not just
  scalp-landmark-based positioning, is standard practice for anything beyond exploratory work.
