"""Tests for wakatime-skill/scripts/wakatime_query.py (standalone)."""

from __future__ import annotations

import importlib.util
import io
import json
import os
import sys
import unittest
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
        class _FakeResp:
            def __init__(self, body: bytes) -> None:
                self._body = body

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def read(self):
                return self._body

            def getcode(self):
                return 200

        captured: dict[str, str] = {}

        def cap(req, timeout=None, **_):
            captured["url"] = req.full_url
            return _FakeResp(b'{"data":[]}')

        env = {"WAKATIME_API_KEY": "k"}
        out = io.StringIO()
        with patch.dict(os.environ, env, clear=False):
            with patch.object(wt.urllib.request, "urlopen", side_effect=cap):
                with patch.object(sys, "argv", ["wakatime_query.py", "projects"]):
                    with redirect_stdout(out):
                        wt.main()
        self.assertEqual(json.loads(out.getvalue()), {"data": []})
        self.assertIn("https://wakatime.com/api/v1/users/current/projects", captured["url"])
