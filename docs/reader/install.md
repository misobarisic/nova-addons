# Install Nova Reader sources

Download the `nova-reader-…zip` matching the desired source from a Nova Addons
[GitHub Release](https://github.com/misobarisic/nova-addons/releases), then import it through
**Browse → Extensions → Install addon** in Nova Reader. These sources are mixed
or adult catalogs: enable **Show adult sources** to list them. MangaFire and
Kagane default to Safe content in their source settings.

| Source | Version | Minimum Reader | Canonical source |
| --- | --- | --- | --- |
| Manhwa18.cc | 1.0.1 | 0.1.17 | [Source](../../reader-addons/manhwa18cc/) |
| MangaFire | 1.0.1 | 0.1.17 | [Source](../../reader-addons/mangafire/) |
| Kagane | 1.0.1 | 0.1.17 | [Source](../../reader-addons/kagane/) |
| Toonily (English) | 1.0.0 | 0.1.26 | [Source](../../reader-addons/toonily/) |
| Mitaku | 1.0.0 | 0.1.26 | [Source](../../reader-addons/mitaku/) |
| CosplayTele | 1.0.1 | 0.1.26 | [Source](../../reader-addons/cosplaytele/) |

Each new repository tag packages all addons and publishes their ZIPs in a
GitHub Release. Download the asset for Nova Reader; generated archives and
checksums are not committed to the source tree.
Reimport a newer version to update an installation. Enabled state survives an
update unless its permissions expand; expanded permissions require explicit
re-enabling on each device. Sources are executable code, so review their grants.

**Toonily and Mitaku are on hold** because of live-site challenge errors. Their
existing packages remain available without challenge-handling changes.
Toonily's Show mature content setting defaults off and sets only the explicitly
granted `toonily-mature` cookie on `https://toonily.com` through Reader's isolated
host jar. Cookies remain in memory and outside sync and backups.

Mitaku and CosplayTele expose each image gallery as one chapter; video-only
posts return an explicit error. CosplayTele 1.0.1 retains a gallery poster during
details refresh. The reported initial Browse poster failure was not reproduced
on the test network; current Popular, Latest and details covers passed limited
proxy-backed native decode/publication checks. Challenges, changed markup and
unverified image hosts can still prevent live use.

Kagane has eighteen language variants. Version 1.0.1 adds its required Origin
header and migrates retired mirror settings to `kagane.moe` without resetting
other compatible settings. Older published packages remain in their GitHub Releases.

Every source includes its pinned upstream notices, Apache-2.0 license and
attributed icon. See [provenance](../../reader-addons/PROVENANCE.md),
[Manhwa18.cc behavior](manhwa18.md), [MangaFire behavior](mangafire.md) and the
[canonical native test harness](../../reader-tests/README.md). Neutral fixtures
and tests stay outside install ZIPs. No app automatically installs these addons.
