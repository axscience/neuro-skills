---
name: voltage-imaging
description: "Voltage imaging analysis with genetically encoded voltage indicators (GEVIs) — bandpass denoising and spike detection from high-speed, low-SNR fluorescence traces. Reports membrane potential directly and much faster than calcium indicators, at far lower SNR. For calcium imaging (higher SNR, slower kinetics), use suite2p or caiman instead."
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: Examples use numpy/scipy. Frame rates are typically 500-1000+ Hz vs. ~30 Hz for calcium imaging, with correspondingly larger data volumes.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  category: optical-imaging
---

# Voltage Imaging

## Overview

Genetically encoded voltage indicators (GEVIs) report membrane potential changes directly and much
faster than calcium indicators, at the cost of substantially lower signal-to-noise ratio and much
higher required frame rates (often 500-1000+ Hz vs. ~30 Hz for calcium imaging). This is a leaf of
the `optical-imaging` category.

## When to use this skill

Activate when the request involves:
- Voltage imaging, GEVI, genetically encoded voltage indicator, ASAP/Voltron/paQuasAr-class sensors
- Terms: subthreshold voltage, high-speed imaging, spike detection from optical traces, SNR-limited
- "Detect spikes in this voltage-imaging trace," "denoise a GEVI recording," "why is my voltage SNR so low"

## Core usage

### Denoising and spike detection

The motion-correction and ROI concepts from the `suite2p`/`caiman` leaves carry over, but voltage
imaging's much lower per-frame SNR changes what's needed downstream:

```python
import numpy as np
from scipy.signal import butter, sosfiltfilt

def denoise_voltage_trace(trace, fs, low_freq=1, high_freq=200):
    """Voltage signals of interest (subthreshold + spikes) occupy a specific
    band; aggressive bandpass filtering is standard given the low raw SNR,
    unlike calcium imaging where minimal filtering is typical."""
    sos = butter(4, [low_freq, high_freq], btype="bandpass", fs=fs, output="sos")
    return sosfiltfilt(sos, trace)

def detect_spikes_from_voltage_trace(trace, threshold_std=4):
    """Simple threshold crossing — production pipelines typically use a
    template-matching or ML-based detector given the low SNR; this is the
    starting point, not a validated detector."""
    threshold = trace.mean() - threshold_std * trace.std()  # spikes are negative deflections in dF/F-style voltage traces
    from scipy.signal import find_peaks
    peaks, _ = find_peaks(-trace, height=-threshold)
    return peaks
```

## Validation & Pitfalls

Canonical reference: Villette et al. (2019), "Ultrafast two-photon imaging of a high-gain voltage
indicator in awake behaving mice," *Cell*, for a representative modern GEVI approach and its
reported SNR/frame-rate tradeoffs.

- **Per-frame SNR is fundamentally worse than calcium imaging, and no amount of post-processing fully
  compensates.** This is a physical limitation of currently available GEVIs, not a preprocessing
  failure — treat spike detection from voltage imaging as noisier than electrophysiological spike
  detection, and validate against simultaneous electrophysiology where possible rather than assuming
  single-trial detection reliability.
- **The much higher required frame rate creates a real light-exposure/photobleaching tradeoff** —
  sessions are typically shorter than calcium imaging sessions for this reason; account for
  photobleaching-driven signal decay over even short recordings.
- **Different GEVI variants have substantially different kinetics, brightness, and baseline
  fluorescence direction (some report spikes as fluorescence increases, others decreases)** — code
  written for one indicator's sign convention silently produces inverted results with another; always
  confirm sign convention for the specific indicator in use before interpreting a trace.
- **Spatial resolution is often sacrificed for temporal resolution** (smaller field of view, fewer
  cells per session than calcium imaging) — this is a real experimental-design tradeoff to plan for,
  not just an analysis consideration.
