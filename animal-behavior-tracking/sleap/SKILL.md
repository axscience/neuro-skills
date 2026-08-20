---
name: sleap
description: "Markerless animal pose estimation with SLEAP — labeling, training, and inference with strong native multi-animal identity tracking. For single-animal tracking, DeepLabCut is a well-established alternative; for kinematics from the output, use the kinematics leaf."
license: BSD-3-Clause
allowed-tools: Read Write Edit Bash
compatibility: Examples target SLEAP 1.3+. GPU acceleration is effectively required for practical training times.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  category: animal-behavior-tracking
---

# SLEAP

## Overview

SLEAP is a deep-learning pose-estimation tool with particularly strong native support for
multi-animal tracking — assigning consistent identity to multiple animals in the same frame, which is
where single-animal-oriented tools struggle most. This is a leaf of the `animal-behavior-tracking`
category; see `deeplabcut` for the single-animal-focused alternative and `kinematics` for analyzing
the trajectory output.

## When to use this skill

Activate when the request involves:
- SLEAP, multi-animal pose tracking, identity tracking across animals
- Terms: `.slp` labels, `sleap-train`, top-down/bottom-up model, track identity
- File formats: `.mp4`/`.avi` video, SLEAP `.slp` project/prediction files
- "Track multiple animals," "train a SLEAP model," "fix identity swaps in my tracking"

## Core usage

```python
import sleap

labels = sleap.load_file("labeled_frames.slp")
# Training is typically via the SLEAP CLI/GUI (`sleap-train`), which handles the
# multi-animal identity-tracking configuration more directly than the Python API.
predictions = sleap.load_file("predictions.slp")  # after running inference
tracks = predictions.tracks  # per-identity trajectory across frames
```

The output is per-keypoint positions per identity per frame — hand this to the `kinematics` leaf for
velocity/joint-angle measures.

## Validation & Pitfalls

Canonical reference: Pereira et al. (2022), "SLEAP: a deep learning system for multi-animal pose
tracking," *Nature Methods*.

- **Multi-animal identity tracking can swap identities between animals, especially during close
  contact/occlusion** — SLEAP is stronger here than most tools, but not immune; a downstream analysis
  assuming stable identity across a full session should include an identity-swap check (e.g.
  implausible instantaneous jumps in a keypoint's position) rather than trusting track continuity.
- **Every keypoint prediction has a confidence score, and low-confidence frames must be filtered or
  interpolated**, not treated as equally reliable — same discipline as DeepLabCut.
- **Training-label quality and coverage dominate tracking quality** — labels must span the actual
  range of poses/lighting/occlusion and, for multi-animal work, the actual range of inter-animal
  configurations; evaluate on held-out frames spanning that range.
- **Top-down vs. bottom-up model choice affects multi-animal performance depending on animal density
  and overlap** — the right choice is dataset-dependent; don't assume one model type is universally
  best without checking on the actual recordings.
- **2D single-camera tracking cannot resolve depth/out-of-plane movement** — same limitation as any
  2D pose tool; multi-camera 3D is needed for absolute movement-magnitude claims.
