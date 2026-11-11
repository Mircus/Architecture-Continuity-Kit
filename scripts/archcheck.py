#!/usr/bin/env python3
"""Lightweight, dependency-free (Python >=3.11) architecture inspector.

Checks declared components, local evidence files, cycles and simple static Python
imports. It is NOT a substitute for tests, runtime tracing, or full import analysis.
"""
import argparse
import ast
import subprocess
import sys
import tomllib
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "architecture.toml"
REPORT = ROOT / "docs" / "ARCHITECTURE.generated.md"


def load():
    with MAP.open("rb") as f:
        data = tomllib.load(f)
    return data["project"], data["components"]


def within_root(rel):
    candidate = (ROOT / rel).resolve()
    if not candidate.is_relative_to(ROOT):
        raise ValueError(f"path escapes project directory: {rel}")
    return candidate


def component_for_import(name, components):
    # Longest prefix wins: demo.core.x belongs to demo.core.
    matches = [c for c in components if name == c["package"]
               or name.startswith(c["package"] + ".")]
    return max(matches, key=lambda c: len(c["package"])) if matches else None


def imports_in(file, package):
    tree = ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
    # AST detects syntactic imports, not reflective/dynamic imports.
    relative_module = file.relative_to(ROOT).with_suffix("")
    module_parts = list(relative_module.parts)
    if module_parts[-1] == "__init__":
        current_package_parts = module_parts[:-1]
    else:
        current_package_parts = module_parts[:-1]
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names += [(node.lineno, alias.name) for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                keep = len(current_package_parts) - (node.level - 1)
                prefix = current_package_parts[:max(0, keep)]
                base = ".".join(prefix + ([node.module] if node.module else []))
            else:
                base = node.module or ""
            if base:
                names.append((node.lineno, base))
            for alias in node.names:
                if alias.name != "*" and base:
                    names.append((node.lineno, base + "." + alias.name))
    return names


def check(components, project):
    errors = []
    known = {}
    packages = set()
    for c in components:
        label = c.get("id", "<missing id>")
        if label in known:
            errors.append(f"duplicate component id {label}")
        known[label] = c
        for field in ("id", "path", "package", "purpose", "owner", "evidence"):
            if not c.get(field):
                errors.append(f"{label}: missing {field}")
        if c.get("package") in packages:
            errors.append(f"duplicate package {c.get('package')}")
        packages.add(c.get("package"))
        try:
            component_path = within_root(c["path"])
            if not component_path.is_dir():
                errors.append(f"{label}: component directory does not exist: {c['path']}")
        except (KeyError, ValueError) as exc:
            errors.append(f"{label}: {exc}")
        for e in c.get("evidence", []):
            try:
                if not within_root(e).is_file():
                    errors.append(f"{label}: evidence file absent: {e}")
            except ValueError as exc:
                errors.append(f"{label}: {exc}")
    for c in components:
        label = c.get("id", "<missing>")
        for dep in c.get("dependencies", []):
            if dep not in known:
                errors.append(f"{label}: unknown dependency {dep}")
            if dep == label:
                errors.append(f"{label}: self-dependency")

    # Detect declared dependency cycles, not just immediate inversions.
    visited, visiting = set(), set()
    def visit(label):
        if label in visiting:
            errors.append(f"dependency cycle involving {label}")
            return
        if label in visited or label not in known:
            return
        visiting.add(label)
        for dep in known[label].get("dependencies", []):
            visit(dep)
        visiting.remove(label)
        visited.add(label)
    for label in known:
        visit(label)

    # Only statically visible imports between declared Python package roots.
    for c in components:
        try:
            folder = within_root(c["path"])
        except (KeyError, ValueError):
            continue
        if not folder.is_dir():
            continue
        for file in folder.rglob("*.py"):
            try:
                candidates = imports_in(file, c.get("package", ""))
            except (SyntaxError, UnicodeDecodeError) as exc:
                errors.append(f"{file.relative_to(ROOT)}: cannot parse: {exc}")
                continue
            for line, target in candidates:
                other = component_for_import(target, components)
                if other and other["id"] != c.get("id"):
                    if other["id"] not in c.get("dependencies", []):
                        errors.append(f"{file.relative_to(ROOT)}:{line}: {c['id']} "
                                      f"imports forbidden component {other['id']} ({target})")
    return errors


def render_report(project, components):
    lines = ["# Architecture map (generated)", "",
             "> DECLARED structure from `architecture.toml`; file and import checks are",
             "> performed separately by `archcheck.py`. A diagram is not runtime proof.", "",
             f"**Project:** {project['name']}", "",
             f"**Mission:** {project['mission']}", "",
             "## Components", "",
             "| Component | Responsibility | Owner | Declared dependencies | Evidence pointers |",
             "| --- | --- | --- | --- | --- |"]
    for c in components:
        dependencies = ", ".join(c["dependencies"]) or "None"
        evidence = ", ".join(f"`{e}`" for e in c["evidence"])
        cells = [f"`{c['id']}`", c["purpose"], c["owner"], dependencies, evidence]
        lines.append("| " + " | ".join(x.replace("|", "\\|") for x in cells) + " |")
    lines += ["", "## Declared component graph", "", "```mermaid", "flowchart LR"]
    for c in components:
        lines.append(f'  {c["id"]}["{c["id"]}"]')
    for c in components:
        for dep in c["dependencies"]:
            lines.append(f'  {c["id"]} --> {dep}')
    lines += ["```", "", "## Reading this map", "",
              "An arrow `A --> B` means A is **allowed/expected** to depend on B.",
              "The AST checker catches some forbidden Python imports; it cannot prove",
              "that all runtime links are captured. Compare this declared view with",
              "runtime traces and repository evidence before making strong claims.", ""]
    return "\n".join(lines)


def impact(components, files):
    direct = set()
    for path in files:
        path = Path(path).as_posix().lstrip("./")
        if path == "architecture.toml":
            direct = {c["id"] for c in components}
            break
        for c in components:
            root = c["path"].rstrip("/")
            if path == root or path.startswith(root + "/"):
                direct.add(c["id"])
    reverse = {c["id"]: set() for c in components}
    for c in components:
        for dep in c["dependencies"]:
            if dep in reverse:
                reverse[dep].add(c["id"])
    affected = set(direct)
    queue = deque(direct)
    while queue:
        for downstream in reverse[queue.popleft()]:
            if downstream not in affected:
                affected.add(downstream)
                queue.append(downstream)
    print("Directly changed:", ", ".join(sorted(direct)) or "none mapped")
    print("Potentially affected:", ", ".join(sorted(affected)) or "none mapped")
    print("This is dependency-based triage, not a proof of actual runtime effects.")
    if not direct:
        print("Review unmapped changes manually and update architecture.toml when appropriate.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("check", help="check declared map and basic Python import boundaries")
    sub.add_parser("report", help="regenerate docs/ARCHITECTURE.generated.md")
    imp = sub.add_parser("impact", help="estimate impacted components from changed paths")
    imp.add_argument("files", nargs="*", help="files changed, relative to repository root")
    imp.add_argument("--base", help="git ref compared to HEAD using three-dot diff")
    args = parser.parse_args()
    project, components = load()
    if args.command in (None, "check", "report"):
        errors = check(components, project)
        if errors:
            print("ARCHITECTURE CHECK FAILED", file=sys.stderr)
            for err in errors:
                print(" - " + err, file=sys.stderr)
            return 1
        if args.command == "report":
            REPORT.write_text(render_report(project, components), encoding="utf-8")
            print(f"Updated {REPORT.relative_to(ROOT)}")
        else:
            print(f"Architecture check passed ({len(components)} declared components).")
        return 0
    if args.command == "impact":
        files = list(args.files)
        if args.base:
            proc = subprocess.run(["git", "diff", "--name-only", f"{args.base}...HEAD"],
                                  cwd=ROOT, capture_output=True, text=True)
            if proc.returncode:
                print(f"git diff failed: {proc.stderr.strip()}", file=sys.stderr)
                return 2
            files += [p for p in proc.stdout.splitlines() if p]
        if not files:
            parser.error("impact needs changed file paths or --base")
        impact(components, files)
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
