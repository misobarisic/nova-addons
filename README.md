# Nova addons

AniKoto and Supernova are independently packaged JavaScript addons for Nova.
Their production source lives under `addons/<id>`. Nova ships the sandbox and
local ZIP installer, and does not embed or download these addons automatically.

Each addon includes `manifest.json`, `stremio-manifest.json`, its explicitly
ordered JavaScript scripts, declared assets, `NOTICE.md` and full `LICENSE`.
Supernova's entry is last in its thirteen-script declaration. AniKoto uses one
entry script. Fixtures are development inputs and never enter packages.

Build from a Nova runtime checkout, using that runtime's parser to verify output:

```sh
python3 /path/to/nova/scripts/package-addon.py --source-root "$PWD" --all --output-dir dist
```

The result is one `<id>-<version>.zip` and adjacent `.zip.sha256` per addon.
Entries are sorted and stored without compression, with fixed timestamps and
permissions. Identical sources yield byte-identical archives. No signing or
network repository is implemented. Nova installs these packages from local files.

Use `--validator /path/to/validate-package` for packaging with a prebuilt Nova
parser, without invoking Cargo or requiring a runtime checkout.

Supernova’s Sort order includes **Number of seeds** (source-reported counts). Move
it up to prioritize seed count, and choose High or Low for its direction. Unknown
counts remain last. The stored criterion key is `seeders`, so existing priorities
and directions survive the display-label update.
