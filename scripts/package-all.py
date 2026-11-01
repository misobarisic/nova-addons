#!/usr/bin/env python3
"""Package both catalogs with app-owned recipes and production native parsers."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PRIVATE_DIRS = {"fixtures", "tests", "node_modules", "target", "dist", "build"}
PRIVATE_SUFFIXES = {".pem", ".key", ".keystore", ".p12", ".pfx"}


def run(command, **kwargs):
    return subprocess.run([str(part) for part in command], check=True, **kwargs)


def validator(runtime, package, prebuilt):
    if prebuilt:
        return [str(prebuilt.resolve())]
    return ["cargo", "run", "--quiet", "--locked", "--manifest-path",
            str(runtime / "crates" / package / "Cargo.toml"),
            "--example", "validate-package", "--"]


def declared_files(directory, app):
    """Audit package membership; schema validation belongs to the native parser."""
    if directory.is_symlink():
        raise ValueError(f"symlink addon directory: {directory}")
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    if app == "nova":
        names = ["manifest.json", "stremio-manifest.json", "LICENSE", "NOTICE.md",
                 *manifest.get("scripts", [manifest["entry"]]), *manifest.get("assets", [])]
    else:
        names = ["manifest.json", manifest["entry"], *manifest.get("scripts", []),
                 *manifest.get("assets", [])]
    for name in names:
        path = Path(name)
        if (not name or path.is_absolute() or "\\" in name or ":" in name
                or any(part in ("", ".", "..") for part in name.split("/"))
                or any(part.startswith(".") or part in PRIVATE_DIRS for part in path.parts)
                or path.suffix.lower() in PRIVATE_SUFFIXES):
            raise ValueError(f"private/development/unsafe package input: {name}")
        if any(directory.joinpath(*path.parts[:i]).is_symlink()
               for i in range(1, len(path.parts) + 1)):
            raise ValueError(f"symlink package input: {name}")
    return manifest, sorted(names)


def audit_archive(archive, directory, expected, app):
    with zipfile.ZipFile(archive) as package:
        if package.namelist() != expected:
            raise ValueError(f"unexpected package membership/order: {archive}")
        for info in package.infolist():
            compression = zipfile.ZIP_STORED if app == "nova" else zipfile.ZIP_DEFLATED
            if (info.date_time != (1980, 1, 1, 0, 0, 0) or info.create_system != 3
                    or info.external_attr >> 16 != 0o100644 or info.compress_type != compression):
                raise ValueError(f"non-deterministic archive metadata: {info.filename}")
            if package.read(info.filename) != (directory / info.filename).read_bytes():
                raise ValueError(f"recipe changed source bytes: {info.filename}")


def require_rejection(command, archive):
    result = subprocess.run([*command, str(archive)], capture_output=True, text=True)
    if result.returncode != 1 or not result.stderr.strip():
        raise ValueError(f"other app parser must reject {archive.name}: {result}")


def commit(runtime):
    return subprocess.check_output(["git", "-C", str(runtime), "rev-parse", "HEAD"], text=True).strip()


def package_all(args):
    roots = {"nova": args.nova_root.resolve(), "nova-reader": args.reader_root.resolve()}
    validators = {
        "nova": validator(roots["nova"], "providers", args.nova_validator),
        "nova-reader": validator(roots["nova-reader"], "reader-sources", args.reader_validator),
    }
    compatibility = json.loads((ROOT / "compatibility.json").read_text())
    inventory = {"schemaVersion": 1, "runtimes": {}, "packages": []}
    for app, runtime in roots.items():
        recipe = runtime / ("scripts/package-addon.py" if app == "nova" else "tools/package-addon.py")
        inventory["runtimes"][app] = {
            **compatibility[app], "commit": commit(runtime),
            "packagingRecipeSha256": hashlib.sha256(recipe.read_bytes()).hexdigest(),
        }
    output = args.output_dir.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    # Publish only after the complete catalog passed both parser boundaries and
    # reproducibility/member checks. Never modify an app's packaging recipe.
    with tempfile.TemporaryDirectory(prefix="nova-addons-", dir=output.parent) as temp:
        staging = Path(temp)
        for app in roots:
            source = ROOT / ("addons" if app == "nova" else "reader-addons")
            directories = sorted(p for p in source.iterdir() if p.is_dir())
            for directory in directories:
                manifest, expected = declared_files(directory, app)
                archives = []
                for attempt in ("first", "second"):
                    destination = staging / attempt / app
                    destination.mkdir(parents=True, exist_ok=True)
                    plain = destination / f"{manifest['id']}-{manifest['version']}.zip"
                    if app == "nova":
                        run([sys.executable, roots[app] / "scripts/package-addon.py", directory.name,
                             "--source-root", ROOT, "--output-dir", destination,
                             "--validator", validators[app][0]] if args.nova_validator else
                            [sys.executable, roots[app] / "scripts/package-addon.py", directory.name,
                             "--source-root", ROOT, "--output-dir", destination,
                             "--runtime-root", roots[app]])
                    else:
                        run([sys.executable, roots[app] / "tools/package-addon.py", directory, plain])
                    run([*validators[app], plain], stdout=subprocess.DEVNULL)
                    audit_archive(plain, directory, expected, app)
                    archives.append(plain)
                data = archives[0].read_bytes()
                if data != archives[1].read_bytes():
                    raise ValueError(f"non-reproducible archive: {directory}")
                other = "nova-reader" if app == "nova" else "nova"
                require_rejection(validators[other], archives[0])
                if app == "nova-reader" and args.reader_reference_dir:
                    reference = args.reader_reference_dir / archives[0].name
                    if data != reference.read_bytes():
                        raise ValueError(f"existing Reader version changed bytes: {reference}")
                name = f"{app}-{archives[0].name}"
                sha = hashlib.sha256(data).hexdigest()
                (staging / name).write_bytes(data)
                (staging / f"{name}.sha256").write_text(f"{sha}  {name}\n")
                inventory["packages"].append({
                    "app": app, "id": manifest["id"], "name": manifest["name"],
                    "version": manifest["version"], "formatVersion": manifest["formatVersion"],
                    **({"contract": manifest["contract"]} if app == "nova-reader" else {}),
                    "archive": name, "sha256": sha, "bytes": len(data), "files": expected,
                })
        inventory["packages"].sort(key=lambda row: row["archive"])
        (staging / "SHA256SUMS").write_text("".join(
            f"{row['sha256']}  {row['archive']}\n" for row in inventory["packages"]))
        (staging / "inventory.json").write_text(json.dumps(inventory, indent=2) + "\n")
        body = ["Install the ZIP matching your app through its local addon installer.",
                "Nova video packages and Nova Reader source packages are incompatible.", "",
                "| App | Addon | Version | Download |", "| --- | --- | --- | --- |"]
        body.extend(f"| {'Nova Reader' if row['app'] == 'nova-reader' else 'Nova'} | {row['name']} | {row['version']} | `{row['archive']}` |"
                    for row in inventory["packages"])
        body.extend(["", "Verify downloads with `sha256sum -c SHA256SUMS`.",
                     "Each archive is validated by its app's native parser and rejected by the other app's parser.",
                     "Packages are independently versioned; the repository release bundles the current catalog.", ""])
        (staging / "release-notes.md").write_text("\n".join(body))
        # Do not leave stale ZIPs from previous catalog versions in a release.
        if output.exists() and any(output.iterdir()):
            raise ValueError(f"output directory must be empty: {output}")
        output.mkdir(exist_ok=True)
        for path in staging.iterdir():
            if path.is_file():
                shutil.copyfile(path, output / path.name)
    print(f"Packaged {len(inventory['packages'])} verified addons in {output}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nova-root", required=True, type=Path)
    parser.add_argument("--reader-root", required=True, type=Path)
    parser.add_argument("--nova-validator", type=Path)
    parser.add_argument("--reader-validator", type=Path)
    parser.add_argument("--reader-reference-dir", type=Path,
                        help="also require byte equality with already distributed Reader ZIPs")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    package_all(parser.parse_args())


if __name__ == "__main__":
    main()
