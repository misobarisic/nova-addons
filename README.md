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

Manhwa18.cc (`manhwa18cc` 1.0.1), MangaFire (`mangafire` 1.0.1), Kagane
(`kagane` 1.0.1), Toonily (`toonily` 1.0.0), Mitaku (`mitaku` 1.0.0) and
CosplayTele (`cosplaytele` 1.0.1) live under `reader-addons/`. They use Reader source identities,
chapter/page operations and Reader's sandbox permissions. They provide no Nova
video streams. These mixed/adult catalogs retain their NSFW declarations and
source settings; see each original notice for upstream revisions and limitations.

Kagane 1.0.1 sends `Origin: https://kagane.moe` on metadata, integrity,
book-manifest and page requests. Its Mirror setting now offers only
`kagane.moe`; Reader migrates saved `kagane.cx`/`kagane.net` selections to that
default while retaining compatible settings. No permission expansion or settings
reset is needed. It works with published Reader 0.1.26; the original Kagane 1.0.0
archive remains unchanged.

**Toonily and Mitaku are on hold** because of live-site challenge errors. Existing
packages remain available without challenge-handling changes.

CosplayTele 1.0.1 fixes details clearing a saved catalogue poster: details now
selects the first gallery image, excluding unrelated sidebar images. Initial
untouched Browse poster failures were not reproduced; current URLs responded
successfully in proxy-backed native decode/publication tests for Popular,
Latest and details. The ordinary native live smoke hit a DNS deadline.

Toonily is English and requires **Nova Reader 0.1.26 or newer**. Its **Show mature
content** setting defaults off and uses a host-managed cookie grant limited to
`toonily-mature` on `https://toonily.com`. Cookies remain source/profile scoped,
in memory, and outside sync and backups. Mitaku and CosplayTele expose each image
gallery as one chapter; video-only posts return an explicit unsupported error.
Their reference is Keiyoushi revision `efa93f5a3537856fe830450bbe33f69d21d28167`.
All three include neutral parser fixtures, Apache-2.0 licenses and attributed
upstream icons. Initial port checks used metadata only; CosplayTele 1.0.1 also
decoded transient cover candidates in isolated native tests. No live images are
bundled as fixtures. Challenges/site changes can still prevent live use. Unknown image hosts fail
until verified and permissioned.

This repository is the sole home of these source packages, their fixtures,
site documentation and immutable ZIP goldens. Reader contains only generic host
code, catalogue compatibility metadata and neutral executable addon fixtures. See [Reader installation](docs/reader/install.md) and
[site documentation](docs/reader/) for source-specific behavior.
Synthetic tests are retained for development and never enter release packages.
MangaFire fixtures run with `node --test reader-addons/mangafire/tests/parser.test.mjs`;
Manhwa18.cc fixtures use their pinned development-only dependency: run
`npm ci --ignore-scripts --prefix reader-addons/manhwa18cc/tests`, then
`node --test reader-addons/manhwa18cc/tests/parser.test.mjs`.
For Toonily, Mitaku and CosplayTele, run
`npm ci --ignore-scripts --prefix reader-addons/<id>/tests`, then
`npm test --prefix reader-addons/<id>/tests`.
Native QuickJS regressions live in [reader-tests](reader-tests/README.md), pinned
to published Reader 0.1.26 without a sibling Reader checkout. Run
`cargo test --locked --manifest-path reader-tests/Cargo.toml`.
Release packaging does not install Node dependencies or run live-source probes.
See [Reader provenance](reader-addons/PROVENANCE.md). Individual addon licenses
and notices apply to their code/assets; the repository license does not replace
them. Already distributed addon versions retain identical archive bytes and
hashes, even though catalog release filenames gain an app prefix.

## Verify changes

Run `make check` from this repository root. It runs the six Reader Node parser
suites, the independent native harness's formatting/Clippy/integration checks,
and Python packaging/golden regressions. The harness pins published Reader
0.1.26 at `5c8cfb3d5d55c1a6552b3ce9910560200bee605b`; it never imports a sibling
Reader working tree. PRs and main pushes run these checks; tag pushes retain the
separate packaging/publishing workflow described below.

## Package the complete catalog

The wrapper calls the apps' actual packaging tools and production native parsers;
it carries no second implementation of their manifest validators. Supported
runtime release tags are recorded in [compatibility.json](compatibility.json).
The Reader `ref` selects the published runtime's packaging recipe and native
parser. Golden archives live locally in [reader-packages](reader-packages/),
with a checked SHA256SUMS inventory covering current and historical versions.
No separate Reader reference checkout or reference commit is needed. Check out
the published runtime tags before packaging:

```sh
python3 scripts/package-all.py --nova-root /path/to/nova --reader-root /path/to/nova-reader --output-dir dist
```

Use an empty output directory. Cargo builds/runs only the parser examples in the
`nova-providers` and `reader-sources` leaf crates. To use already built parsers:

```sh
cargo build --locked --manifest-path /path/to/nova/crates/providers/Cargo.toml --example validate-package
cargo build --locked --manifest-path /path/to/nova-reader/crates/reader-sources/Cargo.toml --example validate-package
python3 scripts/package-all.py --nova-root /path/to/nova --reader-root /path/to/nova-reader --nova-validator /path/to/nova/target/debug/examples/validate-package --reader-validator /path/to/nova-reader/target/debug/examples/validate-package --output-dir dist
```

The result is nine app-prefixed ZIPs, adjacent `.zip.sha256` files, `SHA256SUMS`,
`inventory.json` and a release-notes body. For example,
`nova-reader-mangafire-1.0.1.zip` belongs in Nova Reader. Verify downloads with
`sha256sum -c SHA256SUMS` from the release download directory.

Nova keeps its sorted ZIP_STORED recipe; Reader keeps its sorted ZIP_DEFLATED
recipe. Both fix timestamps and permissions and include only declared package
inputs. The wrapper packages twice, requires byte equality, checks exact members
and source bytes, rejects development/private/symlink inputs, and runs every ZIP
through both parsers: matching app accepts, other app rejects. Every current
Reader package must match its repository-local golden byte-for-byte. All retained
golden versions also pass their SHA256SUMS inventory and both parser boundaries;
these checks are mandatory locally and in release automation. Fixtures, tests,
credentials and this repository's release metadata never enter addon archives.
No package validation installs an addon or performs source network requests.

Nova's original standalone tool remains available for its existing directory
layout: `python3 /path/to/nova/scripts/package-addon.py --source-root "$PWD" --all --output-dir dist`.
Its unprefixed outputs remain supported by Nova's installer; the combined release
wrapper supplies app prefixes to make downloads easier to distinguish.

## Tagged releases

[Release addons](.github/workflows/release-addons.yml) runs only on `v*` tag
pushes. It checks out the published runtime tags in `compatibility.json`, builds
the two leaf parsers, and compares Reader outputs against this repository's
`reader-packages/` archives. Packaging uses only the runtime checkout's recipe
and parser; canonical addon inputs and historical goldens come from Nova Addons.
It packages all current addons and publishes a GitHub Release
with ZIPs, checksums and inventory. It does not run a PR or workspace test/check
pipeline on tags. Native package validation and reproducibility are part of
creating the release artifacts. Only the publish job receives `contents: write`.

Publish the referenced app runtime releases before tagging this repository.
Commit each new Reader version's golden and SHA256SUMS entry alongside its
canonical source update. Validate packaging and runtime-ref handling with
`python3 -B -m unittest discover -s scripts -p 'test_*.py'`.
A catalog release bundles independently versioned addons; it does not rewrite
their manifest versions. Any change to a published archive's inputs requires
that addon's version bump. Releases are unsigned local-install archives, with
no automatic update repository or installation mechanism.
