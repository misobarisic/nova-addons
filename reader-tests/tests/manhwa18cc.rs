//! Manhwa18 parser fixtures executed through the pinned production QuickJS host.
use reader_sources::{
    CancelToken, HttpRequest, HttpResponse, Result, SourceError, SourceRegistry, SourceTransport,
};
use serde_json::{Value, json};
use std::{
    collections::BTreeMap,
    io::{Cursor, Write},
    sync::{Arc, Mutex},
};
use zip::write::SimpleFileOptions;
fn archive(files: Vec<(String, Vec<u8>)>) -> Vec<u8> {
    let mut zip = zip::ZipWriter::new(Cursor::new(Vec::new()));
    for (name, data) in files {
        zip.start_file(
            name,
            SimpleFileOptions::default().compression_method(zip::CompressionMethod::Deflated),
        )
        .unwrap();
        zip.write_all(&data).unwrap();
    }
    zip.finish().unwrap().into_inner()
}
fn load(root: &std::path::Path, name: &str) -> Vec<u8> {
    let dir = root.join("../reader-addons").join(name);
    let m: Value =
        serde_json::from_slice(&std::fs::read(dir.join("manifest.json")).unwrap()).unwrap();
    let mut names = vec![
        "manifest.json".to_string(),
        m["entry"].as_str().unwrap().into(),
    ];
    for key in ["scripts", "assets"] {
        for value in m[key].as_array().unwrap() {
            names.push(value.as_str().unwrap().into())
        }
    }
    archive(
        names
            .into_iter()
            .map(|n| {
                let bytes = std::fs::read(dir.join(&n)).unwrap();
                (n, bytes)
            })
            .collect(),
    )
}
struct FixtureTransport {
    body: String,
    status: u16,
    seen: Mutex<Vec<HttpRequest>>,
}
impl SourceTransport for FixtureTransport {
    fn request(&self, r: &HttpRequest, _: usize, cancel: &CancelToken) -> Result<HttpResponse> {
        cancel.check()?;
        self.seen.lock().unwrap().push(r.clone());
        Ok(HttpResponse {
            status: self.status,
            url: r.url.clone(),
            body: self.body.as_bytes().to_vec(),
            headers: BTreeMap::new(),
        })
    }
}
#[test]
fn manhwa_parser_executes_through_quickjs_with_sanitized_html() {
    let dir = tempfile::tempdir().unwrap();
    let registry = SourceRegistry::open(dir.path()).unwrap();
    let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR"));
    registry.install_zip(&load(root, "manhwa18cc")).unwrap();
    registry.set_enabled("manhwa18cc", true).unwrap();
    for (op, file, request) in [
        (
            "browse",
            "list",
            json!({"sourceId":"manhwa18cc.en","page":1}),
        ),
        ("details", "details", json!({"id":"/webtoon/clockwork"})),
        ("chapters", "details", json!({"id":"/webtoon/clockwork"})),
        (
            "pages",
            "pages",
            json!({"id":"/webtoon/clockwork/chapter-2.5"}),
        ),
    ] {
        let fixture = std::fs::read_to_string(root.join(format!(
            "../reader-addons/manhwa18cc/tests/fixtures/{file}.html"
        )))
        .unwrap();
        let transport = Arc::new(FixtureTransport {
            body: fixture,
            status: 200,
            seen: Mutex::new(vec![]),
        });
        let source = registry
            .source("manhwa18cc")
            .unwrap()
            .with_transport(transport);
        let value = source.call(op, &request).unwrap();
        match op {
            "browse" => assert!(!value["items"].as_array().unwrap().is_empty()),
            "details" => assert_eq!(value["title"], "Clockwork"),
            "chapters" => {
                assert_eq!(value["chapters"][0]["number"], "2.5");
                assert_eq!(value["chapters"][1]["number"], Value::Null);
            }
            "pages" => assert_eq!(value["pages"].as_array().unwrap().len(), 3),
            _ => unreachable!(),
        }
    }
    for (status, code) in [
        (401, "authentication"),
        (403, "challenge"),
        (429, "rate limited"),
    ] {
        let source = registry
            .source("manhwa18cc")
            .unwrap()
            .with_transport(Arc::new(FixtureTransport {
                body: "".into(),
                status,
                seen: Mutex::new(vec![]),
            }));
        assert!(
            source
                .call("browse", &json!({}))
                .unwrap_err()
                .to_string()
                .contains(code)
        );
    }
    let source = registry
        .source("manhwa18cc")
        .unwrap()
        .with_transport(Arc::new(FixtureTransport {
            body: "<div>changed</div>".into(),
            status: 200,
            seen: Mutex::new(vec![]),
        }));
    assert!(matches!(
        source.call("browse", &json!({})),
        Err(SourceError::ParseChanged(_))
    ));
}
