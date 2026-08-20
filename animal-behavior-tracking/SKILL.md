---
name: animal-behavior-tracking
description: Markerless pose estimation and kinematic analysis for animal behavior. Category router over DeepLabCut and SLEAP (competing pose-tracking tools) and a tool-agnostic kinematics leaf. Use for animal (not human) behavior; for human behavioral tasks, use human-psychophysics instead.
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: Category router — see individual leaf skills for per-tool version/environment notes.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  category: animal-behavior-tracking
---

# Animal Behavior Tracking

## Overview

Markerless pose estimation locates user-labeled keypoints (paws, nose, tail, joints) in video
without physical markers. This is a **category**: DeepLabCut and SLEAP are genuinely competing tools
for that job, and kinematic analysis (velocity, joint angles) is tool-agnostic — each is a leaf skill
loaded on demand. Pick the leaf that matches your task.

## When to use this skill

Activate when the request involves:
- Animal pose estimation, markerless tracking, kinematics, DeepLabCut, DLC, SLEAP
- Terms: keypoint, pose model training, multi-animal identity tracking, joint angle
- "Track this animal's pose from video," "train a DeepLabCut model," "compute limb kinematics"

## Which leaf skill to load

| You have... | Load |
|---|---|
| Pose tracking with DeepLabCut (established, strong single-animal) | [deeplabcut](deeplabcut/SKILL.md) |
| Pose tracking with SLEAP (strong native multi-animal identity tracking) | [sleap](sleap/SKILL.md) |
| Keypoint trajectories (from either tool) and want kinematic measures | [kinematics](kinematics/SKILL.md) |

**DeepLabCut vs. SLEAP:** both train a neural network to locate keypoints and output trajectories in
the same conceptual format. DeepLabCut is more established for single-animal tracking; SLEAP has
stronger native multi-animal identity handling. They're genuine alternatives — the `kinematics` leaf
treats their output identically.

## Validation & Pitfalls

- **Pose-tracking output quality is dominated by training-label quality and coverage, not tool
  choice** — the most consequential decisions (labeling frames that span the actual range of
  poses/lighting/occlusion, filtering low-confidence predictions) are shared across both tools and
  covered in each leaf; picking DeepLabCut vs. SLEAP matters less than doing those steps well.
