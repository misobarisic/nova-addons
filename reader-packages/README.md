# Immutable Nova Reader package archives

These original, unprefixed ZIPs are the byte-for-byte goldens for every Reader
addon version retained by this repository. `SHA256SUMS` records their hashes.
Current source lives in [`../reader-addons`](../reader-addons/); historical
archives remain here after a source update. Do not rebuild or replace a released
version's bytes. Add a new version and golden when its declared inputs change.

The release wrapper always checks this local inventory and requires each current
Reader package to match its golden exactly. Runtime recipes and native validation
still come from the published app tags in `../compatibility.json`; no Reader
source/golden checkout is required. The current combined release contains six
Reader packages and three Nova video packages, not all historical goldens.

For installation, use the app-prefixed ZIPs and checksums from a tagged Nova
Addons release as described in the [repository README](../README.md). These
unprefixed goldens also retain their original native package contents.
