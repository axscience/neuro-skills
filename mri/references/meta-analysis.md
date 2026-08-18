# Coordinate-Based Meta-Analysis

Modality-specific detail for [../SKILL.md](../SKILL.md). Combines reported activation coordinates
(peak voxel locations, typically in MNI/Talairach space) across many published fMRI studies to find
regions consistently implicated across a literature — distinct from a within-study GLM or
connectivity analysis, and distinct from a text-based literature search (`neuro-lit-search`).

## Activation Likelihood Estimation (ALE) via NiMARE

```python
import nimare
from nimare.dataset import Dataset
from nimare.meta.cbma.ale import ALE
from nimare.correct import FWECorrector

# dataset: built from a set of studies' reported peak coordinates + sample sizes,
# either hand-curated or pulled from a coordinate database (e.g. Neurosynth, NeuroVault)
dataset = Dataset.load("my_coordinate_dataset.pkl.gz")

ale = ALE()
results = ale.fit(dataset)

corrector = FWECorrector(method="montecarlo", n_iters=1000)
corrected_results = corrector.transform(results)
```

## Querying existing coordinate databases (Neurosynth-style)

```python
from nimare.extract import fetch_neurosynth
from nimare.io import convert_neurosynth_to_dataset

files = fetch_neurosynth(data_dir="neurosynth_data", version="7")
neurosynth_dataset = convert_neurosynth_to_dataset(
    coordinates_file=files[0]["coordinates"],
    metadata_file=files[0]["metadata"],
)
```

This gives access to tens of thousands of studies' reported coordinates without manually curating a
study set — useful for large-scale, exploratory meta-analysis, though with less curatorial control
over study inclusion criteria than a hand-built dataset for a focused question.

## Validation & Pitfalls

Canonical references: Eickhoff et al. (2012), "Activation likelihood estimation meta-analysis
revisited," *NeuroImage*, for the ALE algorithm; Yarkoni et al. (2011), "Large-scale automated
synthesis of human functional neuroimaging data," *Nature Methods*, for the Neurosynth approach this
builds on.

- **Coordinate-based meta-analysis discards the actual statistical maps and uses only peak
  locations** — this is a real information loss relative to image-based meta-analysis (when full
  statistical maps are available), and means results are sensitive to how studies report peaks
  (some report many, some only the single global maximum per contrast).
- **Study selection criteria drive the result as much as the underlying neuroscience.** A meta-
  analysis of "reward processing" studies will produce different results depending on inclusion
  criteria (task type, contrast direction, threshold used by the original studies) — report the
  selection criteria explicitly; they're not a neutral preprocessing step.
- **Automated large-scale databases (Neurosynth) use text-mining to associate studies with terms, not
  expert curation.** A term-based query can pull in studies where the term appears incidentally
  (e.g. in a discussion section) rather than being the study's actual focus — treat automated-database
  results as a broader, noisier signal than a hand-curated meta-analysis, not an equivalent
  replacement.
- **Multiple-comparison correction is still required at the meta-analytic level** — ALE's Monte
  Carlo FWE correction (above) addresses this, but skipping it (reporting uncorrected ALE maps) is a
  common and serious error, same as skipping correction in a single-study GLM.
