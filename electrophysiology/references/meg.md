# MEG — Source Localization

Modality-specific detail for [../SKILL.md](../SKILL.md). MEG's distinguishing analysis need beyond
the shared preprocessing pipeline is source localization: estimating cortical source activity from
sensor-level data. (Everything here applies to EEG source localization too, at lower spatial
resolution — the same MNE-Python tools and forward-model machinery are shared.)

## Build the forward model

```python
import mne

bem = mne.make_bem_model(subject="sub-01", subjects_dir="freesurfer_subjects")
bem_solution = mne.make_bem_solution(bem)
src = mne.setup_source_space(subject="sub-01", subjects_dir="freesurfer_subjects", spacing="oct6")

forward = mne.make_forward_solution(raw.info, trans="sub-01-trans.fif", src=src, bem=bem_solution)
```

## Minimum-norm estimation

```python
noise_cov = mne.compute_covariance(epochs, tmax=0.0)  # from pre-stimulus baseline

inverse_operator = mne.minimum_norm.make_inverse_operator(
    evoked.info, forward, noise_cov, loose=0.2, depth=0.8
)
stc = mne.minimum_norm.apply_inverse(evoked, inverse_operator, lambda2=1.0 / 9.0, method="dSPM")
```

## LCMV beamforming (better for focal, well-separated sources; assumes uncorrelated sources)

```python
data_cov = mne.compute_covariance(epochs, tmin=0.0, tmax=0.5)

filters = mne.beamformer.make_lcmv(
    evoked.info, forward, data_cov, reg=0.05, noise_cov=noise_cov, pick_ori="max-power"
)
stc_beamformer = mne.beamformer.apply_lcmv(evoked, filters)
```

## Method choice

| | Minimum-norm (MNE/dSPM/sLORETA) | LCMV beamforming |
|---|---|---|
| Assumption | Simplest (lowest-energy) distributed solution | Sources are spatially uncorrelated |
| Good for | Distributed activity, trial-averaged evoked responses | Focal sources; single-trial or induced (non-phase-locked) activity |
| Weak point | Blurs/spreads focal sources | Underestimates or cancels correlated bilateral sources |

If the two methods substantially disagree on a result central to a claim, that disagreement is
informative — report it rather than picking whichever method gives the preferred answer.

## Extracting an anatomical ROI time course

```python
labels = mne.read_labels_from_annot("sub-01", parc="aparc", subjects_dir="freesurfer_subjects")
motor_label = [l for l in labels if l.name == "precentral-lh"][0]
roi_timecourse = stc.extract_label_time_course(motor_label, src=forward["src"], mode="mean_flip")
```

Use `mode="mean_flip"`, not `"mean"` — raw averaging across vertices can cancel real signal because
adjacent vertices' estimated source orientations can have opposite sign for the same underlying
activity; `mean_flip` corrects for this.

## Validation & Pitfalls (MEG-specific, in addition to ../SKILL.md's shared list)

Canonical references: Hämäläinen & Ilmoniemi (1994), "Interpreting magnetic fields of the brain:
minimum norm estimates," *Medical & Biological Engineering & Computing*; Van Veen et al. (1997) for
LCMV beamforming, *IEEE Transactions on Biomedical Engineering*.

- **Source localization is fundamentally underdetermined.** Every method's output reflects its own
  assumption, not ground truth — state which method was used and why when reporting results.
- **A wrong or approximate coregistration (`trans` file) between sensor space and MRI anatomy
  produces plausible-looking but wrong source estimates.** This fails silently, not loudly — verify
  with `mne.viz.plot_alignment` before trusting results.
- **Using `fsaverage` (template anatomy) instead of subject-specific FreeSurfer reconstruction trades
  precision for convenience** — a reasonable choice, but state which was used; it changes what "this
  activity is in region X" means.
- **Source-space statistics need the same multiple-comparisons correction as any other high-
  dimensional space** — use `mne.stats.spatio_temporal_cluster_1samp_test`, not per-vertex
  uncorrected tests.
