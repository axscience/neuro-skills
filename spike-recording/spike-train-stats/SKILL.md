---
name: spike-train-stats
description: "Spike-train statistics from already-sorted spike times — inter-spike intervals, firing rate, PSTH, coefficient of variation, Fano factor. Tool-agnostic (numpy only); input is spike times in seconds. For sorting raw voltage into spike times first, use the spikeinterface leaf."
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: Examples use numpy only; input is per-unit spike-time arrays (seconds) from any source (a sorter, a public dataset, or simulation).
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  category: spike-recording
---

# Spike-Train Statistics

## Overview

Given sorted spike times (per unit, in seconds), this leaf computes the standard descriptive
statistics that characterize a neuron's firing: inter-spike intervals, firing rate, peri-stimulus
time histogram (PSTH), coefficient of variation of ISIs, and Fano factor. It's tool-agnostic — the
input can come from the `spikeinterface` leaf, a public dataset (`neuro-data-standards`), or a
simulation (`computational-modeling`). This is a leaf of the `spike-recording` category.

## When to use this skill

Activate when the request involves:
- Firing rate, PSTH, inter-spike interval, ISI, CV, Fano factor, spike-train statistics
- Terms: peri-stimulus time histogram, coefficient of variation, spike-count variability, bin size
- "Compute firing rate/PSTH from spike times," "how bursty is this neuron," "spike-count variability"

## Core usage

```python
import numpy as np

def isi(spike_times):
    return np.diff(np.sort(np.asarray(spike_times)))

def mean_firing_rate(spike_times, duration):
    return len(spike_times) / duration

def psth(trial_spike_times, window, bin_size=0.01):
    """trial_spike_times: list of arrays, aligned so t=0 is the event of interest."""
    bins = np.arange(window[0], window[1] + bin_size, bin_size)
    counts = np.zeros(len(bins) - 1)
    for trial in trial_spike_times:
        trial_counts, _ = np.histogram(trial, bins=bins)
        counts += trial_counts
    rate = counts / (len(trial_spike_times) * bin_size)
    return rate, (bins[:-1] + bins[1:]) / 2

def cv_isi(spike_times):
    intervals = np.diff(np.sort(np.asarray(spike_times)))
    return np.std(intervals) / np.mean(intervals) if len(intervals) >= 2 else np.nan

def fano_factor(trial_spike_times, window):
    counts = np.array([
        np.sum((np.asarray(t) >= window[0]) & (np.asarray(t) < window[1])) for t in trial_spike_times
    ])
    return counts.var() / counts.mean() if counts.mean() > 0 else np.nan
```

CV of ISI (within-trial timing irregularity) and Fano factor (across-trial count variability) answer
different questions — a neuron can be bursty (high CV) while still producing a reproducible trial
count (low Fano factor), or vice versa. Report both when characterizing a unit.

## Validation & Pitfalls

Canonical references: Dayan & Abbott, *Theoretical Neuroscience* (2001), Ch. 1; Perkel, Gerstein &
Moore (1967), "Neuronal spike trains and stochastic point processes," *Biophysical Journal*.

- **These statistics are only meaningful on well-isolated single units** — multi-unit contamination
  (imperfect sorting) conflates multiple neurons into one ISI/CV distribution, typically producing a
  spuriously low CV (looks more regular than any single neuron actually is). Confirm single-unit
  isolation quality (via the `spikeinterface` leaf) before interpreting variability metrics.
- **PSTH bin size changes the story, not just the resolution** — no universally correct choice;
  report the bin size used and sanity-check with at least one other before trusting a claimed
  transient.
- **Firing-rate and variability estimates need adequate spike counts** — a handful of spikes gives an
  unstable CV/Fano-factor estimate; report the spike/trial counts alongside the statistics, not just
  the ratios.
- **Spike times must be in consistent units (seconds here)** — mixing sample-index and seconds inputs
  silently produces wrong ISIs and misaligned PSTHs; confirm the input unit before computing anything.
