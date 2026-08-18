# Electromyography

Modality-specific detail for [../SKILL.md](../SKILL.md). EMG measures electrical activity from
muscle fiber contraction — used for motor control research (muscle synergies, motor unit
decomposition) and, in a simpler form, as a psychophysiological measure (facial EMG for affective
response) grouped alongside SCR/HRV/respiration.

## Preprocessing

```python
import neurokit2 as nk

emg_signals, info = nk.emg_process(emg_raw, sampling_rate=1000)
emg_amplitude = emg_signals["EMG_Amplitude"]   # rectified, smoothed envelope
onsets = info["EMG_Onsets"]
```

## Motor unit decomposition (from surface EMG — high-density arrays)

```python
# Decomposing surface EMG into individual motor unit action potential trains
# requires specialized algorithms (e.g. convolutive blind source separation) —
# typically done with dedicated tools (e.g. DEMUSE, or open decomposition
# toolboxes) rather than a general-purpose signal processing library. Conceptually:
# each detected motor unit's firing times are the output, directly analogous to
# spike-recording's sorted single-unit output, but from surface muscle recording
# rather than intramuscular/intracranial electrodes.
```

## Muscle synergy extraction (non-negative matrix factorization)

```python
from sklearn.decomposition import NMF

def extract_synergies(emg_envelopes, n_synergies):
    """emg_envelopes: (n_timepoints, n_muscles), non-negative (rectified) EMG.
    NMF finds n_synergies weighting patterns (W) and their time-varying
    activation (H) that reconstruct the multi-muscle EMG — the standard
    approach for testing whether muscle coordination reduces to a small
    number of shared activation patterns."""
    model = NMF(n_components=n_synergies, init="nndsvda", max_iter=1000)
    activation = model.fit_transform(emg_envelopes)   # (n_timepoints, n_synergies)
    synergy_weights = model.components_                # (n_synergies, n_muscles)
    return synergy_weights, activation
```

## Validation & Pitfalls

Canonical references: Merletti & Farina (eds.), *Surface Electromyography: Physiology, Engineering,
and Applications* (2016); Tresch, Cheung & d'Avella (2006), "Matrix factorization algorithms for the
identification of muscle synergies," *Journal of Neurophysiology*, for synergy extraction
methodology and its pitfalls specifically.

- **Surface EMG amplitude is affected by electrode placement relative to the muscle's innervation
  zone, and by crosstalk from adjacent muscles** — absolute amplitude comparisons across sessions or
  subjects are unreliable without careful, consistent electrode placement (and normalization, e.g. to
  a maximum voluntary contraction); within-session relative comparisons are more robust.
- **Muscle synergy count (`n_synergies`) is a free parameter that needs a principled selection
  criterion (e.g. variance-accounted-for threshold), not an assumed value.** Choosing the number of
  synergies to match a hypothesis, rather than by a pre-specified data-driven criterion, is a common
  and serious analytic-flexibility problem in this literature.
- **NMF's non-negativity constraint and the initialization method affect the specific solution found
  — results can differ across runs with different random initialization.** Check solution stability
  across multiple initializations before treating a specific set of synergies as "the" answer.
- **Motor unit decomposition accuracy depends heavily on electrode density and signal quality** — a
  decomposition from a low-channel-count or noisy recording should be treated with more skepticism
  about individual motor unit identity accuracy than one from a high-density array with good SNR.
