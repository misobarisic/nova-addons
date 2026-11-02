# Manhwa18.cc native source

The independently installable package is in `reader-addons/manhwa18cc`.
It is marked NSFW. Select `sourceId` explicitly as `manhwa18cc.en`,
`manhwa18cc.ko` or `manhwa18cc.all`; English is the API fallback. The application enables a newly selected ZIP explicitly; raw registry installation
starts disabled. Permission-expanding updates require re-enabling in Browse. No adult images or scraped live
HTML are bundled. Generic neutral fixtures remain with the Reader host.

From the repository root:

```sh
python3 /path/to/published-reader/tools/package-addon.py reader-addons/manhwa18cc /tmp/manhwa18cc.zip
cd reader-addons/manhwa18cc/tests
npm ci --ignore-scripts
npm test
```

Package syntax is defined by the host tooling. The package declares format 2,
`nova-reader1`, API `^1.0`, and an independent semantic version. It is a source
package for Nova Reader, not an executable Keiyoushi APK/JAR file. Its canonical
location is `reader-addons/manhwa18cc` in Nova Addons. Tagged catalog releases
provide manually installable ZIPs; no signing or automatic update installation
is claimed here.

`yiimadara.js` contains the reusable parser and request policy; `main.js` only
sets the Manhwa18 routes. Popular uses `/webtoons/<page>?orderby=trending`, latest
uses `/webtoons/<page>`, and Korean uses `/raw/<page>`. Text search uses
`/search?q=…&page=…`, replaces ASCII apostrophes with typographic apostrophes,
and ignores filters. Without text search genre takes precedence over category.
The newest-series sort is separate from latest updates. Pagination comes from
the next link before filtering. English hides raw entries; Korean includes only
raw entries outside the raw directory; all includes both, matching upstream.

Series identities are `/webtoon/<slug>`. Chapters retain source order and full
source-local paths, including specials and fractional chapter numbers. Dates
accept English `dd MMM yyyy` and `dd MMM yy` and become ISO date strings. Pages
retain document order, prefer `data-src`, resolve relative to the final response
URL, and carry chapter Referer and source Origin headers. The host owns image
bytes and the source/profile session. Cross-host image domains require a reviewed
manifest permission update; this package currently permits `manhwa18.cc` only.

The parser maps 403/challenge markup to `ChallengeRequired`, 429 to `RateLimited`,
401 to `AuthenticationRequired`, and 404 to `NotFound`. Missing expected markup
becomes `ParseChanged`; only explicit empty-result markup or a present empty
chapter container is treated as empty. Interactive browser challenge resolution
and persistent session transfer are not implemented by this package. Cancellation
and request limits belong to the actual QuickJS host.

Deterministic fixtures cover languages, routes, apostrophes, filter precedence,
pagination after filtering, optional metadata, badges, dates, chapter order,
relative/lazy image URLs, headers, errors and markup changes. The Node shim uses
pinned linkedom; actual QuickJS host integration lives in `reader-tests/tests/manhwa18cc.rs`,
using the published Reader host dependency.
No live-site smoke test has been run and live-site support is unverified.
A manual live probe, when chosen, should inspect safe metadata/status only and
remain separate from CI.

Exact upstream commit, paths, modifications, omissions and Apache-2.0 license
are retained in the package NOTICE.md and LICENSE. Native source version 1.0.1
is independent of upstream versionCode 65. Upstream catalogue IDs are not guessed
or mapped by this reference package.
