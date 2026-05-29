import json
import pathlib

import pytest

import pymusicbrainz
from pymusicbrainz import transport

FIXTURES = pathlib.Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures():
    return FIXTURES


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class _FakeSession:
    """A session that returns canned JSON per (path-substring) route.

    ``routes`` maps a substring of the request URL to a fixture filename; the
    first match wins. Lets the offline tests exercise lookup/search/browse with
    no network.
    """

    def __init__(self, routes):
        self.headers = {}
        self.routes = routes
        self.calls = []

    def get(self, url, params=None, **kwargs):
        self.calls.append((url, params))
        for needle, fname in self.routes.items():
            if needle in url:
                payload = json.loads((FIXTURES / fname).read_text())
                return _FakeResponse(payload)
        raise AssertionError(f"no fake route for {url}")


@pytest.fixture
def fake_session():
    """Install a fake transport session; restore real one afterwards."""
    def _install(routes):
        transport.set_delay(0.0)
        session = _FakeSession(routes)
        transport.set_session(session)
        return session

    yield _install
    transport.set_delay(1.1)
    transport.reset_session()
