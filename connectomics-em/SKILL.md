---
name: connectomics-em
description: Electron-microscopy connectomics — volumetric EM data handling, neuron segmentation/reconstruction, and synapse detection, using Neuroglancer-style tooling. Distinct from diffusion MRI tractography (mri/references/diffusion.md), which infers macroscopic white-matter connectivity rather than reconstructing individual synapses from micron-scale imaging.
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: Examples use CloudVolume (Python) for volumetric EM data access; Neuroglancer for visualization/annotation.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  modality: connectomics-em
---

# EM Connectomics

## Overview

Electron microscopy connectomics reconstructs neural circuits at synaptic resolution — segmenting
individual neurons from serial EM sections and detecting synapses between them — producing a
literal wiring diagram, unlike any other modality in this repo (which measure activity, not
structural connectivity at this resolution). Datasets are enormous (petabyte-scale for whole-brain
volumes), and analysis is dominated by data access/visualization tooling built for that scale.

## When to use this skill

Activate when the request involves:
- Electron microscopy, EM connectomics, connectome, synapse detection, neuron reconstruction,
  segmentation
- Terms: CloudVolume, Neuroglancer, CAVE, merge/split errors, precomputed volume
- "Access this EM volume," "query synapses for a reconstructed neuron," "proofread this segmentation"

## Core usage

### Accessing a cloud-hosted EM volume

```python
import cloudvolume

vol = cloudvolume.CloudVolume("precomputed://gs://example-em-dataset/image", mip=0)
image_chunk = vol[1000:1100, 1000:1100, 100:110]   # a small (100,100,10) voxel region
```

### Querying segmentation and connectivity for a reconstructed neuron

```python
segmentation = cloudvolume.CloudVolume("precomputed://gs://example-em-dataset/segmentation")
neuron_mesh = segmentation.mesh.get(segment_id=12345)   # 3D mesh for one reconstructed neuron

# Synapse tables (pre/post synaptic partner IDs + locations) are typically queried
# via a separate annotation database rather than the volumetric data itself —
# e.g. CAVE (Connectome Annotation Versioning Engine) for datasets that use it.
```

### Visualization/proofreading (Neuroglancer)

```python
import neuroglancer

viewer = neuroglancer.Viewer()
with viewer.txn() as s:
    s.layers["segmentation"] = neuroglancer.SegmentationLayer(
        source="precomputed://gs://example-em-dataset/segmentation"
    )
print(viewer)  # opens a URL for interactive proofreading/annotation
```

## Validation & Pitfalls

Canonical reference: Kornfeld & Denk (2018), "Progress and remaining challenges in high-throughput
volume electron microscopy," *Current Opinion in Neurobiology*, for a survey of methodology and its
current limitations.

- **Automated segmentation is never error-free at whole-brain scale, and errors are of two distinct
  types with different consequences** — "merge errors" (two separate neurons incorrectly joined into
  one segment) and "split errors" (one neuron incorrectly broken into multiple segments). Both
  require human proofreading to catch; an unproofread automated segmentation should not be treated as
  ground-truth connectivity.
- **A reconstructed "connection" (synapse detected between two segments) still requires the
  segmentation itself to be correct on both sides** — a synapse detector operating on a merge-error-
  contaminated segmentation will report connections that don't reflect real neuron-to-neuron synapses.
- **EM connectomics gives structural connectivity only — it says nothing about synaptic strength,
  sign (excitatory/inhibitory beyond morphological cues), or whether a structural synapse is
  functionally active.** A "connectome" is a wiring diagram, not a functional circuit model; claims
  drawing functional conclusions from structural connectivity alone need to state this limitation
  explicitly.
- **Dataset scale means most analysis is necessarily on a subvolume or a proofread subset of neurons,
  not the full dataset** — be explicit about what fraction/region of a released dataset a given
  analysis actually covers, since "whole-brain EM connectome" datasets are frequently used for
  targeted analyses of specific circuits, not exhaustively.
