#!/usr/bin/env python3
"""Resolve published runtime tags used to package tagged addon releases."""
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
    if "referenceRef" in compatibility["nova-reader"]:
        raise ValueError("Reader referenceRef is obsolete; releases package current source inputs")
    return refs


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("compatibility.json")
    refs = release_refs(json.loads(path.read_text(encoding="utf-8")))
    # Validate all refs before writing any Actions output.
    for key, ref in refs.items():
        print(f"{key}={ref}")


if __name__ == "__main__":
    main()
