---
name: eye-tracking
description: Eye-tracking data processing — fixation/saccade detection, blink handling, and pupillometry, for common vendor formats (EDF/Tobii). Cross-references electrophysiology/references/eeg.md for co-registered EEG-eye-tracking artifact rejection when both are recorded simultaneously.
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: Examples use numpy/scipy for algorithm-level processing; `pyedfread` for parsing EyeLink EDF files specifically.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  modality: eye-tracking
---

# Eye Tracking

## Overview

Eye trackers record gaze position (and often pupil diameter) at high sampling rates; the core
processing task is segmenting the continuous gaze signal into fixations (gaze relatively stable),
saccades (rapid gaze shifts between fixations), and blinks (signal loss), then computing measures
from each. This skill covers the standard velocity-based event detection and pupillometry
preprocessing shared across vendors, despite format differences (EyeLink's EDF, Tobii's proprietary
format, etc.).

## When to use this skill

Activate when the request involves:
- Eye tracking, gaze, fixation, saccade, pupillometry, blink
- File formats: EyeLink `.edf`, Tobii proprietary formats
- Terms: pyedfread, dispersion-threshold identification (I-DT), velocity threshold
- "Detect fixations/saccades in this gaze data," "clean pupil diameter," "co-register with EEG"

## Core usage

### Loading data (EyeLink EDF)

```python
import pyedfread

samples, events, messages = pyedfread.read_edf("recording.edf")
# samples: per-sample gaze x/y/pupil; events: vendor-detected fixations/saccades/blinks (see pitfalls)
```

### Velocity-based saccade detection (vendor-independent — works on raw x/y/timestamp)

```python
import numpy as np

def detect_saccades(gaze_x, gaze_y, timestamps, velocity_threshold_deg_s=30):
    """Simple velocity-threshold detector. dt in seconds; gaze in degrees of visual angle."""
    dt = np.diff(timestamps)
    dx, dy = np.diff(gaze_x), np.diff(gaze_y)
    velocity = np.sqrt(dx**2 + dy**2) / dt
    is_saccade = velocity > velocity_threshold_deg_s
    return is_saccade
```

### Blink detection and interpolation

```python
def interpolate_blinks(pupil_diameter, min_valid=0.1, max_gap_samples=200):
    """Pupil diameter near/at zero indicates a blink (eyelid occludes the pupil).
    Short gaps are linearly interpolated; long gaps are left as NaN rather than
    interpolated across, since long-gap interpolation fabricates data."""
    invalid = pupil_diameter < min_valid
    cleaned = pupil_diameter.copy()
    gap_starts = np.where(np.diff(invalid.astype(int)) == 1)[0]
    gap_ends = np.where(np.diff(invalid.astype(int)) == -1)[0]
    for start, end in zip(gap_starts, gap_ends):
        if end - start <= max_gap_samples:
            cleaned[start:end] = np.interp(
                np.arange(start, end), [start - 1, end], [pupil_diameter[start - 1], pupil_diameter[end]]
            )
        else:
            cleaned[start:end] = np.nan
    return cleaned
```

### Fixation identification (dispersion-based, after removing saccades/blinks)

```python
def detect_fixations(gaze_x, gaze_y, timestamps, dispersion_threshold_deg=1.0, min_duration_s=0.1):
    """I-DT (dispersion-threshold identification) — groups consecutive samples
    within a small spatial window into a fixation if they persist long enough."""
    fixations = []
    start = 0
    while start < len(gaze_x):
        end = start
        while end < len(gaze_x):
            window_x, window_y = gaze_x[start:end + 1], gaze_y[start:end + 1]
            dispersion = (window_x.max() - window_x.min()) + (window_y.max() - window_y.min())
            if dispersion > dispersion_threshold_deg:
                break
            end += 1
        duration = timestamps[end - 1] - timestamps[start] if end > start else 0
        if duration >= min_duration_s:
            fixations.append({"start": start, "end": end, "duration": duration,
                               "x": gaze_x[start:end].mean(), "y": gaze_y[start:end].mean()})
        start = max(end, start + 1)
    return fixations
```

## Validation & Pitfalls

Canonical reference: Salvucci & Goldberg (2000), "Identifying fixations and saccades in eye-tracking
protocols," *ACM Symposium on Eye Tracking Research & Applications*, for the algorithm families above
(velocity-threshold saccade detection, dispersion-threshold fixation detection) and their tradeoffs.

- **Vendor-provided event classification (EyeLink's built-in fixation/saccade parsing) and a custom
  velocity-threshold detector can disagree, sometimes substantially, depending on threshold choice.**
  State which was used; don't treat vendor-classified events as unambiguously "the" fixations/saccades
  if reanalyzing with different parameters would give a different segmentation.
- **Pupil diameter is confounded by luminance, not just cognitive/arousal state** — a pupillometry
  result attributed to an experimental manipulation needs to rule out luminance differences between
  conditions (screen brightness, stimulus contrast) as the actual driver, either by design (matched
  luminance) or explicit statistical control.
- **Calibration quality degrades over a session (head movement, fatigue) and isn't necessarily
  constant** — check for drift in fixation accuracy over the session (e.g. via periodic
  calibration-validation points) rather than assuming initial calibration holds throughout.
- **Blink interpolation over long gaps fabricates data that looks like a real pupil trace** — the
  `max_gap_samples` cutoff above exists specifically to avoid this; a downstream analysis run on a
  fully-interpolated trace can produce a result driven by the interpolation method, not real
  physiology, if long gaps are papered over.
- **When co-registered with EEG** (e.g. to reject trials with fixation breaks, or to build ocular-
  artifact regressors), synchronize on a shared trigger channel and confirm clock alignment
  explicitly — don't assume the two devices' timestamps share a reference without checking. See
  `electrophysiology/references/eeg.md` for the EEG-side ocular artifact handling this feeds into.
