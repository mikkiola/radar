#!/usr/bin/env python3
"""Component + VC-source-pattern discovery, plus structural validation.

Steps 1-2 of the SPEC -> checklist -> harness -> drift -> doc-sync
automation track.

Step 1: scans the repo for SPEC.md files and determines, for each,
whether it carries a "## Milestones" section with checkbox lines --
its VC-source pattern. A paired CHECKPOINT.md was a second valid
pattern historically; deprecated 2026-08-20 (DocOps SPEC.md M6,
ADR-0037) because a CHECKPOINT.md's mere presence silently overrode a
SPEC.md's own inline Milestones section, even a well-formed one --
confirmed live against this project's own DocOps SPEC.md, whose inline
Milestones went unvalidated for two full commits while a stale,
topically-unrelated CHECKPOINT.md sat next to it. SPEC.md's own inline
content is now the only VC-source pattern.

Step 2: for each discovered source_file, confirms it's structurally
parseable into individual verification-criteria-like units (an inline
Milestones checkbox line with description text) — and reports which
units, if any, are malformed. Does not extract actual VC-IDs or build
a checklist — that's a later step.
"""
import argparse
import json
import re
import sys
from pathlib import Path

MILESTONES_HEADING_RE = re.compile(r"^##\s+Milestones\b", re.MULTILINE)
NEXT_HEADING_RE = re.compile(r"^##\s+\S", re.MULTILINE)
CHECKBOX_LINE_RE = re.compile(r"^\s*(?:-|\d+\.)\s*\[[ xX]\]", re.MULTILINE)
CHECKBOX_FULL_LINE_RE = re.compile(r"^[ \t]*(?:-|\d+\.)\s*\[[ xX]\](.*)$", re.MULTILINE)
FIELD_LINE_RE = re.compile(r"^([ \t]*)(verify|done-when):\s*(.*)$")

# Directories that hold project infrastructure, not a pipeline
# component, and are therefore never SPEC.md/component candidates.
NON_COMPONENT_DIRS = {"docs", "scripts"}


def find_spec_files(repo_root: Path) -> list[Path]:
    """SPEC.md at repo root, plus SPEC.md directly inside any
    immediate subdirectory. Does not recurse further, does not
    hardcode any specific file path."""
    found = []
    root_spec = repo_root / "SPEC.md"
    if root_spec.is_file():
        found.append(root_spec)
    for child in sorted(repo_root.iterdir()):
        if not child.is_dir() or child.name.startswith(".") or child.name in NON_COMPONENT_DIRS:
            continue
        candidate = child / "SPEC.md"
        if candidate.is_file():
            found.append(candidate)
    return found


def component_candidate_dirs(repo_root: Path, owned_dirs: set) -> list:
    """Immediate subdirectories that could be the component a
    root-level SPEC.md documents: excludes infra dirs and any
    directory that already owns its own SPEC.md (that directory's
    component identity is already resolved directly, not inferred)."""
    dirs = []
    for child in sorted(repo_root.iterdir()):
        if not child.is_dir() or child.name.startswith(".") or child.name in NON_COMPONENT_DIRS:
            continue
        if child.name in owned_dirs:
            continue
        dirs.append(child.name)
    return dirs


def resolve_component_name(spec_path: Path, repo_root: Path, owned_dirs: set):
    """Returns (component_name, ambiguous).

    A SPEC.md living directly inside a component directory: that
    directory's name IS the component name, unambiguous.

    A SPEC.md at repo root: the component it documents isn't given by
    its own location, so it's inferred from its text. Strong signal:
    an explicit "<repo-dir-name>/<component>/" path (the pattern a
    SPEC's own "code location" section uses to state where a
    component's code actually lives). Fallback: bare "<component>/"
    occurrence count. If neither resolves to a single candidate,
    ambiguous=True and a best guess is still returned.
    """
    parent = spec_path.parent
    if parent != repo_root:
        return parent.name, False

    text = spec_path.read_text(encoding="utf-8")
    candidates = component_candidate_dirs(repo_root, owned_dirs)
    if not candidates:
        return repo_root.name, True

    strong_counts = {
        d: len(re.findall(re.escape(f"{repo_root.name}/{d}/"), text))
        for d in candidates
    }
    strong_hits = {d: c for d, c in strong_counts.items() if c > 0}
    if len(strong_hits) == 1:
        return next(iter(strong_hits)), False

    bare_counts = {
        d: len(re.findall(re.escape(f"{d}/"), text)) for d in candidates
    }
    max_count = max(bare_counts.values(), default=0)
    top = [d for d, c in bare_counts.items() if c == max_count and c > 0]
    if len(top) == 1:
        return top[0], False

    best_guess = sorted(top)[0] if top else sorted(candidates)[0]
    return best_guess, True


def isolate_milestones_section(text: str):
    """Returns (section_text, section_start_offset), or (None, None)
    if there's no "## Milestones" heading. section_start_offset is
    the absolute offset of the section's start within `text`, used to
    recover real line numbers for anything found inside it."""
    match = MILESTONES_HEADING_RE.search(text)
    if not match:
        return None, None
    start = match.end()
    rest = text[start:]
    next_heading = NEXT_HEADING_RE.search(rest)
    end = start + (next_heading.start() if next_heading else len(rest))
    return text[start:end], start


def has_milestones_checkboxes(spec_path: Path) -> bool:
    text = spec_path.read_text(encoding="utf-8")
    section, _ = isolate_milestones_section(text)
    if section is None:
        return False
    return bool(CHECKBOX_LINE_RE.search(section))


def classify(spec_path: Path):
    """Returns (pattern, source_file).

    pattern is one of "inline_spec" / "UNKNOWN". "UNKNOWN" means no
    inline Milestones checklist was found — the component has zero
    tracked verification criteria, and this must never pass through
    silently. A paired CHECKPOINT.md is no longer consulted at all
    (deprecated 2026-08-20, ADR-0037) — see this module's docstring.
    """
    if has_milestones_checkboxes(spec_path):
        return "inline_spec", str(spec_path)
    return "UNKNOWN", None


def validate_inline_spec_structure(spec_path: str) -> dict:
    """Within the Milestones section (isolated via the same
    MILESTONES_HEADING_RE/NEXT_HEADING_RE logic Step 1 uses), each
    checkbox line must carry non-empty description text after the
    checkbox marker on that same line."""
    text = Path(spec_path).read_text(encoding="utf-8")
    section, section_start = isolate_milestones_section(text)

    if section is None:
        return {
            "status": "MALFORMED",
            "total_units": 0,
            "well_formed": 0,
            "malformed_details": [
                {"line": None, "text": "no '## Milestones' section found"}
            ],
        }

    matches = list(CHECKBOX_FULL_LINE_RE.finditer(section))
    if not matches:
        return {
            "status": "MALFORMED",
            "total_units": 0,
            "well_formed": 0,
            "malformed_details": [
                {"line": None, "text": "no checkbox lines found in Milestones section"}
            ],
        }

    total_units = len(matches)
    well_formed = 0
    malformed_details = []

    for match in matches:
        description = match.group(1).strip()
        if description:
            well_formed += 1
        else:
            abs_pos = section_start + match.start()
            line_no = text[:abs_pos].count("\n") + 1
            malformed_details.append({"line": line_no, "text": match.group(0).strip()})

    status = "MALFORMED" if malformed_details else "OK"
    return {
        "status": status,
        "total_units": total_units,
        "well_formed": well_formed,
        "malformed_details": malformed_details,
    }


def parse_milestone_fields(spec_path: str) -> list[dict]:
    """Extracts optional `verify:`/`done-when:` metadata (B-036) from
    every checkbox line in a SPEC.md, anywhere in the document -- not
    limited to isolate_milestones_section()'s narrow "## Milestones"-
    to-next-"##"-heading boundary (that boundary serves classify()'s
    component-discovery purpose; this is a separate, additive scan and
    does not share or alter it).

    Field-line contract:
    - `verify:`/`done-when:` are both optional per milestone.
    - When present, each sits at a fixed indent of exactly 2 spaces
      deeper than its own checkbox line's indent, single-line only,
      taken verbatim after the first colon following the key -- no
      escaping of embedded colons, backticks, or pipe characters.
    - Any other indented sub-line under a checkbox that isn't exactly
      a recognized key at that fixed indent is ordinary descriptive
      text: skipped, never an error.
    - A milestone's scanned block ends at the first blank line, the
      next checkbox line, or a line indented no deeper than the
      checkbox itself.
    """
    text = Path(spec_path).read_text(encoding="utf-8")
    lines = text.split("\n")

    results = []
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        cb_match = CHECKBOX_FULL_LINE_RE.match(line)
        if not cb_match:
            idx += 1
            continue

        indent = len(line) - len(line.lstrip(" \t"))
        description = cb_match.group(1).strip()
        line_no = idx + 1

        verify = None
        done_when = None
        j = idx + 1
        while j < len(lines):
            nxt = lines[j]
            if nxt.strip() == "":
                break
            if CHECKBOX_LINE_RE.match(nxt):
                break
            nxt_indent = len(nxt) - len(nxt.lstrip(" \t"))
            if nxt_indent <= indent:
                break
            field_match = FIELD_LINE_RE.match(nxt)
            if field_match and len(field_match.group(1)) == indent + 2:
                key, value = field_match.group(2), field_match.group(3).strip()
                if key == "verify" and verify is None:
                    verify = value
                elif key == "done-when" and done_when is None:
                    done_when = value
            j += 1

        results.append(
            {
                "line": line_no,
                "description": description,
                "verify": verify,
                "done_when": done_when,
            }
        )
        idx = j

    return results


def check_milestones_boundary_integrity(spec_path: str) -> dict:
    """Lint backstop for the [B-039] bug class: a milestone-detail
    section written at the "## " level truncates
    isolate_milestones_section()'s own output early, silently hiding
    later checkbox lines from classify()/validate_inline_spec_structure().

    Does NOT scan isolate_milestones_section()'s own output for a "##"
    heading -- that output can never contain one by construction (the
    function is defined to stop exactly at the first "## " heading it
    finds), so a check limited to it would always pass regardless of
    whether the bug is present. Instead cross-checks the isolated
    section's checkbox count against a whole-document checkbox count:
    if more checkboxes exist in the document than the isolated section
    captured, some are sitting outside the recognized Milestones
    boundary -- the actual, detectable signature of this bug class.
    """
    text = Path(spec_path).read_text(encoding="utf-8")
    section, _ = isolate_milestones_section(text)

    isolated_count = len(list(CHECKBOX_FULL_LINE_RE.finditer(section))) if section else 0
    total_count = len(list(CHECKBOX_FULL_LINE_RE.finditer(text)))

    if total_count > isolated_count:
        return {
            "status": "VIOLATION",
            "isolated_count": isolated_count,
            "total_count": total_count,
            "detail": (
                f"{total_count} checkbox line(s) exist in {spec_path}, but "
                f"isolate_milestones_section() only captured {isolated_count} "
                f"-- an interior '##' heading (or other boundary issue) is "
                f"likely truncating the Milestones section early."
            ),
        }
    return {"status": "OK", "isolated_count": isolated_count, "total_count": total_count}


def validate_structure(pattern: str, source_file) -> dict:
    if pattern == "inline_spec":
        return validate_inline_spec_structure(source_file)
    return {"status": "UNKNOWN", "total_units": 0, "well_formed": 0, "malformed_details": []}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repo root to scan (default: parent directory of scripts/)",
    )
    args = parser.parse_args()

    repo_root = (args.repo_root or Path(__file__).resolve().parent.parent).resolve()

    spec_files = find_spec_files(repo_root)
    if not spec_files:
        print("discover: no SPEC.md files found", file=sys.stderr)
        return 2

    # Resolve directories that own their own SPEC.md directly first,
    # so a root-level SPEC.md's inference excludes them as candidates.
    owned_dirs = {p.parent.name for p in spec_files if p.parent != repo_root}

    results = []

    for spec_path in spec_files:
        component, ambiguous = resolve_component_name(spec_path, repo_root, owned_dirs)
        pattern, source_file = classify(spec_path)

        if pattern == "UNKNOWN":
            print(
                f"discover: WARNING - {spec_path} has no '## Milestones' "
                f"section with checkbox lines. VC-source "
                f"pattern is UNKNOWN for this component; it carries zero "
                f"tracked verification criteria until this is resolved.",
                file=sys.stderr,
            )
        if ambiguous:
            print(
                f"discover: WARNING - could not unambiguously map {spec_path} "
                f"to a single component directory; best guess is "
                f"'{component}'.",
                file=sys.stderr,
            )

        structure = validate_structure(pattern, source_file)
        for detail in structure["malformed_details"]:
            if "heading" in detail:
                print(
                    f"discover: MALFORMED block in {source_file} — heading "
                    f"'{detail['heading']}' is missing: "
                    f"{', '.join(detail['missing_fields'])}",
                    file=sys.stderr,
                )
            else:
                where = f"{source_file}:{detail['line']}" if detail["line"] else source_file
                print(
                    f"discover: MALFORMED unit at {where} — {detail['text']!r}",
                    file=sys.stderr,
                )

        results.append(
            {
                "component": component,
                "spec_path": str(spec_path),
                "pattern": pattern,
                "source_file": source_file,
                "structure": structure,
            }
        )

    print(json.dumps(results, indent=2, ensure_ascii=False))

    any_not_ok = any(r["structure"]["status"] != "OK" for r in results)
    return 1 if any_not_ok else 0


if __name__ == "__main__":
    sys.exit(main())
