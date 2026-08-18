# Public Dataset Access

Practical fetch code for [../SKILL.md](../SKILL.md)'s two standards — three sources covering most
public neuroscience data: DANDI (NWB), OpenNeuro (BIDS), and the Allen Institute (curated, richly
annotated NWB-adjacent datasets with their own SDK).

## DANDI Archive (NWB — ephys, calcium imaging, behavior)

```python
from dandi.dandiapi import DandiAPIClient

with DandiAPIClient() as client:
    dandiset = client.get_dandiset("000409")
    print(dandiset.get_metadata().description)
    for asset in dandiset.get_assets():
        print(asset.path, f"{asset.size / 1e9:.2f} GB")

    asset = dandiset.get_asset_by_path("sub-1/sub-1_ses-1_ecephys.nwb")
    asset.download("session.nwb")
```

```bash
dandi download https://dandiarchive.org/dandiset/000409   # full dandiset, CLI
```

Streaming a remote NWB file without a full download (for large files where only a slice is needed):

```python
import fsspec
from pynwb import NWBHDF5IO
import h5py

s3_url = asset.get_content_url(follow_redirects=1, strip_query=True)
with fsspec.open(s3_url, "rb") as f:
    with NWBHDF5IO(file=h5py.File(f, "r"), load_namespaces=True) as io:
        nwbfile = io.read()
```

## OpenNeuro (BIDS — fMRI, EEG, MEG, iEEG)

```python
import openneuro

openneuro.download(
    dataset="ds000228", target_dir="ds000228",
    include=["sub-01", "participants.tsv"],  # partial download — see pitfalls on full-dataset size
)
```

## Allen Institute (AllenSDK — Neuropixels, Ophys, Cell Types)

```python
from allensdk.brain_observatory.ecephys.ecephys_project_cache import EcephysProjectCache

cache = EcephysProjectCache.from_warehouse(manifest="ecephys_manifest.json")
sessions = cache.get_session_table()
session = cache.get_session_data(sessions.index[0])   # downloads on first access, then cached

units = session.units
good_units = units[
    (units["isi_violations"] < 0.5) & (units["amplitude_cutoff"] < 0.1) & (units["presence_ratio"] > 0.9)
]
```

## Validation & Pitfalls

- **Asset sizes are commonly tens to hundreds of GB per session/dataset.** List assets and check
  sizes before a full download; stream or selectively download when prototyping. This applies to all
  three sources equally.
- **A dandiset/dataset's "draft" version can change under you.** DANDI dandisets have a mutable draft
  and immutable numbered releases — pin to a specific version for reproducible analysis.
- **AllenSDK's `session.units` includes every detected unit, not just clean single units** — filter
  on the provided QC columns before treating results as single-neuron data (same principle as spike
  sorting quality metrics in `spike-recording`).
- **Licenses vary per dataset, not per archive.** Check the specific dataset's license before use in
  a publication, even within the same archive.
- **First access to Allen session data downloads it; a loop over many sessions can trigger
  unplanned large-scale downloads.** Filter the session table by metadata (brain region, session
  type) before bulk-fetching data.
