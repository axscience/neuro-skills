---
name: spike-recording
description: Extracellular single/multi-unit recording — spike sorting raw voltage traces into single-unit spike times with SpikeInterface, then computing standard spike train statistics (ISIs, firing rate, PSTH, CV, Fano factor). Use this for action-potential/spike data specifically. For field-potential recordings (EEG/MEG/ECoG), use electrophysiology instead — different signal class, different tooling.
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: Examples target spikeinterface 0.100+ for sorting; numpy/pandas/matplotlib only for the analysis section. Actual sorting algorithms (Kilosort, Mountainsort) are external dependencies SpikeInterface wraps.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  modality: spike-recording
---

# Spike Recording (Sorting + Analysis)

## Overview

Extracellular recording captures action potentials from many neurons on each channel; turning that
into per-neuron spike times (sorting) and then characterizing each neuron's firing (analysis) are
the two stages this skill covers. They're presented together because they're a tight pipeline —
sorting's output format is exactly analysis's input format — but are separable: skip sorting entirely
if spikes are already sorted (e.g. from a public dataset via `neuro-data-standards`).

## When to use this skill

Activate when the request involves:
- Extracellular recording, spike sorting, single-unit, multi-unit, action potentials, raw voltage traces
- Terms: SpikeInterface, Kilosort, Mountainsort, ISI, PSTH, firing rate, CV, Fano factor,
  refractory period violation
- File formats: raw binary ephys (`.dat`, `.bin`), Neuropixels/probe recordings
- "Sort these spikes," "compute firing rate/PSTH," "check unit quality metrics"

## Part 1 — Spike sorting (SpikeInterface)

SpikeInterface is a unified framework over many sorting algorithms (Kilosort, Mountainsort,
HerdingSpikes, and others) — it standardizes I/O, preprocessing, sorter invocation, and quality
metrics regardless of which underlying sorter you use.

```python
import spikeinterface.full as si

recording = si.read_binary("raw_recording.dat", sampling_frequency=30000, num_channels=64, dtype="int16")
recording = si.bandpass_filter(recording, freq_min=300, freq_max=6000)
recording = si.common_reference(recording, reference="global", operator="median")

sorting = si.run_sorter(sorter_name="kilosort2_5", recording=recording, output_folder="sorting_output")

analyzer = si.create_sorting_analyzer(sorting, recording, folder="analyzer_output")
analyzer.compute(["random_spikes", "waveforms", "templates", "quality_metrics"])
quality_metrics = analyzer.get_extension("quality_metrics").get_data()

good_unit_ids = quality_metrics[
    (quality_metrics["isi_violations_ratio"] < 0.5)
    & (quality_metrics["amplitude_cutoff"] < 0.1)
    & (quality_metrics["presence_ratio"] > 0.9)
].index

spike_times_per_unit = {
    unit_id: sorting.get_unit_spike_train(unit_id) / recording.get_sampling_frequency()
    for unit_id in good_unit_ids
}  # values in seconds — this is the input format Part 2 expects
```

### Manual curation before trusting automated quality metrics

Automated metrics catch obviously bad units, not merged/split clusters. Spot-check waveform shape
and cross-correlograms for units a specific claim depends on:

```python
import spikeinterface.widgets as sw

sw.plot_unit_waveforms(analyzer, unit_ids=[unit_id])       # consistent shape across spikes?
sw.plot_crosscorrelograms(analyzer, unit_ids=[unit_id_a, unit_id_b])  # sharp dip at zero lag = same neuron, split
sw.plot_autocorrelograms(analyzer, unit_ids=[unit_id])       # clear refractory dip = clean single unit
```

## Part 2 — Spike train analysis

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

Canonical references: Buccino et al. (2020), "SpikeInterface, a unified framework for spike
sorting," *eLife*; Dayan & Abbott, *Theoretical Neuroscience* (2001), Ch. 1, and Perkel, Gerstein &
Moore (1967), "Neuronal spike trains and stochastic point processes," *Biophysical Journal*, for
spike-statistics foundations.

- **Different sorters produce meaningfully different results on the same data — there's no single
  "correct" sorter.** Running two and checking agreement on well-isolated units is a reasonable
  cross-check, especially on a novel probe/preparation type a sorter wasn't tuned on.
- **ISIs below the refractory period (~1-2 ms) indicate a sorting error, not biology.** Fix the
  upstream sorting; don't silently filter these out without flagging it.
- **Electrode drift over long recordings degrades sorting if uncorrected** — check whether the
  sorter's drift correction (most modern sorters, including Kilosort, have this) is actually enabled
  for sessions longer than ~30-60 minutes on chronic probes.
- **Multi-unit contamination (imperfect sorting) conflates multiple neurons into one ISI/CV
  distribution**, typically producing a spuriously low CV (looks more regular than any single neuron
  actually is). Confirm single-unit isolation quality before interpreting variability metrics.
- **PSTH bin size changes the story, not just the resolution** — no universally correct choice;
  report the bin size used and sanity-check with at least one other before trusting a claimed
  transient.
- **Spike sorting output is in sample indices until divided by the sampling rate** — a common source
  of silently misaligned downstream analysis (wrong ISIs, wrong stimulus alignment).
