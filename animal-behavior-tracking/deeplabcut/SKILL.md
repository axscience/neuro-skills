---
name: deeplabcut
description: "Markerless animal pose estimation with DeepLabCut — creating a project, extracting/labeling frames, training a keypoint model, and analyzing videos. Established, strong for single-animal tracking. For native multi-animal identity tracking, consider sleap; for kinematics from the output, use the kinematics leaf."
license: LGPL-3.0-or-later
allowed-tools: Read Write Edit Bash
compatibility: Examples target DeepLabCut 2.3+. GPU acceleration is effectively required for practical training times on real datasets.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  category: animal-behavior-tracking
---

# DeepLabCut

## Overview

DeepLabCut trains a neural network to locate user-labeled body-part keypoints in video without
physical markers. It's the more established of the two pose-tracking tools here, particularly strong
for single-animal tracking. This is a leaf of the `animal-behavior-tracking` category; see `sleap`
for the multi-animal-focused alternative and `kinematics` for analyzing the trajectory output.

## When to use this skill

Activate when the request involves:
- DeepLabCut, DLC, markerless pose estimation (single-animal especially)
- Terms: `create_new_project`, `train_network`, `analyze_videos`, config.yaml, keypoint likelihood
- File formats: `.mp4`/`.avi` video, DLC `.h5`/`.csv` tracking output
- "Train a DeepLabCut model," "track this animal's pose," "why is my DLC tracking jumpy"

## Core usage

```python
import deeplabcut

config_path = deeplabcut.create_new_project("my_project", "researcher", ["video1.mp4"])
deeplabcut.extract_frames(config_path, mode="automatic")
# Label extracted frames in the DLC GUI, then:
deeplabcut.create_training_dataset(config_path)
deeplabcut.train_network(config_path, maxiters=100000)
deeplabcut.analyze_videos(config_path, ["new_video.mp4"])
```

The output is per-keypoint (x, y, likelihood) per frame — hand this to the `kinematics` leaf for
velocity/joint-angle measures.

## Validation & Pitfalls

Canonical reference: Mathis et al. (2018), "DeepLabCut: markerless pose estimation of user-defined
body parts with deep learning," *Nature Neuroscience*.

- **Every keypoint prediction has a likelihood score, and low-likelihood frames must be filtered or
  interpolated, not treated as equally reliable.** A raw trajectory including low-confidence
  predictions (occlusion, motion blur, animal out of frame) introduces spurious "movement" that's
  tracking failure, not real kinematics.
- **Training-label quality and diversity determine tracking quality more than iterations or
  architecture.** Labeled frames that don't span the video set's actual poses/lighting/occlusion
  produce a model that fails exactly on the conditions the training set omitted — evaluate tracking on
  held-out frames spanning the real behavioral range, not just training frames.
- **DeepLabCut's multi-animal mode exists but identity tracking is harder than single-animal** — for
  studies where robust multi-animal identity is central, evaluate SLEAP too rather than assuming DLC
  multi-animal handles close-contact identity swaps well.
- **2D single-camera tracking cannot resolve depth/out-of-plane movement** — kinematics from 2D pixel
  coordinates conflate true movement with perspective; multi-camera 3D is needed for absolute
  movement-magnitude claims.
