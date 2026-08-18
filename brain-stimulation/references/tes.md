# Transcranial Electrical Stimulation (tDCS/tACS)

Modality-specific detail for [../SKILL.md](../SKILL.md). tDCS (direct current) and tACS (alternating
current) apply weak electrical current through scalp electrodes to modulate cortical excitability
(tDCS) or entrain oscillatory activity at a target frequency (tACS). Unlike TMS, tES doesn't directly
evoke action potentials — it modulates the likelihood of firing, making effects generally weaker and
more variable.

## Standard dosing conventions

```python
# tDCS: typically 1-2 mA, 10-20 minutes, anode over the target region (excitatory
# in the traditional model — see pitfalls), cathode as a return electrode
# (often extracephalic or over a contralateral region).
#
# tACS: typically 1-2 mA peak-to-peak, at a frequency matched to a hypothesized
# oscillatory mechanism (e.g. 10 Hz for alpha entrainment, 40 Hz for gamma).
#
# Electrode montage (position of anode/cathode or stimulating electrodes) is
# itself a research decision determined by the target region and current-flow
# modeling — not read off a fixed lookup table.
```

## Current-flow modeling (montage planning)

```python
# Individual head models (from structural MRI, via tools like SimNIBS) predict
# the actual current density distribution for a given montage — scalp electrode
# position doesn't map simply onto which cortical region receives the strongest
# field, due to skull/CSF/gyral folding effects on current flow.
import simnibs
# simnibs workflow: build a head model from structural MRI (headreco/charm),
# then run a simulation for a candidate montage to check predicted field strength
# and focality at the intended target before running a study with that montage.
```

## Blinding/sham verification

```python
# Standard sham condition: brief ramp-up/ramp-down current (mimicking the
# initial tingling sensation) without sustained stimulation — verify blinding
# effectiveness by asking participants to guess their condition post-session,
# and report the blinding-check result, not just assume sham felt identical.
```

## Validation & Pitfalls

Canonical references: Nitsche & Paulus (2000), "Excitability changes induced in the human motor
cortex by weak transcranial direct current stimulation," *Journal of Physiology*, for the original
tDCS polarity model; Horvath, Forte & Carter (2015), "Quantitative review finding no evidence of
cognitive effects in healthy populations from single-session transcranial direct current stimulation
(tDCS)," *Brain Stimulation*, for a well-known critical reassessment of tDCS effect reliability.

- **The classic "anode excitatory, cathode inhibitory" tDCS model is an oversimplification that
  doesn't reliably hold outside primary motor cortex (where it was originally established) or across
  individuals** — don't assume this polarity rule transfers to a different target region or task
  without citing region-specific evidence.
- **tDCS/tACS effect sizes are small and highly variable across individuals and studies — several
  systematic reviews (including Horvath et al. above) have found inconsistent or null effects for
  commonly claimed cognitive benefits.** Treat a single-study tDCS/tACS cognitive effect claim with
  the same skepticism the field's own replication record warrants; a properly powered, pre-registered
  design is especially important here given the literature's documented reliability problems.
- **Current-flow through the skull and scalp is highly individual-specific (skull thickness, CSF
  volume, gyral folding)** — a fixed electrode montage does not deliver the same field strength to the
  same cortical target across participants. Individualized current-flow modeling (SimNIBS or
  equivalent) is increasingly considered best practice rather than optional refinement, especially for
  clinical/high-stakes applications.
- **Sham blinding is imperfect, particularly at higher current intensities and with repeated
  sessions** — participants above chance can often correctly guess active vs. sham. Report a blinding
  check, don't assume blinding succeeded by protocol design alone.
