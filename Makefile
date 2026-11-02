.PHONY: check check-reader check-reader-parsers check-reader-native check-packaging

check: check-reader check-packaging

check-reader: check-reader-parsers check-reader-native

check-reader-parsers:
	npm ci --ignore-scripts --prefix reader-addons/manhwa18cc/tests
	npm test --prefix reader-addons/manhwa18cc/tests
	node reader-addons/mangafire/tests/parser.test.mjs
	node reader-addons/kagane/tests/request.test.mjs
	npm ci --ignore-scripts --prefix reader-addons/toonily/tests
	npm test --prefix reader-addons/toonily/tests
	npm ci --ignore-scripts --prefix reader-addons/mitaku/tests
	npm test --prefix reader-addons/mitaku/tests
	npm ci --ignore-scripts --prefix reader-addons/cosplaytele/tests
	npm test --prefix reader-addons/cosplaytele/tests

check-reader-native:
	cargo fmt --manifest-path reader-tests/Cargo.toml -- --check
	cargo clippy --locked --manifest-path reader-tests/Cargo.toml --all-targets -- -D warnings
	cargo test --locked --manifest-path reader-tests/Cargo.toml

check-packaging:
	python3 -B -m unittest discover -s scripts -p 'test_*.py'
