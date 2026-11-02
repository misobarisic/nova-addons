#!/usr/bin/env python3
"""Resolve published runtime tags and an optional immutable Reader golden pin."""
import json
from pathlib import Path
import re
import sys


def release_refs(compatibility):
    refs = {}
    for app, key in (("nova", "nova"), ("nova-reader", "reader")):
        ref = compatibility[app]["ref"]
        if not isinstance(ref, str) or not re.fullmatch(r"v[A-Za-z0-9._+\-]+", ref):
            raise ValueError("runtime ref must be a published version tag")
        refs[key] = ref
    reader = compatibility["nova-reader"]
    if "referenceRef" in reader:
        reference = reader["referenceRef"]
        if not isinstance(reference, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", reference):
            raise ValueError("Reader referenceRef must be a full 40-hex commit")
    else:
        reference = refs["reader"]
    refs["reader-reference"] = reference
    return refs


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("compatibility.json")
    refs = release_refs(json.loads(path.read_text(encoding="utf-8")))
    # Validate all refs before writing any Actions output.
    for key, ref in refs.items():
        print(f"{key}={ref}")


if __name__ == "__main__":
    main()
