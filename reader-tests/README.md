# Native Reader addon tests

These integration tests install the canonical packages from `../reader-addons`
and execute their fixtures through the production `SourceRegistry`, QuickJS,
HTML and network host APIs. The runtime dependency is pinned to the immutable
commit for published Reader v0.1.26; a Reader checkout is not required.

```sh
cargo test --locked --manifest-path reader-tests/Cargo.toml
cargo clippy --locked --manifest-path reader-tests/Cargo.toml --all-targets -- -D warnings
cargo build --locked --manifest-path reader-tests/Cargo.toml --example validate-package
```

Run these commands from the repository root. Normal tests use neutral synthetic
records and images. Manual live metadata/cover smoke tests remain ignored unless
explicitly selected with `--ignored`; website availability is external. The
Kagane upgrade regression builds an authored legacy-behavior fixture in memory;
no historical addon ZIP is required.
The `validate-package` example is copied unchanged from that published runtime
and builds against the same pinned dependency for package/release validation.

Reader's own generic host, permission, session, cache and neutral-package tests
stay in the Reader repository and do not depend on this harness or these addons.
