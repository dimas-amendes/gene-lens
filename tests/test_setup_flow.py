"""
Tests for the first-run browser setup flow: the /setup gate, the download
kickoff endpoint, and the status poller.

The gate is what makes the packaged app "just work" for a non-technical user —
without the core database, land on a setup page instead of an empty dashboard.
A regression that skips the gate ships an app that silently returns empty
reports, so we lock the redirect and the endpoint contracts here.
"""
import pytest

import dashboard
import download_databases


@pytest.fixture
def client():
    dashboard.app.config["TESTING"] = True
    with dashboard.app.test_client() as c:
        yield c


def test_index_redirects_to_setup_when_clinvar_missing(client, monkeypatch):
    monkeypatch.setattr(dashboard, "_clinvar_missing", lambda: True)
    resp = client.get("/")
    assert resp.status_code == 302
    assert "/setup" in resp.headers["Location"]


def test_index_does_not_redirect_when_clinvar_present(client, monkeypatch):
    monkeypatch.setattr(dashboard, "_clinvar_missing", lambda: False)
    resp = client.get("/")
    # Either renders (200) or redirects to consent — but NOT to /setup.
    assert "/setup" not in resp.headers.get("Location", "")


def test_tiny_clinvar_is_treated_as_missing(tmp_path, monkeypatch):
    """A present-but-tiny (corrupt) ClinVar must count as missing, so the app
    offers a re-download instead of trusting a near-empty database."""
    import config
    from src import system_status as ss
    tiny = tmp_path / "clinvar_alleles.tsv"
    tiny.write_bytes(b"broken\n" * 10)  # ~70 bytes, far below the 10 MB floor
    monkeypatch.setattr(ss, "CLINVAR_TSV", tiny)
    monkeypatch.setattr(config, "CLINVAR_TSV", tiny)

    assert ss.clinvar_present() is False
    assert dashboard._clinvar_missing() is True
    status = ss.check_clinvar()
    assert status.installed is False
    assert "corrupt" in status.detail.lower()


def test_reset_all_data_wipes_databases_genetic_files_and_flags(tmp_path, monkeypatch):
    import config
    from src import consent as consent_mod, preferences as prefs_mod

    data, inp, out, hist = (tmp_path / n for n in ("data", "input", "output", "history"))
    for d in (data, inp, out, hist):
        d.mkdir()
    (data / "clinvar_alleles.tsv").write_bytes(b"x" * 2000)
    (inp / "genome.txt").write_bytes(b"rs1\t1\t100\tAA\n")
    (out / "report.md").write_text("report")
    (hist / "h1").mkdir()
    (hist / "h1" / "analysis.json").write_text("{}")
    log = tmp_path / "dashboard.log"; log.write_text("log")
    consent_f = tmp_path / ".consent"; consent_f.write_text("ok")
    prefs_f = tmp_path / ".prefs"; prefs_f.write_text("{}")

    monkeypatch.setattr(dashboard, "INPUT_DIR", inp)
    monkeypatch.setattr(dashboard, "OUTPUT_DIR", out)
    monkeypatch.setattr(dashboard, "HISTORY_DIR", hist)
    monkeypatch.setattr(dashboard, "DATA_DIR", data)
    monkeypatch.setattr(dashboard, "LOG_PATH", log)
    monkeypatch.setattr(config, "DATA_DIR", data)
    monkeypatch.setattr(config, "CACHE_DIR", data / "cache")
    monkeypatch.setattr(config, "INPUT_DIR", inp)
    monkeypatch.setattr(config, "OUTPUT_DIR", out)
    monkeypatch.setattr(consent_mod, "CONSENT_FILE", consent_f)
    monkeypatch.setattr(prefs_mod, "PREFS_FILE", prefs_f)

    dashboard._reset_all_data()

    assert not (inp / "genome.txt").exists()        # genetic data wiped
    assert not (out / "report.md").exists()
    assert list(hist.glob("*")) == []               # history wiped
    assert not (data / "clinvar_alleles.tsv").exists()  # databases wiped
    assert not consent_f.exists() and not prefs_f.exists()  # flags wiped
    assert inp.exists() and out.exists() and data.exists()  # dirs recreated


def test_explain_section_runs_in_background_and_polls(client, monkeypatch):
    import src.local_ai as local_ai
    from src import preferences
    monkeypatch.setattr(preferences, "is_ai_chat_enabled", lambda: True)
    monkeypatch.setattr(local_ai, "chat_about_analysis",
                        lambda **k: (True, "Plain-language explanation."))
    monkeypatch.setattr(dashboard, "_build_chat_context", lambda active, lang: "ctx")
    # Run the background worker inline so the test is deterministic.
    monkeypatch.setattr(dashboard.threading, "Thread",
                        lambda target, args, daemon, name: type(
                            "T", (), {"start": lambda self: target(*args)})())
    dashboard._jobs["active_result"] = {"health": {}}
    try:
        resp = client.post("/api/explain", json={"section": "disease"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True and data["job_id"]
        status = client.get(f"/api/explain/status/{data['job_id']}").get_json()
        assert status["status"] == "done"
        assert status["explanation"] == "Plain-language explanation."
    finally:
        dashboard._jobs.pop("active_result", None)


def test_reset_rejects_missing_token(client):
    # A blind POST (no session token) must not wipe data.
    resp = client.post("/api/reset-data", json={})
    assert resp.status_code == 403
    assert resp.get_json()["error"] == "bad_token"


def test_reset_accepts_valid_session_token(client, monkeypatch):
    called = {}
    monkeypatch.setattr(dashboard, "_reset_all_data", lambda: called.setdefault("wiped", True))
    with client.session_transaction() as sess:
        sess["reset_token"] = "tok-abc"
    resp = client.post("/api/reset-data", json={"token": "tok-abc"})
    assert resp.status_code == 200
    assert resp.get_json()["ok"] is True
    assert called.get("wiped") is True
    # token is single-use: a replay is now rejected
    replay = client.post("/api/reset-data", json={"token": "tok-abc"})
    assert replay.status_code == 403


def test_explain_rejects_unknown_section(client):
    resp = client.post("/api/explain", json={"section": "nonsense"})
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "unknown_section"


def test_explain_stream_emits_sse_chunks(client, monkeypatch):
    import src.local_ai as local_ai
    from src import preferences
    monkeypatch.setattr(preferences, "is_ai_chat_enabled", lambda: True)
    # Stub the generator so the test never touches Ollama.
    monkeypatch.setattr(local_ai, "chat_about_analysis_stream",
                        lambda **k: iter(["Hello ", "world."]))
    dashboard._jobs["active_result"] = {"health": {}}
    try:
        resp = client.post("/api/explain/stream", json={"section": "disease"})
        assert resp.status_code == 200
        body = resp.get_data(as_text=True)
        assert '"event": "chunk"' in body
        assert "Hello " in body and "world." in body
        assert '"event": "done"' in body
    finally:
        dashboard._jobs.pop("active_result", None)


def test_explain_stream_rejects_unknown_section(client):
    resp = client.post("/api/explain/stream", json={"section": "nope"})
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "unknown_section"


def test_build_explain_context_is_section_scoped():
    # Each section's context must contain ONLY that section's findings, so the
    # local model stops bleeding wellness/mental genes into the pharma answer.
    active = {
        "genome_info": {"snp_count": 100, "format": "csv", "profile": {"sex": "F"}},
        "health": {
            "findings": [{"rsid": "rs1801133", "gene": "MTHFR", "category": "methylation",
                          "genotype": "TT", "description": "reduced enzyme"}],
            "pharmgkb_findings": [{"rsid": "rs4149056", "gene": "SLCO1B1", "level": "1A",
                                   "genotype": "CC", "drugs": "simvastatin",
                                   "annotation": "myopathy risk"}],
        },
        "hereditary": {"conditions": [{"name": "Hereditary breast cancer",
                                       "genes_found": ["BRCA1"], "max_stars": 3,
                                       "text": "BRCA1 pathogenic variant"}]},
        "wellness": {"nutri": {"findings": [{"trait": "Vitamin D", "gene": "VDR",
                                             "genotype": "AA", "label": "low",
                                             "text": "vit d panel"}]}},
    }
    pharma = dashboard._build_explain_context(active, "pharma", "en")
    assert "SLCO1B1" in pharma
    assert "VDR" not in pharma      # wellness must not leak into pharma
    assert "BRCA1" not in pharma    # hereditary must not leak either
    assert "MTHFR" not in pharma    # lifestyle findings are a different section

    hered = dashboard._build_explain_context(active, "hereditary", "en")
    assert "BRCA1" in hered and "SLCO1B1" not in hered

    wellness = dashboard._build_explain_context(active, "wellness", "en")
    assert "VDR" in wellness and "SLCO1B1" not in wellness

    # A section with no scoped view falls back to the full analysis context.
    fallback = dashboard._build_explain_context(active, "mystery", "en")
    assert "MTHFR" in fallback


def test_explain_requires_ai_enabled(client, monkeypatch):
    from src import preferences
    monkeypatch.setattr(preferences, "is_ai_chat_enabled", lambda: False)
    resp = client.post("/api/explain", json={"section": "disease"})
    assert resp.status_code == 403


def test_setup_page_renders(client):
    resp = client.get("/setup")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    # Core databases and the offline-after-setup promise must be on the page.
    assert "ClinVar" in body
    assert "PharmGKB" in body


def test_setup_status_returns_contract(client):
    resp = client.get("/api/setup/status")
    assert resp.status_code == 200
    data = resp.get_json()
    assert set(data) >= {"running", "finished", "items"}


def test_setup_download_rejects_empty_selection(client):
    resp = client.post("/api/setup/download", json={"databases": []})
    assert resp.status_code == 200
    assert resp.get_json() == {"ok": False, "error": "nothing_selected"}


def test_check_updates_requires_post(client):
    # GET must not trigger outbound HEADs — that would be firable cross-origin.
    # POST is covered by the global CSRF/Origin guard.
    assert client.get("/api/check-updates").status_code == 405


def test_check_updates_post_returns_status(client, monkeypatch):
    monkeypatch.setattr(
        download_databases, "check_for_updates",
        lambda: {"clinvar": "up-to-date", "pharmgkb": "not-downloaded"},
    )
    resp = client.post("/api/check-updates")
    assert resp.status_code == 200
    assert resp.get_json() == {
        "ok": True,
        "status": {"clinvar": "up-to-date", "pharmgkb": "not-downloaded"},
    }


def test_setup_download_ignores_unknown_databases(client, monkeypatch):
    started = {}
    monkeypatch.setattr(dashboard, "_run_setup_download", lambda sel: started.setdefault("sel", sel))
    # Prevent a real background thread/network: run target inline via patch.
    monkeypatch.setattr(dashboard.threading, "Thread",
                        lambda target, args, daemon, name: type("T", (), {"start": lambda self: target(*args)})())
    resp = client.post("/api/setup/download", json={"databases": ["clinvar", "evil"]})
    assert resp.status_code == 200
    assert resp.get_json()["ok"] is True
    assert started["sel"] == ["clinvar"]  # "evil" filtered out
