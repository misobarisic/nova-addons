# Reader source provenance

The original three production sources and their synthetic parser fixtures were
copied without modifying package inputs from Nova Reader's `examples/addons/` at
[`59b5000695f7b280ee22a1dd63dc1e76195c5b39`](https://github.com/misobarisic/nova-reader/tree/59b5000695f7b280ee22a1dd63dc1e76195c5b39/examples/addons).
Nova Addons is now the canonical home of all six source packages, their neutral
fixtures, native tests and site documentation. Reader's current tree retains
host code, catalogue compatibility metadata and neutral executable addon fixtures. The immutable historical links above
record the original port provenance, not a current source dependency. Existing
`addons/` video paths are unchanged.

Toonily 1.0.0, Mitaku 1.0.0 and CosplayTele 1.0.0 are native ports introduced in
[Nova Reader 0.1.26](https://github.com/misobarisic/nova-reader/tree/v0.1.26/examples/addons).
Their upstream references are pinned to Keiyoushi
`efa93f5a3537856fe830450bbe33f69d21d28167`. Their notices identify exact Kotlin
sources/dependencies, upstream icons, port differences, neutral fixtures and
metadata-only live checks. Toonily's narrow cookie permission requires the
0.1.26 host API; the compatibility pin selects its production package parser.
The published Manhwa18.cc 1.0.1, MangaFire 1.0.1 and Kagane 1.0.0 package inputs
and hashes remain unchanged.

Kagane 1.0.1 is an addon-only update compatible with published Nova Reader
0.1.26. Its request Origin handling follows Keiyoushi Kagane versionCode 39 at
`efa93f5a3537856fe830450bbe33f69d21d28167`; metadata, integrity, book manifests
and page requests send `Origin: https://kagane.moe`. Retired `kagane.cx` and
`kagane.net` Mirror choices migrate to `kagane.moe` through Reader's existing
settings validation, preserving compatible settings without new permissions.
Its notice records the metadata and HEAD-only verification. Kagane 1.0.0 remains
immutable; changed inputs use the new 1.0.1 package version.

CosplayTele 1.0.1 corrects the native port's missing detail cover while keeping
the same pinned upstream reference, license and icon. Its notice records the
neutral regression and limited live cover checks. The 1.0.0 ZIP stays immutable.
Toonily and Mitaku remain on hold for live-site challenge errors.

Each source's original `NOTICE.md` records the upstream Keiyoushi source paths,
immutable revisions, port modifications and limitations. Full Apache-2.0
`LICENSE` files remain next to the sources and inside each package. Original
notices may describe an earlier planned catalog path; the current Reader source
catalog is `reader-addons/`. No manifest field or package input was added merely
to classify the app. Reader's format 2 plus `nova-reader1` contract already does so.

The release wrapper calls the apps' own packaging tools and native parsers.
The `nova-reader.ref` tag in `compatibility.json` selects the published runtime
recipe/parser (currently Reader 0.1.26). All nine retained Reader ZIP versions
were copied byte-for-byte into `reader-packages/` with their SHA256SUMS inventory;
the packager validates every golden and requires exact equality for each current
Reader source. No Reader reference checkout, reference commit, sibling-source
path or copied validator implementation supplies these goldens. The independent
`reader-tests/` harness pins the published production host directly.

Reader's existing ZIP_DEFLATED recipe and every declared source byte are retained
so already distributed versions keep their original archive hashes. Release
filenames gain `nova-reader-`; that does not change ZIP contents. The original
released hashes also remain hardcoded in the packaging regressions independently
of the inventory. Never change a published archive's bytes without bumping that
addon's manifest version. Package notices containing old Reader paths remain
unchanged as historical attribution; current sources live in `reader-addons/`.
