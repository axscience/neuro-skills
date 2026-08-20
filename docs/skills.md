# Skill index

**37 skills** (21 flat + 4 two-tier categories + 12 leaves) and 22 nested references. The
machine-readable version is [`registry.yaml`](../registry.yaml); this file is the human index. Run
`python3 scan_skills.py` to validate structure + registry before regenerating by hand.

Two-tier categories (a router `SKILL.md` over per-tool/per-method leaf skills) are marked **▸** below.

## By modality (recording/imaging data)

| Modality | Skill(s) |
|---|---|
| EEG | [electrophysiology](../electrophysiology/SKILL.md) → [references/eeg.md](../electrophysiology/references/eeg.md), [references/time-frequency-analysis.md](../electrophysiology/references/time-frequency-analysis.md), [references/epilepsy-eeg.md](../electrophysiology/references/epilepsy-eeg.md), [references/eeg-fmri-simultaneous.md](../electrophysiology/references/eeg-fmri-simultaneous.md) |
| MEG | [electrophysiology](../electrophysiology/SKILL.md) → [references/meg.md](../electrophysiology/references/meg.md) |
| ECoG / sEEG / DBS-LFP | [electrophysiology](../electrophysiology/SKILL.md) → [references/intracranial.md](../electrophysiology/references/intracranial.md) |
| fNIRS | [fnirs](../fnirs/SKILL.md) |
| Sleep PSG | [sleep-eeg](../sleep-eeg/SKILL.md) |
| fMRI | [mri](../mri/SKILL.md) → [references/fmri.md](../mri/references/fmri.md) |
| Structural MRI | [mri](../mri/SKILL.md) → [references/structural.md](../mri/references/structural.md) |
| Diffusion MRI | [mri](../mri/SKILL.md) → [references/diffusion.md](../mri/references/diffusion.md) |
| PET | [pet-imaging](../pet-imaging/SKILL.md) |
| Spikes / single-unit / extracellular | **▸** [spike-recording](../spike-recording/SKILL.md) → [spikeinterface](../spike-recording/spikeinterface/SKILL.md) (sorting), [spike-train-stats](../spike-recording/spike-train-stats/SKILL.md) (analysis) |
| Calcium / photometry / voltage imaging | **▸** [optical-imaging](../optical-imaging/SKILL.md) → [suite2p](../optical-imaging/suite2p/SKILL.md), [caiman](../optical-imaging/caiman/SKILL.md), [fiber-photometry](../optical-imaging/fiber-photometry/SKILL.md), [voltage-imaging](../optical-imaging/voltage-imaging/SKILL.md) |
| Animal pose/kinematics | **▸** [animal-behavior-tracking](../animal-behavior-tracking/SKILL.md) → [deeplabcut](../animal-behavior-tracking/deeplabcut/SKILL.md), [sleap](../animal-behavior-tracking/sleap/SKILL.md), [kinematics](../animal-behavior-tracking/kinematics/SKILL.md) |
| Human psychophysics/behavior | [human-psychophysics](../human-psychophysics/SKILL.md) |
| Eye tracking | [eye-tracking](../eye-tracking/SKILL.md) |
| SCR/HRV/respiration | [psychophysiology](../psychophysiology/SKILL.md) |
| EMG | [psychophysiology](../psychophysiology/SKILL.md) → [references/emg.md](../psychophysiology/references/emg.md) |
| EM connectomics | [connectomics-em](../connectomics-em/SKILL.md) |

Optogenetics/chemogenetics and brain stimulation are interventions, not recordings — see the
technique table below.

## By technique (analysis, modeling, and cross-cutting methodology)

| Technique | Skill |
|---|---|
| Optogenetics / chemogenetics (animal causal manipulation) | [optogenetics-chemogenetics](../optogenetics-chemogenetics/SKILL.md) |
| TMS-EEG, tDCS/tACS, clinical stimulation (human/clinical) | [brain-stimulation](../brain-stimulation/SKILL.md) → [references/tms-eeg.md](../brain-stimulation/references/tms-eeg.md), [references/tes.md](../brain-stimulation/references/tes.md), [references/clinical-stimulation.md](../brain-stimulation/references/clinical-stimulation.md) |
| Viral tracing, IHC, tissue clearing, cell counting | [histology-and-anatomical-tracing](../histology-and-anatomical-tracing/SKILL.md) |
| Task/stimulus delivery, trigger coding, timing sync | [experimental-design](../experimental-design/SKILL.md) |
| Biophysical/network simulation (NEURON/Brian2/NEST) | [computational-modeling](../computational-modeling/SKILL.md) |
| Behavioral/decision modeling (RL, DDM, Bayesian observer) | **▸** [cognitive-computational-modeling](../cognitive-computational-modeling/SKILL.md) → [hbayesdm](../cognitive-computational-modeling/hbayesdm/SKILL.md), [ddm-python](../cognitive-computational-modeling/ddm-python/SKILL.md), [pymc-cognitive](../cognitive-computational-modeling/pymc-cognitive/SKILL.md) |
| BIDS/NWB standards + practical dataset access (DANDI/OpenNeuro/Allen) | [neuro-data-standards](../neuro-data-standards/SKILL.md) → [references/dataset-access.md](../neuro-data-standards/references/dataset-access.md) |
| Cluster permutation, multiple comparisons, mixed models, power analysis | [neuro-stats](../neuro-stats/SKILL.md) → [references/clinical-stats.md](../neuro-stats/references/clinical-stats.md) (survival analysis, longitudinal, ComBat) |
| Coherence, Granger causality, DCM, graph theory | [neuro-connectivity](../neuro-connectivity/SKILL.md) |
| Decoding, encoding (TRF/mTRF, RSA), population dynamics | [neuro-decoding-encoding](../neuro-decoding-encoding/SKILL.md) → [references/leakage_and_splitting.md](../neuro-decoding-encoding/references/leakage_and_splitting.md), [references/population-dynamics-deep-learning.md](../neuro-decoding-encoding/references/population-dynamics-deep-learning.md) |
| Diagnostic/prognostic ML, clinical scales | [clinical-biomarkers-ml](../clinical-biomarkers-ml/SKILL.md) → [references/clinical-assessment.md](../clinical-biomarkers-ml/references/clinical-assessment.md) |
| Meta-analysis across published fMRI studies | [mri](../mri/SKILL.md) → [references/meta-analysis.md](../mri/references/meta-analysis.md) |
| Literature search | [neuro-lit-search](../neuro-lit-search/SKILL.md) |
| Figures | [neuro-figures](../neuro-figures/SKILL.md) |

## Ownership notes (read before adding overlapping content)

- **fMRI connectivity**: same-modality ROI-to-ROI correlation lives in `mri/references/fmri.md`.
  Cross-modality, effective (Granger/DCM), or graph-theoretic connectivity lives in
  `neuro-connectivity`. Don't duplicate one in the other.
- **Dataset access vs. data standards**: `neuro-data-standards/SKILL.md` covers what BIDS/NWB *are*;
  `references/dataset-access.md` covers practical fetch code (DANDI, OpenNeuro, Allen). New
  acquisition code belongs in the reference, not scattered into modality skills.
- **Clinical epilepsy EEG vs. sleep EEG**: `electrophysiology/references/epilepsy-eeg.md` (interictal
  discharges, seizure detection) and `sleep-eeg/SKILL.md` (PSG staging) are both clinical EEG but
  different disciplines with different tooling — kept separate deliberately.
- **EEG/MEG source localization**: lives in `electrophysiology/references/meg.md` since MEG is where
  it's most commonly used, but the methods and code apply to EEG source localization too (at lower
  spatial resolution) — check there even if your data is EEG-only.

## Known gaps

Not yet covered: genomics/transcriptomics of neural tissue (out of scope by design — molecular data,
not neural recording/behavior), functional ultrasound, closed-loop/real-time BCI (compositionally
covered by combining `neuro-decoding-encoding` + `brain-stimulation`/`optogenetics-chemogenetics`,
doesn't need its own skill), and generic reproducible-pipeline/workflow-manager tooling (software
engineering practice, not neuroscience domain knowledge).

## Adding a skill

See [CONTRIBUTING.md](../CONTRIBUTING.md) — placement (new modality vs. new reference vs. new
cross-cutting skill) is the first decision to get right, before writing content.
