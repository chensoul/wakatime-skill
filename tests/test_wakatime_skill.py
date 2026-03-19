"""Tests for wakatime-skill/scripts/wakatime_query.py (standalone)."""

from __future__ import annotations

import importlib.util
import io
import json
import os
import sys
import unittest
import urllib.error
from http.client import HTTPMessage
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


def _load_wakatime():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "wakatime_query.py"
    spec = importlib.util.spec_from_file_location("wakatime_query", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["wakatime_query"] = mod
    spec.loader.exec_module(mod)
    return mod


wt = _load_wakatime()
wt._RUNTIME["prog"] = "wakatime_query"


class _FakeUrlopenResp:
    """Minimal context manager for urllib.request.urlopen mocks."""

    def __init__(self, body: bytes, *, code: int = 200) -> None:
        self._body = body
        self._code = code

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self):
        return self._body

    def getcode(self):
        return self._code


class TestWakatimeApiRoot(unittest.TestCase):
    def tearDown(self) -> None:
        wt._RUNTIME["debug"] = False

    def test_api_root_fixed_origin(self) -> None:
        self.assertEqual(wt._api_root(), "https://wakatime.com/api/v1")

    def test_statusbar_url_fixed_origin(self) -> None:
        self.assertEqual(
            wt._statusbar_today_url(),
            "https://wakatime.com/api/v1/users/current/statusbar/today",
        )


class TestWakatimeMainProjects(unittest.TestCase):
    def tearDown(self) -> None:
        wt._RUNTIME["debug"] = False

    def test_projects_hits_v1_path(self) -> None:
        captured: dict[str, str] = {}

        def cap(req, timeout=None, **_):
            captured["url"] = req.full_url
            return _FakeUrlopenResp(b'{"data":[]}')

        env = {"WAKATIME_API_KEY": "k"}
        out = io.StringIO()
        with patch.dict(os.environ, env, clear=False):
            with patch.object(wt.urllib.request, "urlopen", side_effect=cap):
                with patch.object(sys, "argv", ["wakatime_query.py", "projects"]):
                    with redirect_stdout(out):
                        wt.main()
        self.assertEqual(json.loads(out.getvalue()), {"data": []})
        self.assertIn("https://wakatime.com/api/v1/users/current/projects", captured["url"])


class TestWakatimeHealth(unittest.TestCase):
    def tearDown(self) -> None:
        wt._RUNTIME["debug"] = False

    def test_health_ok_stdout_and_exit(self) -> None:
        def cap(req, timeout=None, **_):
            self.assertIn("/users/current/projects", req.full_url)
            return _FakeUrlopenResp(b"")

        env = {"WAKATIME_API_KEY": "k"}
        out = io.StringIO()
        with patch.dict(os.environ, env, clear=False):
            with patch.object(wt.urllib.request, "urlopen", side_effect=cap):
                with patch.object(sys, "argv", ["wakatime_query.py", "health"]):
                    with redirect_stdout(out):
                        with self.assertRaises(SystemExit) as ctx:
                            wt.main()
        self.assertEqual(ctx.exception.code, 0)
        self.assertEqual(json.loads(out.getvalue()), {"healthy": True})

    def test_health_http_error_prints_false_stdout(self) -> None:
        def cap(req, timeout=None, **_):
            fp = io.BytesIO(b'{"error":"nope"}')
            raise urllib.error.HTTPError(
                req.full_url,
                401,
                "Unauthorized",
                HTTPMessage(),
                fp,
            )

        env = {"WAKATIME_API_KEY": "k"}
        out = io.StringIO()
        with patch.dict(os.environ, env, clear=False):
            with patch.object(wt.urllib.request, "urlopen", side_effect=cap):
                with patch.object(sys, "argv", ["wakatime_query.py", "health"]):
                    with redirect_stdout(out):
                        with self.assertRaises(SystemExit) as ctx:
                            wt.main()
        self.assertEqual(ctx.exception.code, 1)
        self.assertEqual(json.loads(out.getvalue()), {"healthy": False})


class TestWakatimeStatsSummariesUrls(unittest.TestCase):
    def tearDown(self) -> None:
        wt._RUNTIME["debug"] = False

    def test_stats_builds_path_and_query(self) -> None:
        captured: dict[str, str] = {}

        def cap(req, timeout=None, **_):
            captured["url"] = req.full_url
            return _FakeUrlopenResp(b'{"ok":true}')

        env = {"WAKATIME_API_KEY": "k"}
        out = io.StringIO()
        argv = [
            "wakatime_query.py",
            "stats",
            "last_7_days",
            "--timeout",
            "300",
            "--writes-only",
            "true",
        ]
        with patch.dict(os.environ, env, clear=False):
            with patch.object(wt.urllib.request, "urlopen", side_effect=cap):
                with patch.object(sys, "argv", argv):
                    with redirect_stdout(out):
                        wt.main()
        u = captured["url"]
        self.assertIn("https://wakatime.com/api/v1/users/current/stats/last_7_days", u)
        self.assertIn("timeout=300", u)
        self.assertIn("writes_only=true", u)

    def test_stats_percent_encodes_range(self) -> None:
        captured: dict[str, str] = {}

        def cap(req, timeout=None, **_):
            captured["url"] = req.full_url
            return _FakeUrlopenResp(b'{}')

        env = {"WAKATIME_API_KEY": "k"}
        with patch.dict(os.environ, env, clear=False):
            with patch.object(wt.urllib.request, "urlopen", side_effect=cap):
                with patch.object(sys, "argv", ["wakatime_query.py", "stats", "2025-03"]):
                    with redirect_stdout(io.StringIO()):
                        wt.main()
        self.assertIn("stats/2025-03", captured["url"])

    def test_summaries_preset_query(self) -> None:
        captured: dict[str, str] = {}

        def cap(req, timeout=None, **_):
            captured["url"] = req.full_url
            return _FakeUrlopenResp(b'{"data":[]}')

        env = {"WAKATIME_API_KEY": "k"}
        with patch.dict(os.environ, env, clear=False):
            with patch.object(wt.urllib.request, "urlopen", side_effect=cap):
                with patch.object(
                    sys,
                    "argv",
                    ["wakatime_query.py", "summaries", "--range", "last_7_days", "--timezone", "UTC"],
                ):
                    with redirect_stdout(io.StringIO()):
                        wt.main()
        self.assertIn("/users/current/summaries?", captured["url"])
        self.assertIn("range=last_7_days", captured["url"])
        self.assertIn("timezone=UTC", captured["url"])


class TestWakatimeArgparseSummaries(unittest.TestCase):
    def tearDown(self) -> None:
        wt._RUNTIME["debug"] = False

    def test_summaries_start_without_end_errors(self) -> None:
        env = {"WAKATIME_API_KEY": "k"}
        err = io.StringIO()
        with patch.dict(os.environ, env, clear=False):
            with patch.object(sys, "argv", ["wakatime_query.py", "summaries", "--start", "2025-01-01"]):
                with patch.object(sys, "stderr", err):
                    with self.assertRaises(SystemExit) as ctx:
                        wt.main()
        self.assertNotEqual(ctx.exception.code, 0)
        self.assertIn("--end", err.getvalue())


class TestWakatimeAuthHeader(unittest.TestCase):
    def test_basic_header_is_key_base64_only(self) -> None:
        import base64

        with patch.dict(os.environ, {"WAKATIME_API_KEY": "abc"}, clear=False):
            h = wt._request_headers()
        self.assertEqual(h["Authorization"], f"Basic {base64.b64encode(b'abc').decode('ascii')}")
