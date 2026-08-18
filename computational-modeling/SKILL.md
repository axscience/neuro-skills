---
name: computational-modeling
description: Biophysical and network SIMULATION of neurons and circuits — NEURON/Brian2/NEST for building spiking models and fitting them to recorded data. Distinct from cognitive-computational-modeling (behavioral/decision models like RL and DDM) — a different modeling tradition entirely, despite both being called "computational neuroscience."
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: Examples target Brian2 2.x for accessibility (pure Python); NEST and NEURON cover the same conceptual ground with different APIs, NEURON favoring biophysically detailed single/multi-compartment models specifically.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  modality: computational-modeling
---

# Computational Modeling (Biophysical / Network Simulation)

## Overview

This is simulation, not statistics or machine learning — building a model of neurons and their
interactions from mechanistic first principles (ion channel dynamics, synaptic conductance, network
connectivity) and running it forward in time to generate simulated activity, then comparing that
activity to real recordings. Brian2 (Python, equation-based) and NEST (large-scale point-neuron
networks) are the most common tools for network-level simulation; NEURON is standard when detailed
multi-compartment single-neuron biophysics matters.

## When to use this skill

Activate when the request involves:
- Biophysical/network simulation, spiking neuron models, integrate-and-fire, ion channel dynamics
- Terms: Brian2, NEST, NEURON, synaptic conductance, parameter fitting to recordings
- "Simulate a spiking network," "build a leaky integrate-and-fire model," "fit model parameters to my data"

## Core usage — Brian2

### A simple network of leaky integrate-and-fire neurons

```python
from brian2 import *

n_neurons = 1000
tau = 10 * ms
eqs = '''
dv/dt = (I - v) / tau : 1
I : 1
'''

neurons = NeuronGroup(n_neurons, eqs, threshold='v > 1', reset='v = 0', method='exact')
neurons.I = 1.2   # constant input drive, above threshold
neurons.v = 'rand()'   # randomized initial state to avoid synchronous artifact

spike_monitor = SpikeMonitor(neurons)
run(1 * second)

spike_times = spike_monitor.t / ms   # simulated spike times, same downstream format as spike-recording
```

### Adding synaptic connectivity

```python
synapses = Synapses(neurons, neurons, on_pre='v_post += 0.1')
synapses.connect(p=0.1)   # random connectivity, 10% connection probability
```

## Fitting a model to recorded data

```python
# Parameter fitting (e.g. matching simulated firing rate statistics to recorded
# spike-recording output) is typically an optimization problem over model
# parameters (connection probability, synaptic weight, time constants) against
# a chosen summary-statistic loss — Brian2's `brian2modelfitting` package
# provides infrastructure for this specifically.
from brian2modelfitting import NeuronGroupFitter  # illustrative import — see package docs for full API
```

## Validation & Pitfalls

Canonical references: Brette et al. (2007), "Simulation of networks of spiking neurons: a review of
tools and strategies," *Journal of Computational Neuroscience*, for a tool/method survey;
Stimberg, Brette & Goodman (2019), "Brian 2, an intuitive and efficient neural simulator," *eLife*.

- **A model that reproduces a recorded summary statistic (mean firing rate, ISI distribution) is not
  thereby validated as mechanistically correct** — many different parameter combinations, and even
  different model architectures, can reproduce the same coarse statistics. Fitting one summary
  measure is weak evidence; matching multiple independent statistics simultaneously is stronger, and
  even then the model remains one hypothesis among possibly several consistent with the data.
- **Numerical integration method and timestep affect simulation accuracy and can silently produce
  qualitatively wrong dynamics** (spurious oscillations, incorrect spike timing) if too coarse for the
  model's fastest timescale. Match the integration method/timestep to the stiffest timescale in the
  equations (e.g. fast synaptic or spike-generating dynamics), not a default chosen for
  convenience.
- **Parameter fitting to noisy neural data is commonly underdetermined** — multiple parameter sets can
  fit the target data comparably well ("sloppiness," well-documented in biophysical model fitting).
  Report parameter uncertainty/identifiability, not just a single best-fit point estimate, when the
  specific parameter values (not just the model's qualitative behavior) are part of a claim.
- **Network size and connectivity structure in a simulation are modeling choices, not neutral
  defaults, and results can be sensitive to them in ways not obvious from a single simulation run.**
  Check sensitivity to network size and connectivity parameters before treating a specific simulated
  behavior as robust rather than an artifact of the particular network configuration chosen.
