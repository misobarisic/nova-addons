"""Tagged releases package current sources using published runtime tools."""
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

    def test_only_published_runtime_refs_are_emitted(self):
        self.assertEqual(REFS.release_refs(self.compatibility()), {
            "nova": "v0.0.57", "reader": "v0.1.26",
        })

    def test_external_reader_reference_is_rejected(self):
        compatibility = self.compatibility()
        compatibility["nova-reader"]["referenceRef"] = "0123456789abcdef0123456789abcdef01234567"
        with self.assertRaisesRegex(ValueError, "obsolete"):
            REFS.release_refs(compatibility)

    def test_runtime_still_requires_version_tag(self):
        for invalid in (None, 123, "main", "a" * 40, "v0.1.26\n", "v0.1.26/other"):
            with self.subTest(runtime=invalid):
                compatibility = self.compatibility()
                compatibility["nova-reader"]["ref"] = invalid
                with self.assertRaisesRegex(ValueError, "published version tag"):
                    REFS.release_refs(compatibility)

    def test_invalid_config_emits_no_actions_outputs(self):
        compatibility = self.compatibility()
        compatibility["nova-reader"]["ref"] = "main"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "compatibility.json"
            path.write_text(json.dumps(compatibility), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/runtime-refs.py"), str(path)],
                capture_output=True, text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("published version tag", result.stderr)

    def test_workflow_uses_published_runtime_tools(self):
        workflow = (ROOT / ".github/workflows/release-addons.yml").read_text()
        self.assertIn('python3 scripts/runtime-refs.py >> "$GITHUB_OUTPUT"', workflow)
        self.assertIn("ref: ${{ steps.runtime.outputs.reader }}\n          path: runtimes/nova-reader", workflow)
        self.assertIn("--manifest-path runtimes/nova-reader/crates/reader-sources/Cargo.toml", workflow)
        self.assertIn("--reader-root runtimes/nova-reader", workflow)
        self.assertNotIn("reader-reference", workflow)
        self.assertNotIn("references/nova-reader", workflow)
        self.assertEqual(workflow.count("repository: misobarisic/nova-reader"), 1)
        compatibility = json.loads((ROOT / "compatibility.json").read_text())
        self.assertEqual(compatibility["nova-reader"]["ref"], "v0.1.26")
        self.assertNotIn("referenceRef", compatibility["nova-reader"])


if __name__ == "__main__":
    unittest.main()
