---
name: spikeinterface
description: "Spike sorting raw extracellular voltage into single-unit spike times with SpikeInterface — preprocessing, running a sorter (Kilosort/Mountainsort/etc.), quality metrics, and manual curation. Output feeds the spike-train-stats leaf. For field-potential recordings (EEG/MEG/ECoG), use electrophysiology instead."
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: Examples target spikeinterface 0.100+. Actual sorting algorithms (Kilosort, Mountainsort) are external dependencies SpikeInterface wraps and install separately.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  category: spike-recording
---

# SpikeInterface

## Overview

SpikeInterface is a unified framework over many spike-sorting algorithms (Kilosort, Mountainsort,
HerdingSpikes, and others) — it standardizes I/O, preprocessing, sorter invocation, and quality
metrics regardless of which underlying sorter you use. This leaf covers turning raw voltage into
sorted, quality-gated single-unit spike times; the `spike-train-stats` leaf covers analyzing those
spike times. This is a leaf of the `spike-recording` category.

## When to use this skill

Activate when the request involves:
- Spike sorting, SpikeInterface, Kilosort, Mountainsort, raw voltage traces, unit quality metrics
- Terms: `run_sorter`, `create_sorting_analyzer`, isi_violations_ratio, amplitude_cutoff,
  presence_ratio, manual curation, cross-correlogram
- File formats: raw binary ephys (`.dat`, `.bin`), Neuropixels/probe recordings
- "Sort these spikes," "check unit quality metrics," "curate merged/split clusters"

## Core usage

### Preprocess and sort

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
}  # values in seconds — this is the input format the spike-train-stats leaf expects
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

## Validation & Pitfalls

Canonical reference: Buccino et al. (2020), "SpikeInterface, a unified framework for spike sorting,"
*eLife*.

- **Different sorters produce meaningfully different results on the same data — there's no single
  "correct" sorter.** Running two and checking agreement on well-isolated units is a reasonable
  cross-check, especially on a novel probe/preparation type a sorter wasn't tuned on.
- **ISIs below the refractory period (~1-2 ms) indicate a sorting error, not biology.** Fix the
  upstream sorting; don't silently filter these out without flagging it.
- **Electrode drift over long recordings degrades sorting if uncorrected** — check whether the
  sorter's drift correction (most modern sorters, including Kilosort, have this) is actually enabled
  for sessions longer than ~30-60 minutes on chronic probes.
- **Automated quality metrics are a filter, not ground truth** — merged/split clusters can pass the
  thresholds above; visually curate (waveforms, cross-correlograms) units a claim depends on.
- **Sorting output is in sample indices until divided by the sampling rate** — a common source of
  silently misaligned downstream analysis (wrong ISIs, wrong stimulus alignment); the conversion to
  seconds above is required before handing off to `spike-train-stats`.
