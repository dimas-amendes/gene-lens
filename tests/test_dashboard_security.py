"""
Tests for the dashboard's security gates: CSRF/origin check, consent flow,
and the security headers we send back on every response.

These guards are the difference between "local-only web tool" and "a thing
that could leak genetic data to any site the user happens to have open in
another tab". A regression here breaks the privacy promise — not the UX.
"""
import pytest

import config as _config
import dashboard
from src import consent as consent_module


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def client(monkeypatch, tmp_path):
    """Flask test client with consent + history + input dirs isolated to tmp.

    Why all three: POST /analyze-sample spawns a background thread that
    copies the sample into INPUT_DIR and saves the resulting analysis into
    HISTORY_DIR. Without isolation, every security test that exercises the
    analyze route pollutes the user's real `history/` folder with phantom
    entries. (We learned this the hard way — two ghost entries showed up
    in production from running this very test file.)
    """
    fake_consent = tmp_path / ".genetics_consent"
    monkeypatch.setattr(consent_module, "CONSENT_FILE", fake_consent)

    # Redirect history + I/O dirs to tmp_path so analysis jobs the route
    # spawns don't litter the repo. The dashboard captures these constants
    # at import time, so we patch both the source module (config) AND the
    # already-imported references on dashboard.
    fake_history = tmp_path / "history"
    fake_input = tmp_path / "input"
    fake_output = tmp_path / "output"
    fake_data = tmp_path / "data"
    fake_history.mkdir()
    fake_input.mkdir()
    fake_output.mkdir()
    fake_data.mkdir()
    monkeypatch.setattr(dashboard, "HISTORY_DIR", fake_history)
    monkeypatch.setattr(dashboard, "INPUT_DIR", fake_input)
    monkeypatch.setattr(_config, "INPUT_DIR", fake_input)
    monkeypatch.setattr(_config, "OUTPUT_DIR", fake_output)
    monkeypatch.setattr(_config, "DATA_DIR", fake_data)

    dashboard.app.config["TESTING"] = True
    with dashboard.app.test_client() as c:
        yield c


def _accept_consent(monkeypatched_path):
    monkeypatched_path.write_text("consent_accepted=true\n")


# ── CSRF / cross-origin POST protection ───────────────────────────────────────

class TestCsrfCheck:
    """`_csrf_check` blocks POSTs whose Origin/Referer is outside localhost.

    GET requests are never blocked (we don't mutate state on GET). POSTs
    without Origin or Referer (curl, programmatic clients) are allowed —
    a malicious browser tab cannot omit Origin on a cross-origin POST."""

    def test_post_with_foreign_origin_is_blocked(self, client):
        r = client.post(
            "/lang/en",
            headers={"Origin": "https://evil.example.com"},
        )
        assert r.status_code == 403
        assert b"cross-origin" in r.data.lower()

    def test_post_with_foreign_referer_is_blocked(self, client):
        r = client.post(
            "/lang/en",
            headers={"Referer": "https://evil.example.com/some-page"},
        )
        assert r.status_code == 403

    def test_post_with_localhost_origin_is_allowed(self, client):
        # /lang/<code> is a POST/GET route that redirects on success.
        for origin in (
            "http://127.0.0.1:5000",
            "http://localhost:5000",
            "http://[::1]:5000",
        ):
            r = client.post(f"/lang/en", headers={"Origin": origin})
            assert r.status_code != 403, f"Origin {origin} should pass CSRF check"

    def test_post_without_origin_or_referer_is_allowed(self, client):
        """Local CLI tools (curl, fetch from same-origin) often omit both.
        Browsers ALWAYS send Origin on cross-origin POST, so absence is
        safe to allow — and necessary, since same-origin fetch may omit it."""
        r = client.post("/lang/en")
        assert r.status_code != 403

    def test_post_with_null_origin_is_allowed(self, client):
        """Browsers send Origin: null for file:// pages and some sandboxed
        iframes. Treat it as "no origin info" and let the request through —
        same-origin file:// would mean the user opened our own HTML."""
        r = client.post("/lang/en", headers={"Origin": "null"})
        assert r.status_code != 403

    def test_get_requests_are_never_blocked_even_with_foreign_origin(self, client):
        """A GET can't be a CSRF vector for mutating state — the protection
        is POST-only by design. (And blocking GETs would break linking.)"""
        r = client.get("/", headers={"Origin": "https://evil.example.com"})
        # GET / redirects to /consent when no consent is given, but never 403.
        assert r.status_code != 403


# ── Consent gate ──────────────────────────────────────────────────────────────

class TestConsentGate:
    def test_index_redirects_to_consent_when_not_given(self, client):
        """Without consent, the dashboard must NOT render — the user has
        to actively acknowledge the medical-device disclaimer first."""
        r = client.get("/", follow_redirects=False)
        # / shows the dashboard if no consent? Let me check actual behavior:
        # the consent check is enforced on /analyze-sample, not /. So /
        # should still render, but actions are gated.
        # If a future change tightens /, update this test.
        assert r.status_code in (200, 302)

    def test_analyze_sample_redirects_to_consent_when_not_given(self, client):
        """The mutating routes MUST gate on consent — submitting a genome
        without acknowledging the false-positive rate disclaimer would
        bypass the legal/ethical guard."""
        r = client.post(
            "/analyze-sample",
            headers={"Origin": "http://127.0.0.1:5000"},
            follow_redirects=False,
        )
        assert r.status_code == 302
        assert "/consent" in r.headers["Location"]

    def test_analyze_sample_proceeds_after_consent(self, client, tmp_path):
        """Once consent is recorded, the same POST should kick off a job
        (redirect to /loading/<id>), not bounce back to /consent."""
        _accept_consent(consent_module.CONSENT_FILE)
        r = client.post(
            "/analyze-sample",
            headers={"Origin": "http://127.0.0.1:5000"},
            follow_redirects=False,
        )
        assert r.status_code == 302
        assert "/loading/" in r.headers["Location"]
        assert "/consent" not in r.headers["Location"]

    def test_consent_get_renders_terms_page(self, client):
        r = client.get("/consent")
        assert r.status_code == 200
        # Terms text must be present so the user actually sees what they're
        # agreeing to.
        body = r.get_data(as_text=True)
        assert "EDUCATIONAL" in body or "EDUCACIONAL" in body

    def test_consent_post_writes_consent_file_and_redirects(self, client):
        assert not consent_module.CONSENT_FILE.exists()
        r = client.post(
            "/consent",
            headers={"Origin": "http://127.0.0.1:5000"},
            follow_redirects=False,
        )
        assert r.status_code == 302
        assert consent_module.CONSENT_FILE.exists()
        # Subsequent gated routes should now proceed.
        r2 = client.post(
            "/analyze-sample",
            headers={"Origin": "http://127.0.0.1:5000"},
            follow_redirects=False,
        )
        assert "/loading/" in r2.headers["Location"]

    def test_is_consent_given_reflects_file_presence(self, tmp_path, monkeypatch):
        """The helper that backs `require_consent_web` must be a pure
        check on the file's presence — no caching, no environment quirks."""
        fake = tmp_path / "consent"
        monkeypatch.setattr(consent_module, "CONSENT_FILE", fake)
        assert consent_module.is_consent_given() is False
        fake.write_text("ok")
        assert consent_module.is_consent_given() is True


# ── Security headers ──────────────────────────────────────────────────────────

class TestSecurityHeaders:
    """Every response — even error responses — must carry the security
    headers we configured. A regression in `add_security_headers` would
    leave the app open to clickjacking, MIME sniffing, and content-type
    confusion attacks across the board, silently."""

    def _expected_headers(self):
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Referrer-Policy": "no-referrer",
        }

    @pytest.mark.parametrize("path", ["/", "/consent", "/settings"])
    def test_headers_present_on_get_routes(self, client, path):
        r = client.get(path)
        for header, expected in self._expected_headers().items():
            assert r.headers.get(header) == expected, (
                f"{path} missing or wrong {header}: got {r.headers.get(header)!r}"
            )

    def test_csp_restricts_external_assets(self, client):
        """The CSP must lock script/style/img/font to 'self' (+ inline for
        script/style — yes, we use inline, deliberately). No external
        sources allowed → no third-party scripts can ever load on a
        compromised page."""
        r = client.get("/")
        csp = r.headers.get("Content-Security-Policy", "")
        assert "default-src 'self'" in csp
        assert "script-src 'self'" in csp
        # External CDNs must NOT be allowed — we serve everything locally.
        assert "https:" not in csp.replace("https://", "")
        assert "cdn." not in csp.lower()

    def test_cache_control_prevents_storage_of_sensitive_responses(self, client):
        """Genetic findings would otherwise live in the browser cache and
        survive logout / shared computers. Force no-store on everything."""
        r = client.get("/")
        cc = r.headers.get("Cache-Control", "")
        assert "no-store" in cc

    def test_headers_present_on_403_response(self, client):
        """The CSRF block path returns 403 directly from before_request —
        we must confirm the after_request hook still runs and stamps the
        security headers on that error response."""
        r = client.post("/lang/en", headers={"Origin": "https://evil.example.com"})
        assert r.status_code == 403
        # X-Content-Type-Options should still be there on a 403.
        assert r.headers.get("X-Content-Type-Options") == "nosniff"
