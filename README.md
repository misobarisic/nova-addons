# Nova and Nova Reader addons

Independent JavaScript addon catalogs for two apps. Download the ZIP whose
filename starts with your app's prefix and import it through that app's local
addon installer. Neither app installs these sources automatically.

| App | Source directories | Release ZIP prefix | Native manifest |
| --- | --- | --- | --- |
| Nova (video) | `addons/<id>/` | `nova-` | `formatVersion: 1` |
| Nova Reader (chapters/pages) | `reader-addons/<id>/` | `nova-reader-` | `formatVersion: 2`, `contract: nova-reader1` |

The existing `addons/` paths and URLs remain unchanged. Classification lives in
directory/release names and the existing native manifest contracts; no extra
manifest fields are needed. Both production parsers reject the other app's
packages. Installing a source still requires the app's permission review.

## Nova: video addons

AniKoto, Re:ANIME and Supernova retain their production sources under `addons/`.
Each includes its manifest, Stremio manifest, explicitly ordered JavaScript,
declared assets, `NOTICE.md` and full `LICENSE`. Supernova's entry is last in its
thirteen-script declaration. AniKoto uses one entry script.

Supernova’s Sort order includes **Number of seeds** (source-reported counts). Move
it up to prioritize seed count, and choose High or Low for its direction. Unknown
counts remain last. The stored criterion key is `seeders`, so existing priorities
and directions survive the display-label update.

Re:ANIME ports Yuzono’s ReAnime source and requires Nova with FlixCloud relay
support (`permissions.flixcloudPlayback`). It includes popular/latest/search
catalogs, metadata, stable episode identities, sub/dub streams and the usual
Streams/Metadata switches. Playback uses the upstream `enc-dec.app` decoding
service. Direct MKV preparation, fonts and chapter markers are not included.
Run source tests with `node --test addons/reanime/fixtures/provider.test.cjs`.

Re:ANIME 0.1.1 updates the initially distributed 0.1.0 package so installed
addons receive the required `rundowncdn.top` CDN permission. Import the newer ZIP;
Nova intentionally rejects changed archives that reuse an installed version.

## Nova Reader: chapter and page sources

Manhwa18.cc (`manhwa18cc` 1.0.1), MangaFire (`mangafire` 1.0.1) and Kagane
(`kagane` 1.0.0) live under `reader-addons/`. They use Reader source identities,
chapter/page operations and Reader's sandbox permissions. They provide no Nova
video streams. These mixed/adult catalogs retain their NSFW declarations and
source settings; see each original notice for upstream revisions and limitations.

Sources and declared icons/scripts/notices/licenses are copied without changes
from Reader's reference packages. Reader retains its examples and fixtures.
Synthetic tests are retained for development and never enter release packages.
MangaFire fixtures run with `node --test reader-addons/mangafire/tests/parser.test.mjs`;
Manhwa18.cc fixtures use their pinned development-only dependency: run
`npm ci --prefix reader-addons/manhwa18cc/tests`, then
`node --test reader-addons/manhwa18cc/tests/parser.test.mjs`.
Release packaging does not install Node dependencies or run live-source probes.
See [Reader provenance](reader-addons/PROVENANCE.md). Individual addon licenses
and notices apply to their code/assets; the repository license does not replace
them. Already distributed addon versions retain identical archive bytes and
hashes, even though catalog release filenames gain an app prefix.

## Package the complete catalog

The wrapper calls the apps' actual packaging tools and production native parsers;
it carries no second implementation of their manifest validators. Supported
runtime release tags are recorded in [compatibility.json](compatibility.json).
Check out those runtime versions before packaging:

```sh
python3 scripts/package-all.py --nova-root /path/to/nova --reader-root /path/to/nova-reader --reader-reference-dir /path/to/nova-reader/addons --output-dir dist
```

Use an empty output directory. Cargo builds/runs only the parser examples in the
`nova-providers` and `reader-sources` leaf crates. To use already built parsers:

```sh
cargo build --locked --manifest-path /path/to/nova/crates/providers/Cargo.toml --example validate-package
cargo build --locked --manifest-path /path/to/nova-reader/crates/reader-sources/Cargo.toml --example validate-package
python3 scripts/package-all.py --nova-root /path/to/nova --reader-root /path/to/nova-reader --nova-validator /path/to/nova/target/debug/examples/validate-package --reader-validator /path/to/nova-reader/target/debug/examples/validate-package --reader-reference-dir /path/to/nova-reader/addons --output-dir dist
```

The result is six app-prefixed ZIPs, adjacent `.zip.sha256` files, `SHA256SUMS`,
`inventory.json` and a release-notes body. For example,
`nova-reader-mangafire-1.0.1.zip` belongs in Nova Reader. Verify downloads with
`sha256sum -c SHA256SUMS` from the release download directory.

Nova keeps its sorted ZIP_STORED recipe; Reader keeps its sorted ZIP_DEFLATED
recipe. Both fix timestamps and permissions and include only declared package
inputs. The wrapper packages twice, requires byte equality, checks exact members
and source bytes, rejects development/private/symlink inputs, and runs every ZIP
through both parsers: matching app accepts, other app rejects. The optional
reference directory additionally guarantees Reader ZIP identity with previously
distributed versions; release automation requires that check. Fixtures, tests,
credentials and this repository's release metadata never enter addon archives.
No package validation installs an addon or performs source network requests.

Nova's original standalone tool remains available for its existing directory
layout: `python3 /path/to/nova/scripts/package-addon.py --source-root "$PWD" --all --output-dir dist`.
Its unprefixed outputs remain supported by Nova's installer; the combined release
wrapper supplies app prefixes to make downloads easier to distinguish.

## Tagged releases

[Release addons](.github/workflows/release-addons.yml) runs only on `v*` tag
pushes. It checks out the published runtime tags in `compatibility.json`, builds
the two leaf parsers, packages all current addons and publishes a GitHub Release
with ZIPs, checksums and inventory. It does not run a PR or workspace test/check
pipeline on tags. Native package validation and reproducibility are part of
creating the release artifacts. Only the publish job receives `contents: write`.

Publish the referenced app runtime releases before tagging this repository.
A catalog release bundles independently versioned addons; it does not rewrite
their manifest versions. Any change to a published archive's inputs requires
that addon's version bump. Releases are unsigned local-install archives, with
no automatic update repository or installation mechanism.
