"""Canonical Reader inputs and historical ZIPs live entirely in Nova Addons."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("package_all", ROOT / "scripts/package-all.py")
PACKAGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACKAGE)

# These previously released byte identities were migrated unchanged from
# Reader's packaging regression, independently of the editable SHA256SUMS index.
ORIGINAL_RELEASES = {
    "manhwa18cc-1.0.1.zip": "9052373c938281bf99d51adb99fe01d11449da482db8811b182cddd003d22261",
    "mangafire-1.0.0.zip": "db2bebbcc3363ac2e7b521e53f8524f4aaaf0b277044b84bd459774838999797",
    "mangafire-1.0.1.zip": "d649274c7c2891df86eb6fc9abc28eb9ac285740f53dd82ada5a48f2853a62fb",
    "kagane-1.0.0.zip": "28ff94cc3b6c1720c9235f03a1410702fd8c056c341d0365f91dc45f07f17212",
    "cosplaytele-1.0.0.zip": "fca6428f39d2671eadcaf84a342a39b82efa1a568a996cb0b6d6e26f251f6375",
}


class ReaderPackagesTests(unittest.TestCase):
    def test_original_released_archives_remain_immutable_after_updates(self):
        goldens = PACKAGE.reader_goldens()
        for name, digest in ORIGINAL_RELEASES.items():
            with self.subTest(archive=name):
                self.assertEqual(hashlib.sha256(goldens[name].read_bytes()).hexdigest(), digest)

    def test_all_current_packages_match_repository_local_goldens(self):
        goldens = PACKAGE.reader_goldens()
        directories = sorted(path for path in (ROOT / "reader-addons").iterdir() if path.is_dir())
        self.assertEqual(len(directories), 6)
        for source in directories:
            with self.subTest(source=source.name):
                manifest, files = PACKAGE.declared_files(source, "nova-reader")
                name = f"{manifest['id']}-{manifest['version']}.zip"
                self.assertIn(name, goldens)
                PACKAGE.audit_archive(goldens[name], source, files, "nova-reader")
                self.assertIn("LICENSE", files)
                self.assertIn("NOTICE.md", files)
                self.assertFalse(set(files) & {"tests", "fixtures", "node_modules"})

    def test_historical_archive_members_are_deterministic_and_declared(self):
        for name, path in PACKAGE.reader_goldens().items():
            with self.subTest(archive=name), zipfile.ZipFile(path) as archive:
                manifest = json.loads(archive.read("manifest.json"))
                files = sorted(["manifest.json", manifest["entry"], *manifest.get("scripts", []),
                                *manifest.get("assets", [])])
                self.assertEqual(archive.namelist(), files)
                for entry in archive.infolist():
                    self.assertEqual(entry.date_time, (1980, 1, 1, 0, 0, 0))
                    self.assertEqual(entry.create_system, 3)
                    self.assertEqual(entry.external_attr >> 16, 0o100644)
                    self.assertEqual(entry.compress_type, zipfile.ZIP_DEFLATED)
                    self.assertFalse(set(Path(entry.filename).parts) & {"tests", "fixtures", "node_modules"})

    def golden_copy(self, temporary):
        target = Path(temporary) / "reader-packages"
        shutil.copytree(ROOT / "reader-packages", target)
        return target

    def test_modified_golden_fails_before_packaging(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = self.golden_copy(temporary)
            archive = target / "kagane-1.0.0.zip"
            archive.write_bytes(archive.read_bytes() + b"changed")
            with self.assertRaisesRegex(ValueError, "changed bytes"):
                PACKAGE.reader_goldens(target)

    def test_missing_extra_duplicate_and_unsafe_golden_entries_are_rejected(self):
        for mutation in ("missing", "extra", "duplicate", "unsafe"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                target = self.golden_copy(temporary)
                index = target / "SHA256SUMS"
                if mutation == "missing":
                    (target / "kagane-1.0.0.zip").unlink()
                elif mutation == "extra":
                    (target / "unreviewed-1.0.0.zip").write_bytes(b"unreviewed")
                elif mutation == "duplicate":
                    index.write_text(index.read_text() + index.read_text().splitlines()[0] + "\n")
                else:
                    index.write_text("0" * 64 + "  ../escape.zip\n")
                with self.assertRaises(ValueError):
                    PACKAGE.reader_goldens(target)

    def test_symlinked_golden_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = self.golden_copy(temporary)
            archive = target / "kagane-1.0.0.zip"
            archive.unlink()
            archive.symlink_to(ROOT / "reader-packages/kagane-1.0.0.zip")
            with self.assertRaisesRegex(ValueError, "regular file"):
                PACKAGE.reader_goldens(target)


if __name__ == "__main__":
    unittest.main()
