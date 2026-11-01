# Reader source provenance

The three production sources and their synthetic parser fixtures were copied
without modifying package inputs from Nova Reader's `examples/addons/` at
[`59b5000695f7b280ee22a1dd63dc1e76195c5b39`](https://github.com/misobarisic/nova-reader/tree/59b5000695f7b280ee22a1dd63dc1e76195c5b39/examples/addons).
This catalog is their independently published home; Reader retains its reference
copies and fixtures. Existing `addons/` video paths are unchanged.

Each source's original `NOTICE.md` records the upstream Keiyoushi source paths,
immutable revisions, port modifications and limitations. Full Apache-2.0
`LICENSE` files remain next to the sources and inside each package. Original
notices may describe an earlier planned catalog path; the current Reader source
catalog is `reader-addons/`. No manifest field or package input was added merely
to classify the app. Reader's format 2 plus `nova-reader1` contract already does so.

The release wrapper calls the apps' own packaging tools and native parsers.
Reader's existing ZIP_DEFLATED recipe and every declared source byte are retained
so already distributed versions keep their original archive hashes. Repository
filenames gain `nova-reader-`; that does not change ZIP contents. Never change a
published archive's bytes without bumping that addon's manifest version.
