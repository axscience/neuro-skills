# Time-Frequency / Oscillatory Analysis

Spans EEG, MEG, and intracranial recordings — spectral power, event-related (de)synchronization,
inter-trial coherence, and phase-amplitude coupling. As central to cognitive/sensory EEG-MEG work as
ERP/ERF analysis, and easy to omit by mistake since it doesn't come up in a basic preprocessing
pipeline.

## Time-frequency decomposition (Morlet wavelets)

```python
import numpy as np
import mne

freqs = np.arange(4, 40, 1)  # Hz
n_cycles = freqs / 2.0        # more cycles at higher frequencies = better frequency resolution there

power = epochs.compute_tfr(
    method="morlet", freqs=freqs, n_cycles=n_cycles,
    use_fft=True, return_itc=False, average=False,
)
```

## Inter-trial coherence (ITC) — phase consistency across trials

```python
power, itc = epochs.compute_tfr(
    method="morlet", freqs=freqs, n_cycles=n_cycles, return_itc=True, average=True,
)
# itc values near 1: phase is consistent across trials at that time-frequency point (evoked, phase-locked)
# itc values near 0: phase is random across trials (induced activity, or no response)
```

## Event-related (de)synchronization — power change relative to baseline

```python
power_db = power.copy()
power_db.apply_baseline(baseline=(-0.5, -0.2), mode="logratio")  # dB-like relative change
```

`mode="logratio"` (or `"percent"`) is standard for oscillatory power specifically — unlike ERP
baseline correction (simple subtraction), because oscillatory power is strictly positive and its
variance scales with its mean, so a ratio-based baseline correction is the appropriate normalization,
not subtraction.

## Phase-amplitude coupling (cross-frequency coupling)

```python
from scipy.signal import hilbert

def modulation_index(low_freq_signal, high_freq_envelope, n_bins=18):
    """Tort et al. (2010) modulation index — how much a high-frequency amplitude
    is modulated by a low-frequency phase."""
    phase = np.angle(hilbert(low_freq_signal))
    bins = np.linspace(-np.pi, np.pi, n_bins + 1)
    mean_amp = np.array([
        high_freq_envelope[(phase >= bins[i]) & (phase < bins[i + 1])].mean()
        for i in range(n_bins)
    ])
    p = mean_amp / mean_amp.sum()
    entropy = -np.sum(p * np.log(p + 1e-12))
    max_entropy = np.log(n_bins)
    return (max_entropy - entropy) / max_entropy  # 0 = no coupling, higher = more coupling
```

## Validation & Pitfalls

Canonical references: Tallon-Baudry & Bertrand (1999), "Oscillatory gamma activity in humans and its
role in object representation," *Trends in Cognitive Sciences*, for evoked-vs-induced power; Tort et
al. (2010), "Measuring phase-amplitude coupling between neuronal oscillations of different
frequencies," *Journal of Neurophysiology*, for the modulation index above.

- **Wavelet cycle count trades time resolution against frequency resolution — there's no free
  choice.** More cycles gives better frequency resolution and worse time resolution at a given
  frequency, and vice versa. State the choice; don't present it as a neutral default.
- **Evoked (phase-locked, visible in the ERP) and induced (non-phase-locked) power are different
  phenomena and get conflated constantly.** High ITC at a time-frequency point means the response is
  evoked; low ITC with high power means induced activity the ERP average would wash out entirely.
- **Baseline period choice affects every downstream time-frequency value**, same as for ERP
  baselines, but more sensitive — a baseline window with any residual task-related activity from a
  prior trial distorts the ratio for the whole epoch, not just an additive offset.
- **Phase-amplitude coupling is easy to compute and easy to over-interpret.** A nonzero modulation
  index doesn't establish the coupling is functionally meaningful rather than a filtering artifact —
  compare against a surrogate/shuffled-phase null distribution before treating a coupling value as
  real.
