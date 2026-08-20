---
name: kinematics
description: "Kinematic analysis from pose-tracking keypoint trajectories — velocity, speed, joint angles, and smoothing — tool-agnostic (works on DeepLabCut or SLEAP output). Use after pose estimation; for the tracking itself, use deeplabcut or sleap."
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: Examples use numpy/scipy only; input is keypoint trajectories from any pose-tracking tool.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  category: animal-behavior-tracking
---

# Kinematics

## Overview

Once pose tracking has produced keypoint trajectories (from `deeplabcut` or `sleap` — the input is
the same either way), kinematic analysis extracts movement measures: speed, velocity, joint angles,
and their time courses. This leaf is deliberately tool-agnostic — it treats trajectories identically
regardless of which tracker produced them.

## When to use this skill

Activate when the request involves:
- Kinematics, velocity, speed, joint angle, gait, movement analysis from tracked keypoints
- Terms: trajectory smoothing, Savitzky-Golay, differencing, likelihood filtering
- "Compute limb velocity from my tracking," "measure joint angles over time," "quantify locomotion speed"

## Core usage

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

Canonical reference: Winter, *Biomechanics and Motor Control of Human Movement* (4th ed., 2009), for
kinematic-measure conventions (velocity/acceleration from position, joint-angle definitions) that
carry over to animal tracking.

- **Filter low-confidence keypoints before computing kinematics** — velocity computed across a
  tracking dropout is a spurious spike, not real movement; drop or interpolate low-likelihood frames
  (from the tracker's confidence output) first.
- **Differencing amplifies tracking noise, especially at low frame rate** — velocity/acceleration by
  simple `np.diff` is noisy; smooth (e.g. Savitzky-Golay) before differencing, and report the frame
  rate alongside any velocity/acceleration claim.
- **2D kinematics conflate true movement with perspective/out-of-plane motion** — a measure computed
  from 2D pixel coordinates is not an absolute movement magnitude unless the movement is in-plane;
  multi-camera 3D reconstruction is needed for absolute-magnitude claims.
- **Pixel-to-physical-unit calibration is required for physical (not just relative) kinematics** — a
  speed in pixels/frame is not cm/s without a spatial calibration and the true frame rate; state both
  before reporting physical units.
