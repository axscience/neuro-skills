## What skill does this add/change?

<!-- Name, modality or technique, one-line summary -->

## Checklist

- [ ] `SKILL.md` frontmatter is complete (`name`, `description`, `license`, `metadata.modality`)
- [ ] `metadata.modality` matches the top-level folder it's in
- [ ] `SKILL.md` has `## Overview` and `## Validation & Pitfalls`; if it has a `references/` folder,
      it has a routing table linking every reference
- [ ] Every `references/*.md` file has a `## Validation & Pitfalls` section
- [ ] Validation & Pitfalls cites a real reference and lists concrete failure modes (not "read the docs")
- [ ] `python scan_skills.py` passes
- [ ] Added/updated the corresponding row(s) in `docs/skills.md`
- [ ] If this could plausibly overlap an existing cross-cutting skill (`neuro-stats`,
      `neuro-connectivity`, `neuro-decoding-encoding`, `clinical-biomarkers-ml`), checked
      `docs/skills.md`'s ownership notes and linked instead of restating
