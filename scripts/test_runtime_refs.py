"""Focused release-ref and runtime/reference checkout regressions."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("runtime_refs", ROOT / "scripts/runtime-refs.py")
REFS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REFS)


class ReleaseRefsTests(unittest.TestCase):
    def compatibility(self):
        return {"nova": {"ref": "v0.0.57"}, "nova-reader": {"ref": "v0.1.26"}}

    def test_missing_reference_defaults_to_published_runtime(self):
        self.assertEqual(REFS.release_refs(self.compatibility()), {
            "nova": "v0.0.57", "reader": "v0.1.26", "reader-reference": "v0.1.26",
        })

    def test_immutable_reference_does_not_change_runtime(self):
        compatibility = self.compatibility()
        pin = "0123456789abcdef0123456789abcdef01234567"
        compatibility["nova-reader"]["referenceRef"] = pin
        refs = REFS.release_refs(compatibility)
        self.assertEqual(refs["reader"], "v0.1.26")
        self.assertEqual(refs["reader-reference"], pin)

    def test_reference_requires_exactly_40_hex_characters(self):
        for invalid in (None, True, 123, {}, [], "", "main", "v0.1.26", "a" * 39,
                        "a" * 41, "g" * 40, "a" * 40 + "\n", " " + "a" * 40,
                        "a" * 40 + "\nreader=main"):
            with self.subTest(reference=invalid):
                compatibility = self.compatibility()
                compatibility["nova-reader"]["referenceRef"] = invalid
                with self.assertRaisesRegex(ValueError, "40-hex commit"):
                    REFS.release_refs(compatibility)

    def test_runtime_still_requires_version_tag(self):
        for invalid in (None, 123, "main", "a" * 40, "v0.1.26\n", "v0.1.26/other"):
            with self.subTest(runtime=invalid):
                compatibility = self.compatibility()
                compatibility["nova-reader"]["ref"] = invalid
                with self.assertRaisesRegex(ValueError, "published version tag"):
                    REFS.release_refs(compatibility)

    def test_invalid_reference_emits_no_actions_outputs(self):
        compatibility = self.compatibility()
        compatibility["nova-reader"]["referenceRef"] = "main"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "compatibility.json"
            path.write_text(json.dumps(compatibility), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/runtime-refs.py"), str(path)],
                capture_output=True, text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("40-hex commit", result.stderr)

    def test_workflow_keeps_runtime_builds_separate_from_reference_goldens(self):
        workflow = (ROOT / ".github/workflows/release-addons.yml").read_text()
        self.assertIn('python3 scripts/runtime-refs.py >> "$GITHUB_OUTPUT"', workflow)
        self.assertIn("ref: ${{ steps.runtime.outputs.reader }}\n          path: runtimes/nova-reader", workflow)
        self.assertIn("ref: ${{ steps.runtime.outputs.reader-reference }}\n          path: references/nova-reader", workflow)
        self.assertIn("--manifest-path runtimes/nova-reader/crates/reader-sources/Cargo.toml", workflow)
        self.assertIn("--reader-root runtimes/nova-reader", workflow)
        self.assertIn("--reader-reference-dir references/nova-reader/addons", workflow)
        self.assertNotIn("--reader-root references/nova-reader", workflow)


if __name__ == "__main__":
    unittest.main()
