# Clinical Stimulation (DBS Programming, Presurgical Mapping)

Modality-specific detail for [../SKILL.md](../SKILL.md). Deep brain stimulation (DBS) is an
implanted, chronic stimulation therapy (Parkinson's, essential tremor, dystonia, and increasingly
psychiatric indications); presurgical mapping (cortical stimulation mapping, often during epilepsy
surgery workups) uses stimulation to functionally localize eloquent cortex before resection.

## DBS electrode localization (research use — Lead-DBS)

```matlab
% Lead-DBS (MATLAB) is the standard tool for reconstructing implanted DBS
% electrode positions from post-operative CT/MRI, registered to a normalized
% template space for group-level analysis of stimulation site vs. outcome.
ea_reconstruct;  % localizes electrode contacts from post-op imaging
```

```python
# Relating contact position / stimulation parameters to clinical outcome typically
# combines Lead-DBS's localization output with a volume-of-tissue-activated (VTA)
# model and an outcome measure (e.g. UPDRS motor score change) — a structural MRI +
# stimulation-parameter regression problem, using the mri skill's tooling for the
# imaging side once electrode positions are exported.
```

## Presurgical cortical stimulation mapping

```python
# Direct cortical stimulation mapping (via implanted ECoG grids, in an epilepsy
# monitoring unit) delivers brief current pulses to pairs of electrodes and
# records the behavioral/functional response (e.g. speech arrest, movement) —
# this is functional localization via causal perturbation, complementary to
# passive high-gamma mapping (electrophysiology/references/intracranial.md) which
# infers function from natural task-evoked activity rather than direct stimulation.

def summarize_mapping_results(stimulation_sites, behavioral_responses):
    """stimulation_sites: electrode pair per stimulation; behavioral_responses:
    clinician-annotated response (e.g. 'speech arrest', 'no response', 'afterdischarge')."""
    import pandas as pd
    return pd.DataFrame({"site": stimulation_sites, "response": behavioral_responses}).groupby("response").size()
```

## Validation & Pitfalls

Canonical references: Horn & Kühn (2015), "Lead-DBS: a toolbox for deep brain stimulation electrode
localizations and visualizations," *NeuroImage*; Ojemann et al. (1989), "Cortical language
localization in left, dominant hemisphere," *Journal of Neurosurgery*, for cortical stimulation
mapping methodology.

- **Electrode localization accuracy directly limits the precision of any stimulation-site-to-outcome
  claim** — post-operative imaging artifact from the implanted hardware itself (metal artifact on CT/
  MRI) degrades localization precision near the electrode; report localization uncertainty, don't
  treat reconstructed contact positions as exact coordinates.
- **Clinical stimulation parameters (contact selection, amplitude, frequency, pulse width) are
  typically optimized by a clinician through iterative programming, not fixed at implant** — a
  research analysis relating "the" stimulation site/parameters to outcome needs to account for
  parameter changes over the observation period, not treat the initial or a single snapshot setting
  as representative throughout.
- **Cortical stimulation mapping results depend on current spread beyond the stimulated
  electrode pair, which varies with amplitude and tissue conductivity** — a negative mapping result
  (no observed function at a site) does not definitively rule out function there; it may reflect
  insufficient current spread to that specific region at the tested amplitude, a distinction that
  matters clinically (a false negative risks resecting functional tissue).
- **Afterdischarges (localized seizure-like activity triggered by stimulation itself) can confound
  interpretation of a behavioral response during mapping** — a "response" to stimulation coinciding
  with an afterdischarge on simultaneous EEG monitoring should be flagged and not attributed
  straightforwardly to the stimulated region's normal function.
