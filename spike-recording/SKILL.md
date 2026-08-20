---
name: spike-recording
description: Extracellular single/multi-unit recording. Category router over spike sorting (SpikeInterface) and spike-train statistics (tool-agnostic). Use for action-potential/spike data; for field-potential recordings (EEG/MEG/ECoG), use electrophysiology instead — different signal class, different tooling.
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: Category router — see individual leaf skills for per-tool version/environment notes.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  category: spike-recording
---

# Spike Recording

## Overview

Extracellular recording captures action potentials from many neurons per channel. Turning raw
voltage into per-neuron spike times (sorting) and characterizing each neuron's firing (analysis) are
two separable stages — this is a **category** with a leaf for each, because they're often used
independently: you might already have sorted spikes from a public dataset (via `neuro-data-standards`)
and only need the analysis leaf.

## When to use this skill

Activate when the request involves:
- Extracellular recording, spike sorting, single-unit, multi-unit, action potentials, raw voltage traces
- Terms: SpikeInterface, Kilosort, Mountainsort, ISI, PSTH, firing rate, CV, Fano factor,
  refractory period violation
- File formats: raw binary ephys (`.dat`, `.bin`), Neuropixels/probe recordings
- "Sort these spikes," "compute firing rate/PSTH," "check unit quality metrics"

## Which leaf skill to load

| You have... | Load |
|---|---|
| Raw voltage traces to sort into single units, or need quality metrics/curation | [spikeinterface](spikeinterface/SKILL.md) |
| Already-sorted spike times, and want firing-rate/ISI/PSTH/CV/Fano-factor statistics | [spike-train-stats](spike-train-stats/SKILL.md) |

The sorting leaf's output (spike times in seconds, per unit) is exactly the analysis leaf's input.

## Validation & Pitfalls

- **Sorting quality gates everything downstream** — spike-train statistics computed on badly-sorted
  units (merged/split clusters, multi-unit contamination) reflect sorting artifacts, not biology. The
  `spikeinterface` leaf's quality-metric and curation steps are a precondition for trusting anything
  the `spike-train-stats` leaf produces; don't skip straight to statistics on unvalidated units.
