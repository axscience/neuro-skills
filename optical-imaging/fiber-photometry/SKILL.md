---
name: fiber-photometry
description: "Bulk fiber photometry analysis — isosbestic-corrected dF/F, motion/photobleaching correction, and peri-event alignment. One signal per fiber/site (no spatial resolution), heavily used for GCaMP and neurotransmitter sensors (dLight/GRAB) in decision/reward neuroscience. For spatially-resolved single-cell calcium, use suite2p or caiman instead."
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: Examples use numpy/scipy; GuPPy and pMAT are common domain-specific alternatives for the same pipeline.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  category: optical-imaging
---

# Fiber Photometry

## Overview

Fiber photometry records bulk fluorescence from a single fiber/site — no spatial resolution, but
simple, robust, and heavily used for calcium (GCaMP) and, especially in decision/reward neuroscience,
neurotransmitter sensors (dLight for dopamine, GRAB sensors for other transmitters). The core
processing pipeline is the same regardless of which sensor is used. This is a leaf of the
`optical-imaging` category.

## When to use this skill

Activate when the request involves:
- Fiber photometry, bulk fluorescence, dLight, GRAB sensor, single-site GCaMP recording
- Terms: isosbestic, 405/465 channels, motion correction, peri-event dF/F, GuPPy, pMAT
- "Process this photometry recording," "isosbestic-correct this signal," "align dF/F to my events"

## Core usage

### Isosbestic-corrected dF/F

The standard photometry setup records two channels: the signal wavelength (indicator-sensitive) and
an isosbestic control wavelength (indicator fluoresces here too, but not activity-sensitively) —
using the isosbestic channel corrects for motion artifact and photobleaching that affect both
channels equally.

```python
import numpy as np
from scipy.optimize import curve_fit

def fit_isosbestic(signal_channel, control_channel):
    """Fit control -> signal with a linear model; the fitted control channel
    becomes the artifact-corrected baseline to subtract."""
    def linear(x, a, b):
        return a * x + b
    popt, _ = curve_fit(linear, control_channel, signal_channel)
    fitted_control = linear(control_channel, *popt)
    return fitted_control

def isosbestic_dff(signal_channel, control_channel):
    fitted_control = fit_isosbestic(signal_channel, control_channel)
    return (signal_channel - fitted_control) / fitted_control
```

### Event-aligned photometry (peri-event dF/F)

```python
def peri_event_dff(dff_trace, timestamps, event_times, window=(-2, 5), fs=30):
    window_samples = (int(window[0] * fs), int(window[1] * fs))
    aligned = []
    for event_time in event_times:
        event_idx = np.searchsorted(timestamps, event_time)
        start, end = event_idx + window_samples[0], event_idx + window_samples[1]
        if start >= 0 and end <= len(dff_trace):
            aligned.append(dff_trace[start:end])
    return np.array(aligned)  # (n_events, n_samples_in_window)
```

## Validation & Pitfalls

Canonical reference: Lerner et al. (2015), "Intact-brain analyses reveal distinct information carried
by SNc dopamine subcircuits," *Cell*, for the isosbestic-correction approach; Martianova, Aronson &
Proulx (2019), "Multi-fiber photometry to record neural activity in freely-moving animals," *JoVE*,
for a practical processing walkthrough.

- **A single fiber averages activity across every cell body, process, and terminal within its
  collection volume.** Photometry cannot distinguish "many cells firing weakly" from "few cells
  firing strongly" — it's a population-bulk signal, and claims about single-cell activity from
  photometry data alone aren't supported by the measurement.
- **Isosbestic correction assumes the control channel captures motion/bleaching artifact linearly and
  completely — this can fail** if the isosbestic wavelength isn't perfectly calibrated for the
  specific indicator variant, leaving residual artifact that looks like a real signal change,
  especially during large movements. Visually check the fitted control trace tracks the signal
  trace's slow trends before trusting the corrected dF/F.
- **Photobleaching is not fully corrected by isosbestic normalization alone in long sessions** —
  check for a slow downward drift in dF/F baseline over the session and consider a session-long
  detrending step in addition to isosbestic correction if one is present.
- **Peri-event window choice is a real analytic decision that affects apparent response
  timing/magnitude** — report the window used, and be cautious interpreting response *latency* from
  photometry given the calcium/sensor kinetics' inherent slowness relative to the underlying neural
  event.
