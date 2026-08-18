---
name: experimental-design
description: Stimulus presentation and task-building (PsychoPy/Psychtoolbox), trigger/event coding, and multi-device timing synchronization. Upstream of every acquisition skill in this repo — use this to build the task that produces the data the other skills analyze.
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: Examples target PsychoPy 2024.x (Python). Psychtoolbox (MATLAB) covers equivalent functionality for MATLAB-based labs.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  modality: experimental-design
---

# Experimental Design

## Overview

Every skill in this repo analyzes data that came from somewhere — this skill is that somewhere.
PsychoPy (Python) and Psychtoolbox (MATLAB) are the two standard stimulus-presentation platforms;
both handle precise stimulus timing, response collection, and (critically for downstream analysis)
trigger/event coding that ties recorded neural data to what the participant actually experienced.

## When to use this skill

Activate when the request involves:
- Stimulus presentation, task building, trigger coding, timing synchronization
- Terms: PsychoPy, Psychtoolbox, Lab Streaming Layer, LSL, parallel port trigger, photodiode
- "Build this task in PsychoPy," "send triggers to my EEG system," "sync multiple recording devices"

## Core usage

### Basic PsychoPy trial structure

```python
from psychopy import visual, core, event

win = visual.Window(size=(1024, 768), fullscr=True, units="deg")
stimulus = visual.GratingStim(win, sf=2, ori=45)

for trial in range(n_trials):
    stimulus.draw()
    win.flip()
    onset_time = core.getTime()
    keys = event.waitKeys(maxWait=2.0, timeStamped=core.Clock())
```

### Trigger/event coding — sending a marker to recording hardware

```python
# Parallel port (legacy but still common for EEG labs needing sub-ms trigger precision)
from psychopy import parallel

port = parallel.ParallelPort(address=0x0378)
port.setData(0)         # reset before trial
win.flip()               # stimulus onset
port.setData(1)          # trigger code for this event, sent as close to the flip as possible

# LSL (Lab Streaming Layer) — for multi-device sync (EEG + eye-tracking + physiological)
from pylsl import StreamInfo, StreamOutlet

info = StreamInfo("PsychoPyMarkers", "Markers", 1, 0, "string", "psychopy_marker_stream")
outlet = StreamOutlet(info)
outlet.push_sample(["stimulus_onset"])
```

### Timing verification (don't assume — measure)

```python
# Photodiode-based verification is the gold standard for confirming actual
# screen-refresh timing matches intended timing, independent of software-reported
# timestamps, which can be misleading (see pitfalls).
frame_intervals = win.frameIntervals   # PsychoPy's own frame-timing diagnostic
dropped_frames = sum(1 for fi in frame_intervals if fi > (1.5 / win.getActualFrameRate()))
```

## Validation & Pitfalls

Canonical references: Peirce et al. (2019), "PsychoPy2: experiments in behavior made easy," *Behavior
Research Methods*; Plant (2016), "A reminder on millisecond timing accuracy and potential replication
failure in computer-based psychology experiments," *Behavior Research Methods*, specifically on the
timing pitfalls below.

- **Software-reported stimulus onset timestamps are not the same as actual screen-refresh timing** —
  operating system scheduling, graphics driver buffering, and display refresh rate all introduce
  potential discrepancies between when code calls "present the stimulus" and when it's actually
  visible. Photodiode verification (measuring actual screen luminance change) is the only way to
  confirm timing accuracy for a specific setup; don't assume software timestamps are ground truth,
  especially for paradigms sensitive to sub-frame timing precision.
- **Trigger codes sent to recording hardware and the timestamp of the event they're meant to mark
  can be offset by an unknown, hardware/software-dependent latency** — measure and report this
  latency (e.g. via a photodiode-to-trigger loopback test) rather than assuming trigger and stimulus
  are simultaneous.
- **Dropped frames silently distort stimulus duration and timing for the specific trials affected** —
  monitor and report frame-timing diagnostics (like `frameIntervals` above), don't assume a modern
  system never drops frames.
- **Multi-device synchronization (EEG + eye-tracking + behavior) needs a shared clock or a
  reconciliation strategy, not independent device clocks assumed to agree** — LSL is the standard
  solution specifically because it timestamps all streams against one reference clock; ad hoc
  post-hoc alignment (e.g. matching event counts) is much more error-prone.
- **Counterbalancing and randomization seeds should be logged and version-controlled**, not
  regenerated fresh at run time without a saved record — an unreproducible trial sequence makes a
  study's exact conditions unrecoverable after the fact, which matters for both replication and
  debugging an unexpected result.
