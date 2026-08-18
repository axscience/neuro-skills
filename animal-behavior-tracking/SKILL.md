---
name: animal-behavior-tracking
description: Markerless pose estimation and kinematic analysis for animal behavior using DeepLabCut or SLEAP — training a pose-tracking model, extracting keypoint trajectories, and computing standard kinematic measures. Use this for animal (not human) behavior; for human psychophysics/behavioral tasks, use human-psychophysics instead.
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: Examples target DeepLabCut 2.3+ and SLEAP 1.3+. Both require GPU acceleration for practical training times on real datasets.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  modality: animal-behavior-tracking
---

# Animal Behavior Tracking

## Overview

DeepLabCut and SLEAP both do markerless pose estimation — training a neural network to locate
user-labeled keypoints (paws, nose, tail, joints) in video without physical markers. DeepLabCut is
more established for single-animal tracking; SLEAP has stronger native support for multi-animal
tracking (identity assignment across animals in the same frame). Both produce keypoint trajectories
as their output, which this skill's kinematic analysis section treats identically regardless of
which produced it.

## When to use this skill

Activate when the request involves:
- Animal pose estimation, markerless tracking, kinematics, DeepLabCut, DLC, SLEAP
- Terms: keypoint, pose model training, multi-animal identity tracking, joint angle
- "Track this animal's pose from video," "train a DeepLabCut model," "compute limb kinematics"

## Core usage

### DeepLabCut — project setup and training

```python
import deeplabcut

config_path = deeplabcut.create_new_project("my_project", "researcher", ["video1.mp4"])
deeplabcut.extract_frames(config_path, mode="automatic")
# Label extracted frames in the DLC GUI, then:
deeplabcut.create_training_dataset(config_path)
deeplabcut.train_network(config_path, maxiters=100000)
deeplabcut.analyze_videos(config_path, ["new_video.mp4"])
```

### SLEAP — multi-animal tracking

```python
import sleap

labels = sleap.load_file("labeled_frames.slp")
# Train via the SLEAP CLI/GUI is typical (`sleap-train`), which handles multi-animal
# identity tracking configuration more directly than the Python API for this step.
predictions = sleap.load_file("predictions.slp")  # after running inference
tracks = predictions.tracks  # per-identity trajectory across frames
```

### Kinematic analysis from keypoint trajectories

```python
import numpy as np

def keypoint_velocity(trajectory, fs):
    """trajectory: (n_frames, 2) x,y keypoint position. Returns speed per frame."""
    velocity = np.diff(trajectory, axis=0) * fs
    return np.linalg.norm(velocity, axis=1)

def joint_angle(point_a, point_b, point_c):
    """Angle at point_b, formed by point_a-point_b-point_c (e.g. a limb joint)."""
    v1 = point_a - point_b
    v2 = point_c - point_b
    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    return np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))
```

## Validation & Pitfalls

Canonical references: Mathis et al. (2018), "DeepLabCut: markerless pose estimation of user-defined
body parts with deep learning," *Nature Neuroscience*; Pereira et al. (2022), "SLEAP: a deep
learning system for multi-animal pose tracking," *Nature Methods*.

- **Every keypoint prediction has a confidence/likelihood score, and low-confidence frames should be
  filtered or interpolated, not treated as equally reliable as high-confidence ones.** A raw
  trajectory including low-confidence predictions (occlusion, motion blur, animal out of frame)
  introduces spurious "movement" that's actually tracking failure, not real kinematics.
- **Training data label quality and diversity determine downstream tracking quality more than model
  architecture choice.** Labeled frames that don't cover the actual range of poses/lighting/occlusion
  in the full video set will produce a model that fails exactly on the conditions the training set
  didn't include — check tracking quality on frames spanning the video's actual behavioral range,
  not just the training frames.
- **Multi-animal identity tracking (SLEAP or DLC's multi-animal mode) can swap identities between
  animals, especially during close contact/occlusion** — a downstream analysis that assumes stable
  identity across a full session should include an identity-swap check (e.g. implausible instantaneous
  jumps in a keypoint's position) rather than trusting track continuity by default.
- **Frame rate limits what kinematic measures are meaningful** — velocity/acceleration computed by
  simple differencing amplifies tracking noise, especially at low frame rates; consider smoothing
  (e.g. a Savitzky-Golay filter) before differencing, and report the frame rate alongside any
  velocity/acceleration claim.
- **2D tracking from a single camera view cannot resolve depth/out-of-plane movement** — a kinematic
  measure computed from 2D pixel coordinates conflates true movement magnitude with apparent
  movement due to perspective and camera angle; multi-camera 3D reconstruction is needed when
  absolute movement magnitude (not just relative/qualitative comparison) is the claim.
