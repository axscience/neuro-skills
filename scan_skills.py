#!/usr/bin/env python3
"""Validate the modality-first skill tree: frontmatter schema, modality-folder
consistency, required sections, reference discoverability, and dead internal
links. Stdlib only — no dependencies to install.

Usage: python scan_skills.py
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent

NON_SKILL_DIRS = {".git", ".github", "docs", "integration-templates", ".claude-plugin"}

REQUIRED_FRONTMATTER = ["name", "description", "license", "metadata"]
REQUIRED_SKILL_SECTIONS = ["## Overview", "## When to use this skill"]
VALIDATION_SECTION_PREFIX = "## Validation & Pitfalls"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
LINK_RE = re.compile(r"\]\(([^)]+\.md[^)]*)\)")


def parse_frontmatter(text):
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None, text
    raw, body = match.group(1), text[match.end():]

    data, metadata = {}, {}
    in_metadata = False
    for line in raw.splitlines():
        if not line.strip():
            continue
        if line.startswith("metadata:"):
            in_metadata = True
            continue
        if in_metadata and line.startswith("  "):
            key, _, val = line.strip().partition(":")
            metadata[key.strip()] = val.strip().strip('"')
            continue
        in_metadata = False
        key, _, val = line.partition(":")
        data[key.strip()] = val.strip()
    data["metadata"] = metadata
    return data, body


def has_section(body, prefix_or_exact, exact=False):
    for line in body.splitlines():
        if exact:
            if line.strip() == prefix_or_exact:
                return True
        elif line.strip().startswith(prefix_or_exact):
            return True
    return False


def validate_reference(ref_path, modality_dir):
    errors = []
    text = ref_path.read_text()
    if not text.lstrip().startswith("#"):
        errors.append(f"{ref_path}: doesn't start with a top-level '# ' title")
    if not has_section(text, VALIDATION_SECTION_PREFIX):
        errors.append(f"{ref_path}: missing a '{VALIDATION_SECTION_PREFIX}' section")
    for link in LINK_RE.findall(text):
        link_path = link.split("#")[0]  # strip any anchor
        if link_path.startswith("http"):
            continue
        target = (ref_path.parent / link_path).resolve()
        if not target.exists():
            errors.append(f"{ref_path}: broken link to '{link}'")
    return errors


def _link_errors(body, base_dir, skill_md):
    errors = []
    for link in LINK_RE.findall(body):
        link_path = link.split("#")[0]
        if link_path.startswith("http"):
            continue
        if not (base_dir / link_path).resolve().exists():
            errors.append(f"{skill_md}: broken link to '{link}'")
    return errors


def validate_skill_md(skill_md, expected_name, parent_category=None):
    """Validate a single SKILL.md. If parent_category is set, this is a leaf
    (metadata.category must equal the parent); otherwise it's a flat skill or a
    category router (metadata.category must equal its own folder name). The
    deprecated metadata.modality field is rejected. Returns (errors, body)."""
    errors = []
    frontmatter, body = parse_frontmatter(skill_md.read_text())
    if frontmatter is None:
        return [f"{skill_md}: missing or malformed frontmatter block"], ""

    for key in REQUIRED_FRONTMATTER:
        if not frontmatter.get(key):
            errors.append(f"{skill_md}: missing required frontmatter field '{key}'")

    if frontmatter.get("name") != expected_name:
        errors.append(
            f"{skill_md}: frontmatter name '{frontmatter.get('name')}' != folder name '{expected_name}'"
        )

    meta = frontmatter.get("metadata", {})
    if meta.get("modality") is not None:
        errors.append(
            f"{skill_md}: uses deprecated metadata.modality — rename it to metadata.category"
        )
    expected_category = parent_category if parent_category is not None else expected_name
    if meta.get("category") != expected_category:
        errors.append(
            f"{skill_md}: metadata.category '{meta.get('category')}' != expected '{expected_category}'"
        )

    for section in REQUIRED_SKILL_SECTIONS:
        if not has_section(body, section, exact=True):
            errors.append(f"{skill_md}: missing required section '{section}'")
    if not has_section(body, VALIDATION_SECTION_PREFIX):
        errors.append(f"{skill_md}: missing a '{VALIDATION_SECTION_PREFIX}' section")

    errors.extend(_link_errors(body, skill_md.parent, skill_md))
    return errors, body


def leaf_subdirs(d):
    return sorted(s for s in d.iterdir() if s.is_dir() and (s / "SKILL.md").exists())


def validate_flat(d):
    """A flat skill: SKILL.md + optional references/, no skill-bearing subdirs."""
    skill_md = d / "SKILL.md"
    if not skill_md.exists():
        return [f"{d}: missing SKILL.md"]
    errors, body = validate_skill_md(skill_md, d.name)

    references_dir = d / "references"
    for ref_path in sorted(references_dir.glob("*.md")) if references_dir.exists() else []:
        rel_link = f"references/{ref_path.name}"
        if rel_link not in body:
            errors.append(
                f"{skill_md}: {rel_link} exists but isn't linked from SKILL.md — "
                f"add it to the routing table so it's discoverable"
            )
        errors.extend(validate_reference(ref_path, d))
    return errors


def validate_category(d, leaves):
    """A category: router SKILL.md + one or more leaf skill subdirs."""
    skill_md = d / "SKILL.md"
    errors, body = validate_skill_md(skill_md, d.name)
    for leaf in leaves:
        rel_link = f"{leaf.name}/SKILL.md"
        if rel_link not in body:
            errors.append(
                f"{skill_md}: leaf '{leaf.name}' exists but isn't linked from the category router — "
                f"add it to the 'Which leaf skill to load' table"
            )
        leaf_errors, _ = validate_skill_md(leaf / "SKILL.md", leaf.name, parent_category=d.name)
        errors.extend(leaf_errors)
    return errors


def all_skill_md_paths():
    """Every SKILL.md in the repo (categories, leaves, flat skills), repo-relative."""
    paths = []
    for d in sorted(p for p in REPO_ROOT.iterdir()
                    if p.is_dir() and p.name not in NON_SKILL_DIRS and not p.name.startswith(".")):
        if (d / "SKILL.md").exists():
            paths.append((d / "SKILL.md").relative_to(REPO_ROOT).as_posix())
        for leaf in leaf_subdirs(d):
            paths.append((leaf / "SKILL.md").relative_to(REPO_ROOT).as_posix())
    return set(paths)


def parse_registry(registry_path):
    """Minimal stdlib parser for registry.yaml's flat `entries:` list. Returns a
    list of dicts with name/type/category/path (the fields we cross-validate).
    Avoids a pyyaml dependency to keep the validator runnable anywhere."""
    entries, current = [], None
    field_re = re.compile(r'^\s*(?:-\s*)?(name|type|sub_type|category|path):\s*"?([^"#]+?)"?\s*$')
    for line in registry_path.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or not stripped:
            continue
        if stripped.startswith("- name:"):
            if current:
                entries.append(current)
            current = {}
        if current is None:
            continue
        m = field_re.match(line)
        if m:
            current[m.group(1)] = m.group(2).strip()
    if current:
        entries.append(current)
    return entries


def validate_registry(registry_path):
    """Cross-validate registry.yaml against the filesystem: every SKILL.md has
    exactly one entry, every entry path resolves and matches its frontmatter
    name, category fields are consistent, and there are no duplicate names."""
    errors = []
    if not registry_path.exists():
        return [f"{registry_path.name}: missing (registry is required)"]

    entries = parse_registry(registry_path)
    disk_paths = all_skill_md_paths()
    registry_paths = set()
    seen_names = set()

    for e in entries:
        path = e.get("path")
        name = e.get("name")
        if not path or not name:
            errors.append(f"registry: entry missing name or path: {e}")
            continue
        if name in seen_names:
            errors.append(f"registry: duplicate entry name '{name}'")
        seen_names.add(name)
        registry_paths.add(path)

        skill_md = REPO_ROOT / path
        if not skill_md.exists():
            errors.append(f"registry: entry '{name}' path does not resolve: {path}")
            continue
        frontmatter, _ = parse_frontmatter(skill_md.read_text())
        fm_name = (frontmatter or {}).get("name")
        if fm_name != name:
            errors.append(f"registry: entry name '{name}' != frontmatter name '{fm_name}' ({path})")
        # category consistency: leaves live in <category>/<leaf>/SKILL.md
        parts = path.split("/")
        expected_cat = parts[0]
        if e.get("category") != expected_cat:
            errors.append(f"registry: entry '{name}' category '{e.get('category')}' != path root '{expected_cat}'")

    for missing in sorted(disk_paths - registry_paths):
        errors.append(f"registry: SKILL.md on disk has no registry entry: {missing}")
    for extra in sorted(registry_paths - disk_paths):
        errors.append(f"registry: entry path not found on disk: {extra}")
    return errors


def main():
    top_dirs = sorted(
        p for p in REPO_ROOT.iterdir()
        if p.is_dir() and p.name not in NON_SKILL_DIRS and not p.name.startswith(".")
    )
    if not top_dirs:
        print("No skill directories found.")
        return 0

    all_errors = []
    n_flat = n_category = n_leaf = 0
    for d in top_dirs:
        if not (d / "SKILL.md").exists():
            all_errors.append(f"{d}: missing SKILL.md")
            continue
        leaves = leaf_subdirs(d)
        if leaves:
            n_category += 1
            n_leaf += len(leaves)
            all_errors.extend(validate_category(d, leaves))
        else:
            n_flat += 1
            all_errors.extend(validate_flat(d))

    registry_errors = validate_registry(REPO_ROOT / "registry.yaml")
    all_errors.extend(registry_errors)

    total = n_flat + n_category + n_leaf
    summary = (f"{total} skill(s) ({n_flat} flat, {n_category} "
               f"categor{'y' if n_category == 1 else 'ies'}, {n_leaf} leaves) + registry")
    if all_errors:
        print(f"Validated {summary} — {len(all_errors)} problem(s):\n")
        for error in all_errors:
            print(f"  - {error}")
        return 1

    print(f"Validated {summary} — all passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
